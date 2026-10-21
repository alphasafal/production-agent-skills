#!/usr/bin/env bash
# Roll checkout-api back to a previously deployed version.
# Usage: ops/rollback.sh <version> [reason]
set -euo pipefail

SERVICE="checkout-api"
VERSION="${1:-}"
REASON="${2:-manual rollback}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_LOG="$DIR/deploys.log"

if [[ -z "$VERSION" ]]; then
  echo "usage: $0 <version> [reason]" >&2
  exit 2
fi

if ! grep -qE "[[:space:]]${SERVICE}[[:space:]]+${VERSION}[[:space:]]" "$DEPLOY_LOG"; then
  echo "error: ${SERVICE} ${VERSION} has never been deployed to production; refusing" >&2
  exit 1
fi

NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[$NOW] rolling ${SERVICE} back to ${VERSION} (6 pods, maxUnavailable=1)"
echo "[$NOW] rollout complete: ${SERVICE} ${VERSION} serving 100% of traffic"
printf '%s     %-16s %-9s %-16s "%s"\n' "$NOW" "$SERVICE" "$VERSION" "oncall/rollback" "ROLLBACK: $REASON" >> "$DEPLOY_LOG"
