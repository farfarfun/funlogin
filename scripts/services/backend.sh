#!/usr/bin/env bash
# funlogin 示例后端（FastAPI + uvicorn）生命周期脚本。
# 不直接调用；由 scripts/setup.sh 统一分发。
set -euo pipefail

SERVICE_NAME="backend"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_DIR="${ROOT}/.run"
PID_FILE="${RUN_DIR}/backend.pid"
LOG_FILE="${RUN_DIR}/backend.log"
PORT=8001
readonly SERVICE_NAME ROOT RUN_DIR PID_FILE LOG_FILE PORT

# shellcheck source=../lib/pid.sh
source "${ROOT}/scripts/lib/pid.sh"

usage() {
  printf 'Usage: %s <start|stop|restart|run|status> <dev|prod>\n' "${0##*/}" >&2
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 2
}

# 组装启动命令。dev 用 uv 跑源码、开热重载；prod 只允许用已安装的正式包，
# 缺失就报错退出，绝不回退到源码或本地构建产物。
backend_command() {
  local env="$1"
  case "${env}" in
    dev)
      COMMAND=(uv run uvicorn example.app:app --host 127.0.0.1 --port "${PORT}" --reload)
      ;;
    prod)
      command -v uvicorn >/dev/null 2>&1 || die "prod 模式需要已安装的 uvicorn（pip/uv pip install uvicorn），拒绝回退到 uv run"
      python3 -c "import funlogin" >/dev/null 2>&1 || die "prod 模式需要已安装的正式 funlogin 包（pip/uv pip install funlogin），当前环境 import 失败"
      COMMAND=(uvicorn example.app:app --host 0.0.0.0 --port "${PORT}")
      ;;
    *)
      die "env 必须是 dev 或 prod，得到：${env:-<empty>}"
      ;;
  esac
}

do_start() {
  local env="$1"
  backend_command "${env}"
  ( cd "${ROOT}" && pid_start "${SERVICE_NAME}(${env})" "${PID_FILE}" "${LOG_FILE}" "${COMMAND[@]}" )
}

do_run() {
  local env="$1"
  backend_command "${env}"
  cd "${ROOT}"
  exec "${COMMAND[@]}"
}

do_stop() {
  pid_stop "${SERVICE_NAME}" "${PID_FILE}"
}

do_restart() {
  local env="$1"
  do_stop
  do_start "${env}"
}

do_status() {
  pid_status "${SERVICE_NAME}" "${PID_FILE}" "${PORT}"
}

main() {
  local action="${1:-}"
  local env="${2:-}"

  case "${action}" in
    start|stop|restart|run)
      [[ -n "${env}" ]] || { usage; die "${action} 必须指定 dev 或 prod"; }
      "do_${action}" "${env}"
      ;;
    status)
      do_status
      ;;
    *)
      usage
      die "unknown action: ${action:-<empty>}"
      ;;
  esac
}

main "$@"
