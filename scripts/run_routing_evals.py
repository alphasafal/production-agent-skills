#!/usr/bin/env python3
"""Deterministic, model-free ROUTING evaluation across the whole skill catalog.

An agent only ever sees each skill's name + description when deciding what to
activate, so a skill is only as good as its description is *distinct*. This
script approximates that decision: it ranks every skill against every
activation prompt with BM25 over the (lightly stemmed) name + description,
and checks that the catalog routes correctly as a whole — not just that a
prompt shares a word with its own skill.

Gates (non-zero exit if any fail):
  - positive-obvious:   the case's skill ranks #1 of all skills
  - positive-ambiguous: the case's skill ranks in the top --ambiguous-top-k (default 3)
  - negative + route_to: the skill named in `route_to` outranks the case's skill
  - collisions:         no two descriptions exceed --max-similarity (TF-IDF cosine)
  - held-out prompts:   >= --min-holdout-top3 (default 90%) rank their skill top-3.
                        evaluations/routing/holdout.json is never used to tune
                        descriptions, so it's the honest generalization number.

Reported, not gated:
  - negatives without route_to (e.g. "What is Kafka?"). Lexical scoring can't tell
    "explain X" from "do X" — that judgement needs a model; see
    scripts/run_behavioral_evals.py.

This is a lexical proxy for routing, not a measurement of real activation.
A failure here usually means: fix the description, not the eval case.

Usage:
    python scripts/run_routing_evals.py
    python scripts/run_routing_evals.py --verbose          # show every case's ranking
    python scripts/run_routing_evals.py --json out.json    # machine-readable results
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import EVALUATIONS_DIR, discover_skills  # noqa: E402

WORD_RE = re.compile(r"[a-z0-9]+")

STOPWORDS = set("""
a an and are as at be been but by can could do does doing done for from has have
how i if in into is it its just me my not of on or our out so some than that the
their them then there these they this those to up us use used using was we were
what when where which while who why will with would you your yes no any all also
only very more most other such same own too s t don should now get got want need
""".split())

# Ordered longest-first so e.g. "ing" doesn't preempt "ying".
SUFFIXES = ("ization", "ations", "ation", "ments", "ment", "ness", "ities", "ity",
            "ings", "ing", "ies", "ied", "ers", "er", "ed", "es", "ly", "s")


def stem(word: str) -> str:
    for suf in SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            word = word[: -len(suf)]
            if suf in ("ies", "ied", "ities", "ity"):
                word += "y" if suf in ("ies", "ied") else ""
            break
    if len(word) > 4 and word[-1] == word[-2] and word[-1] not in "aeiouls":
        word = word[:-1]  # "debugg" -> "debug", "committ" -> "commit"
    return word


def tokens(text: str) -> list[str]:
    return [stem(w) for w in WORD_RE.findall(text.lower()) if w not in STOPWORDS and len(w) > 1]


class BM25:
    def __init__(self, docs: dict[str, list[str]], k1: float = 1.2, b: float = 0.75):
        self.docs = docs
        self.k1, self.b = k1, b
        self.avgdl = sum(len(d) for d in docs.values()) / len(docs)
        df = Counter(t for d in docs.values() for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.tf = {name: Counter(d) for name, d in docs.items()}

    def score(self, query: list[str], name: str) -> float:
        tf, dl = self.tf[name], len(self.docs[name])
        s = 0.0
        for t in set(query):
            if t not in tf:
                continue
            f = tf[t]
            s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return s

    def rank(self, query: list[str]) -> list[tuple[str, float]]:
        return sorted(((n, self.score(query, n)) for n in self.docs), key=lambda x: (-x[1], x[0]))


def tfidf_cosine(docs: dict[str, list[str]]) -> dict[tuple[str, str], float]:
    n = len(docs)
    df = Counter(t for d in docs.values() for t in set(d))
    idf = {t: math.log(n / c) + 1 for t, c in df.items()}
    vecs = {}
    for name, d in docs.items():
        tf = Counter(d)
        v = {t: c * idf[t] for t, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs[name] = {t: x / norm for t, x in v.items()}
    names = sorted(docs)
    out = {}
    for i, a in enumerate(names):
        for b_ in names[i + 1:]:
            va, vb = vecs[a], vecs[b_]
            out[(a, b_)] = sum(x * vb.get(t, 0.0) for t, x in va.items())
    return out


NEGATIVE_CLAUSE_RE = re.compile(r"\b(?:do not|don't|never) use\b", re.IGNORECASE)


def positive_description(description: str) -> str:
    """The description up to its first 'Do not use ...' clause.

    Those clauses are good guidance for a real model, which understands negation,
    but a bag-of-words scorer would read "do not use for reviewing an entire
    codebase (use repo-architect)" as evidence *for* this skill. Scoring only the
    positive part keeps the proxy from rewarding the removal of useful guidance.
    """
    match = NEGATIVE_CLAUSE_RE.search(description)
    return description[: match.start()] if match else description


def skill_document(skill) -> list[str]:
    # The name is the strongest routing signal an agent has; weight it like a title.
    return tokens(skill.name.replace("-", " ")) * 2 + tokens(positive_description(skill.description))


def evaluate(ambiguous_top_k: int = 3, max_similarity: float = 0.45) -> dict:
    skills = discover_skills()
    docs = {s.name: skill_document(s) for s in skills}
    bm25 = BM25(docs)

    results = {"cases": [], "collisions": [], "failures": []}
    for skill in skills:
        eval_file = EVALUATIONS_DIR / "activation" / f"{skill.dir.name}.json"
        if not eval_file.is_file():
            continue
        for case in json.loads(eval_file.read_text()):
            ranking = bm25.rank(tokens(case["prompt"]))
            order = [n for n, _ in ranking]
            scores = dict(ranking)

            def rank_of(name: str) -> int:
                # Ties count against the skill (no alphabetical luck), and a skill
                # with zero score didn't match at all, so it ranks last.
                if scores[name] == 0:
                    return len(order)
                return 1 + sum(1 for n, sc in ranking if n != name and sc >= scores[name])

            rank = rank_of(case["skill"])
            cat = case["category"]
            row = {"id": case["id"], "skill": case["skill"], "category": cat,
                   "rank": rank, "top3": ranking[:3], "gated": True, "passed": True}

            if cat == "positive-obvious":
                row["passed"] = rank == 1
                row["rule"] = "ranks #1"
            elif cat == "positive-ambiguous":
                row["passed"] = rank <= ambiguous_top_k
                row["rule"] = f"ranks top-{ambiguous_top_k}"
            elif case.get("route_to"):
                other_rank = rank_of(case["route_to"])
                row["passed"] = scores[case["route_to"]] > scores[case["skill"]]
                row["rule"] = f"{case['route_to']} outranks it (got #{other_rank} vs #{rank})"
            else:
                row["gated"] = False
                row["passed"] = rank != 1
                row["rule"] = "not #1 (report only)"

            results["cases"].append(row)
            if row["gated"] and not row["passed"]:
                results["failures"].append(row)

    for (a, b_), sim in sorted(tfidf_cosine(docs).items(), key=lambda x: -x[1]):
        if sim > max_similarity:
            results["collisions"].append({"a": a, "b": b_, "similarity": round(sim, 3)})

    def rate(cat, pred):
        rows = [r for r in results["cases"] if r["category"] == cat and pred(r)]
        return len([r for r in rows if r["rank"] == 1]), len(rows)

    holdout_file = EVALUATIONS_DIR / "routing" / "holdout.json"
    holdout = json.loads(holdout_file.read_text())["cases"] if holdout_file.is_file() else []
    results["holdout"] = []
    for case in holdout:
        ranking = bm25.rank(tokens(case["prompt"]))
        order = [n for n, _ in ranking]
        results["holdout"].append({"skill": case["skill"], "prompt": case["prompt"],
                                   "rank": order.index(case["skill"]) + 1, "top": order[0]})

    results["summary"] = {
        "obvious_rank1": rate("positive-obvious", lambda r: True),
        "ambiguous_rank1": rate("positive-ambiguous", lambda r: True),
        "ambiguous_topk": (
            len([r for r in results["cases"] if r["category"] == "positive-ambiguous" and r["passed"]]),
            len([r for r in results["cases"] if r["category"] == "positive-ambiguous"]),
        ),
        "cross_route": (
            len([r for r in results["cases"] if r["category"] == "negative" and r["gated"] and r["passed"]]),
            len([r for r in results["cases"] if r["category"] == "negative" and r["gated"]]),
        ),
        "negatives_report_only_not_rank1": (
            len([r for r in results["cases"] if r["category"] == "negative" and not r["gated"] and r["passed"]]),
            len([r for r in results["cases"] if r["category"] == "negative" and not r["gated"]]),
        ),
        "holdout_rank1": (len([h for h in results["holdout"] if h["rank"] == 1]), len(results["holdout"])),
        "holdout_top3": (len([h for h in results["holdout"] if h["rank"] <= 3]), len(results["holdout"])),
        "max_pair_similarity": round(max(tfidf_cosine(docs).values()), 3),
    }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ambiguous-top-k", type=int, default=3)
    parser.add_argument("--max-similarity", type=float, default=0.45,
                        help="fail if any two skill descriptions exceed this TF-IDF cosine")
    parser.add_argument("--min-holdout-top3", type=float, default=0.9,
                        help="fail if fewer than this fraction of held-out prompts rank their skill top-3")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--json", metavar="PATH", help="write full results as JSON")
    args = parser.parse_args()

    res = evaluate(args.ambiguous_top_k, args.max_similarity)

    for row in res["cases"]:
        mark = "✓" if row["passed"] else ("✗" if row["gated"] else "~")
        if args.verbose or (row["gated"] and not row["passed"]) or (not row["gated"] and not row["passed"]):
            top = ", ".join(f"{n} {s:.2f}" for n, s in row["top3"])
            print(f"  {mark} {row['id']:<44} #{row['rank']}  rule: {row['rule']:<48} top: {top}")

    s = res["summary"]
    pct = lambda a, b: f"{a}/{b} ({100 * a / b:.0f}%)" if b else "n/a"  # noqa: E731
    print()
    print(f"Obvious positives ranked #1:       {pct(*s['obvious_rank1'])}")
    print(f"Ambiguous positives in top-{args.ambiguous_top_k}:     {pct(*s['ambiguous_topk'])}"
          f"   (ranked #1: {pct(*s['ambiguous_rank1'])})")
    print(f"Cross-route negatives correct:     {pct(*s['cross_route'])}")
    print(f"Other negatives not ranked #1:     {pct(*s['negatives_report_only_not_rank1'])}  (report only)")
    print(f"Max description similarity:        {s['max_pair_similarity']} (limit {args.max_similarity})")
    if res["holdout"]:
        print(f"Held-out prompts ranked #1:        {pct(*s['holdout_rank1'])}   (top-3: {pct(*s['holdout_top3'])})")
        if args.verbose:
            for h in res["holdout"]:
                print(f"    {'✓' if h['rank'] == 1 else '·'} #{h['rank']} {h['skill']:<24} {h['prompt']}")
        a, b = s["holdout_top3"]
        if b and a / b < args.min_holdout_top3:
            print(f"  ✗ held-out top-3 rate below floor {args.min_holdout_top3:.0%}")
            res["failures"].append({"id": "holdout-top3-floor"})
    for c in res["collisions"]:
        print(f"  ✗ description collision: {c['a']} ↔ {c['b']} = {c['similarity']}")

    if args.json:
        Path(args.json).write_text(json.dumps(res, indent=2))

    failed = len(res["failures"]) + len(res["collisions"])
    print(f"\n{'FAIL' if failed else 'PASS'}: {failed} gated failure(s).")
    print("Note: lexical routing proxy — necessary, not sufficient. Behavioral evals measure the real thing.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
