#!/bin/sh
# Production Agent Skills installer.
#
# One line, no clone, no Node, no Python:
#
#   curl -fsSL https://raw.githubusercontent.com/alphasafal/production-agent-skills/main/install.sh | sh -s -- --pack sre
#
# It downloads this repository, copies the skills you asked for into the
# directory your agent reads, and stops. Nothing else is written, no network
# calls are made after the download, and nothing runs with elevated rights.
# Read it before you pipe it; it is short on purpose.
#
# Needs: sh, tar, and curl or wget.

set -eu

REPO="alphasafal/production-agent-skills"
REF="${PAS_REF:-main}"

usage() {
  cat <<'EOF'
Usage: install.sh [what] [where] [options]

What (at least one, all repeatable):
  --pack NAME     a role pack: backend-engineer, frontend-engineer, tech-lead,
                  sre, security, data-scientist, product-manager
  --skill NAME    a single skill
  --all           every skill

Where (default: detected, see below):
  --agent NAME    claude | codex | copilot | cursor | gemini | universal
                  (repeatable, to install for more than one agent)
  --global        install for every project of this user, not only this one
  --target DIR    any other skills directory; overrides --agent and --global

Options:
  --list          show the packs and skills, then exit
  --uninstall     remove the selected skills instead of installing them
  --force         replace a skill that is already installed (this is how you update)
  --dry-run       print what would happen and change nothing
  --ref REF       branch or tag to install from (default: main)
  -h, --help      this text

Where skills go:
  claude                              .claude/skills   (--global: ~/.claude/skills)
  codex, copilot, cursor, gemini,
  universal                           .agents/skills   (--global: ~/.agents/skills)
  no --agent given                    .claude/skills if this project (or, with
                                      --global, your home) has a .claude folder,
                                      otherwise .agents/skills

Examples:
  install.sh --pack backend-engineer
  install.sh --skill debugging-investigator --agent cursor
  install.sh --all --agent claude --global
  install.sh --pack sre --force            # update
  install.sh --pack sre --uninstall
EOF
}

say() { printf '%s\n' "$*"; }
die() { printf 'install.sh: %s\n' "$*" >&2; exit 1; }

PACKS=""
SKILLS=""
AGENTS=""
ALL=0
GLOBAL=0
TARGET=""
LIST=0
UNINSTALL=0
FORCE=0
DRY_RUN=0

need_value() { [ "$#" -ge 2 ] || die "$1 needs a value (see --help)"; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pack)      need_value "$@"; PACKS="$PACKS $2"; shift 2 ;;
    --skill)     need_value "$@"; SKILLS="$SKILLS $2"; shift 2 ;;
    --agent)     need_value "$@"; AGENTS="$AGENTS $2"; shift 2 ;;
    --target)    need_value "$@"; TARGET="$2"; shift 2 ;;
    --ref)       need_value "$@"; REF="$2"; shift 2 ;;
    --all)       ALL=1; shift ;;
    --global)    GLOBAL=1; shift ;;
    --list)      LIST=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --force)     FORCE=1; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    -h|--help)   usage; exit 0 ;;
    *)           die "unknown option '$1' (see --help)" ;;
  esac
done

case "$REF" in
  ""|*[!A-Za-z0-9._/-]*) die "--ref may only contain letters, digits and . _ / -" ;;
esac

if [ "$LIST" -eq 0 ] && [ "$ALL" -eq 0 ] && [ -z "$PACKS" ] && [ -z "$SKILLS" ]; then
  usage
  say ""
  die "nothing selected: pass --pack NAME, --skill NAME or --all (or --list to see them)"
fi

# --- where the skills come from -------------------------------------------

TMP=""
cleanup() { [ -z "$TMP" ] || rm -rf "$TMP"; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

SRC=""
if [ -n "${PAS_SOURCE_DIR:-}" ]; then
  # A local checkout to install from instead of downloading (offline use, tests).
  SRC="$PAS_SOURCE_DIR"
else
  case "$0" in
    install.sh|*/install.sh)
      here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
      [ -f "$here/install-index.tsv" ] && [ -d "$here/skills" ] && SRC="$here"
      ;;
  esac
fi

if [ -z "$SRC" ]; then
  command -v tar >/dev/null 2>&1 || die "tar is required"
  TMP=$(mktemp -d 2>/dev/null || mktemp -d -t pas)
  url="https://codeload.github.com/$REPO/tar.gz/$REF"
  say "Downloading $REPO@$REF ..."
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$TMP/src.tar.gz" || die "download failed: $url"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$url" -O "$TMP/src.tar.gz" || die "download failed: $url"
  else
    die "curl or wget is required"
  fi
  mkdir "$TMP/src"
  tar -xzf "$TMP/src.tar.gz" -C "$TMP/src" || die "could not unpack the download"
  for d in "$TMP"/src/*/; do SRC="${d%/}"; break; done
fi

INDEX="$SRC/install-index.tsv"
[ -d "$SRC/skills" ] || die "no skills/ directory in $SRC"
[ -f "$INDEX" ] || die "'$REF' has no install-index.tsv: this installer needs v0.4.0 or later"

TAB=$(printf '\t')
index_rows() { grep "^$1$TAB" "$INDEX" || true; }
all_skills() { index_rows skill | cut -f2; }
pack_skills() { index_rows pack | awk -F '\t' -v p="$1" '$2 == p { print $4 }'; }
skill_field() { index_rows skill | awk -F '\t' -v s="$1" -v n="$2" '$2 == s { print $n }'; }

if [ "$LIST" -eq 1 ]; then
  say "Role packs (--pack NAME):"
  index_rows pack | awk -F '\t' '{ printf "  %-18s %s\n                     %s\n", $2, $3, $4 }'
  say ""
  say "Skills (--skill NAME):"
  index_rows skill | awk -F '\t' '{ printf "  %-26s %s\n", $2, $3 }'
  exit 0
fi

# --- which skills ---------------------------------------------------------

SELECTED=""
add_skill() {
  case " $SELECTED " in
    *" $1 "*) ;;
    *) SELECTED="$SELECTED $1" ;;
  esac
}

if [ "$ALL" -eq 1 ]; then
  for s in $(all_skills); do add_skill "$s"; done
fi
for p in $PACKS; do
  members=$(pack_skills "$p")
  [ -n "$members" ] || die "unknown pack '$p' (run with --list to see the packs)"
  for s in $members; do add_skill "$s"; done
done
for s in $SKILLS; do
  [ -n "$(skill_field "$s" 2)" ] || die "unknown skill '$s' (run with --list to see the skills)"
  add_skill "$s"
done

# --- which directories ----------------------------------------------------

for a in $AGENTS; do
  case "$a" in
    claude|codex|copilot|cursor|gemini|universal) ;;
    *) die "unknown agent '$a': use claude, codex, copilot, cursor, gemini or universal, or pass --target DIR" ;;
  esac
done

agent_dir() {
  case "$1" in
    claude) sub=".claude/skills" ;;
    *) sub=".agents/skills" ;;
  esac
  if [ "$GLOBAL" -eq 1 ]; then
    printf '%s\n' "$HOME/$sub"
  else
    printf '%s\n' "./$sub"
  fi
}

TARGETS=""
add_target() {
  case "
$TARGETS
" in
    *"
$1
"*) ;;
    *) TARGETS="${TARGETS:+$TARGETS
}$1" ;;
  esac
}

if [ -n "$TARGET" ]; then
  add_target "$TARGET"
elif [ -n "$AGENTS" ]; then
  for a in $AGENTS; do add_target "$(agent_dir "$a")"; done
else
  base="."
  [ "$GLOBAL" -eq 0 ] || base="$HOME"
  if [ -d "$base/.claude" ]; then
    say "Found $base/.claude, installing for Claude Code (override with --agent or --target)."
    add_target "$(agent_dir claude)"
  else
    say "Installing to the shared .agents/skills directory, read by Codex, Copilot, Cursor and Gemini CLI."
    say "Using Claude Code? Add --agent claude."
    add_target "$(agent_dir universal)"
  fi
fi

# --- do it ----------------------------------------------------------------

DONE=0
SKIPPED=0
note="" ; [ "$DRY_RUN" -eq 0 ] || note="(dry run) "

install_skill() {
  src="$SRC/skills/$2"
  dest="$1/$2"
  [ -f "$src/SKILL.md" ] || die "$2 is in the index but skills/$2/SKILL.md is missing"
  if [ -e "$dest" ]; then
    if [ "$FORCE" -eq 0 ]; then
      say "  skip     $2 (already in $1; use --force to replace it)"
      SKIPPED=$((SKIPPED + 1))
      return 0
    fi
    [ "$DRY_RUN" -eq 1 ] || rm -rf "$dest"
  fi
  if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$1"
    cp -R "$src" "$dest"
    find "$dest" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
  fi
  say "  ${note}install  $2"
  DONE=$((DONE + 1))
}

uninstall_skill() {
  dest="$1/$2"
  if [ ! -e "$dest" ]; then
    say "  skip     $2 (not in $1)"
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi
  # Only ever delete a directory that is recognisably a skill.
  [ -f "$dest/SKILL.md" ] || die "$dest has no SKILL.md, refusing to delete it"
  [ "$DRY_RUN" -eq 1 ] || rm -rf "$dest"
  say "  ${note}remove   $2"
  DONE=$((DONE + 1))
}

OLDIFS=$IFS
IFS='
'
for t in $TARGETS; do
  IFS=$OLDIFS
  say ""
  say "$t"
  if [ -e "$t" ] && [ ! -d "$t" ]; then die "$t exists and is not a directory"; fi
  for s in $SELECTED; do
    if [ "$UNINSTALL" -eq 1 ]; then uninstall_skill "$t" "$s"; else install_skill "$t" "$s"; fi
  done
done
IFS=$OLDIFS

say ""
if [ "$UNINSTALL" -eq 1 ]; then
  say "${note}Removed $DONE, skipped $SKIPPED."
  exit 0
fi
say "${note}Installed $DONE, skipped $SKIPPED."
if [ "$DONE" -eq 0 ] || [ "$DRY_RUN" -eq 1 ]; then exit 0; fi

first=""
for s in $SELECTED; do first="$s"; break; done
say ""
say "Next: restart your agent so it picks the skills up, then just describe the task."
say "To try $first, say:"
say "  \"$(skill_field "$first" 4)\""
case "$TARGETS" in
  *.claude/skills*) say "In Claude Code you can also run it directly: /$first" ;;
esac
say "More prompts: https://github.com/$REPO/blob/main/docs/prompt-cheatsheet.md"
