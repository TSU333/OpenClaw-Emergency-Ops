#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

BASE_URL="${BASE_URL:-http://localhost:8000/api/v1}"
WORKER_LOG_LINES="${WORKER_LOG_LINES:-80}"
SNOOZE_MINUTES="${SNOOZE_MINUTES:-1}"

print_section() {
  printf '\n========== %s ==========\n' "$1"
}

pretty_json() {
  python3 -m json.tool
}

json_field() {
  local field_path="$1"
  python3 -c '
import json
import sys

path = sys.argv[1].split(".")
data = json.load(sys.stdin)
value = data
for part in path:
    value = value[part]
if isinstance(value, (dict, list)):
    print(json.dumps(value))
else:
    print(value)
' "$field_path"
}

post_json() {
  local method="$1"
  local url="$2"
  local payload="${3:-}"

  if [[ -n "$payload" ]]; then
    curl -sfS -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -d "$payload"
  else
    curl -sfS -X "$method" "$url"
  fi
}

EVENT_PAYLOAD='{
  "source": "quant-engine",
  "event_type": "max_drawdown_breach",
  "title": "Demo: Max drawdown exceeded threshold",
  "message": "Strategy BTC_PERP_01 breached max drawdown limit during demo flow",
  "severity_hint": "p0",
  "metadata": {
    "strategy_id": "BTC_PERP_01",
    "exchange": "Binance",
    "drawdown_pct": 12.4,
    "pnl": -2480.10
  },
  "suggested_actions": ["pause_strategy", "close_positions"]
}'

print_section "Create Event"
CREATE_RESPONSE="$(post_json POST "${BASE_URL}/events" "${EVENT_PAYLOAD}")"
printf '%s\n' "${CREATE_RESPONSE}" | pretty_json
EVENT_ID="$(printf '%s' "${CREATE_RESPONSE}" | json_field "id")"
printf 'EVENT_ID=%s\n' "${EVENT_ID}"

print_section "Acknowledge"
ACK_RESPONSE="$(post_json POST "${BASE_URL}/events/${EVENT_ID}/acknowledge" '{
  "actor": "demo-operator",
  "note": "Immediate acknowledgement from demo flow"
}')"
printf '%s\n' "${ACK_RESPONSE}" | pretty_json

print_section "Snooze"
SNOOZE_RESPONSE="$(post_json POST "${BASE_URL}/events/${EVENT_ID}/snooze" "{
  \"actor\": \"demo-operator\",
  \"note\": \"Short snooze from demo flow\",
  \"minutes\": ${SNOOZE_MINUTES}
}")"
printf '%s\n' "${SNOOZE_RESPONSE}" | pretty_json

print_section "Execute pause_strategy"
ACTION_RESPONSE="$(post_json POST "${BASE_URL}/events/${EVENT_ID}/actions/pause_strategy" '{
  "actor": "demo-operator",
  "parameters": {
    "reason": "demo flow action execution"
  }
}')"
printf '%s\n' "${ACTION_RESPONSE}" | pretty_json

print_section "Event Detail"
DETAIL_RESPONSE="$(curl -sfS "${BASE_URL}/events/${EVENT_ID}")"
printf '%s\n' "${DETAIL_RESPONSE}" | pretty_json

print_section "Timeline"
TIMELINE_RESPONSE="$(curl -sfS "${BASE_URL}/events/${EVENT_ID}/timeline")"
printf '%s\n' "${TIMELINE_RESPONSE}" | pretty_json

print_section "Worker Logs"
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  (
    cd "${PROJECT_ROOT}"
    docker compose logs worker --tail "${WORKER_LOG_LINES}" || true
  )
else
  printf 'docker compose is unavailable; skip worker log printing.\n'
fi

print_section "Summary"
printf 'AI summary:\n%s\n' "$(printf '%s' "${DETAIL_RESPONSE}" | json_field 'ai_summary.operator_brief')"
printf 'Action runs count: %s\n' "$(printf '%s' "${DETAIL_RESPONSE}" | json_field 'action_runs' | python3 -c 'import json,sys; print(len(json.loads(sys.stdin.read())))')"
printf 'Timeline entries: %s\n' "$(printf '%s' "${TIMELINE_RESPONSE}" | json_field 'timeline' | python3 -c 'import json,sys; print(len(json.loads(sys.stdin.read())))')"
