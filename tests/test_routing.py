"""The catalog routes correctly as a whole, and the routing scorer behaves as documented."""
import run_routing_evals as rr


def test_catalog_passes_all_routing_gates():
    res = rr.evaluate()
    assert not res["failures"], [f.get("id") for f in res["failures"]]
    assert not res["collisions"], res["collisions"]


def test_every_obvious_positive_routes_to_its_skill_first():
    res = rr.evaluate()
    misses = [r["id"] for r in res["cases"] if r["category"] == "positive-obvious" and r["rank"] != 1]
    assert not misses, misses


def test_negative_clauses_are_not_scored():
    desc = "Reviews diffs. Use when reviewing a PR. Do not use for mapping a codebase (use repo-architect)."
    positive = rr.positive_description(desc)
    assert "repo-architect" not in positive
    assert "reviewing a PR" in positive


def test_stemming_merges_common_inflections():
    assert rr.stem("debugging") == rr.stem("debug")
    assert rr.stem("crashes") == rr.stem("crash")
    assert rr.stem("reviewing") == rr.stem("review")


def test_stopwords_are_dropped():
    assert rr.tokens("what is the cause of this") == ["cause"]


def test_bm25_prefers_the_matching_document():
    bm = rr.BM25({"a": rr.tokens("memory leak crash"), "b": rr.tokens("product roadmap launch")})
    assert bm.rank(rr.tokens("there's a memory leak"))[0][0] == "a"


def test_identical_descriptions_are_flagged_as_collision():
    sims = rr.tfidf_cosine({"x": rr.tokens("review code diff"), "y": rr.tokens("review code diff"),
                            "z": rr.tokens("plan product launch")})
    assert sims[("x", "y")] > 0.99
    assert sims[("x", "z")] < 0.01
