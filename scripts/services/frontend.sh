#!/usr/bin/env bash
# funlogin 示例前端（静态 HTML 测试页）生命周期脚本。
# 不直接调用；由 scripts/setup.sh 统一分发。
set -euo pipefail

SERVICE_NAME="frontend"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONTEND_DIR="${ROOT}/example/frontend"
RUN_DIR="${ROOT}/.run"
PID_FILE="${RUN_DIR}/frontend.pid"
LOG_FILE="${RUN_DIR}/frontend.log"
PORT=3001
readonly SERVICE_NAME ROOT FRONTEND_DIR RUN_DIR PID_FILE LOG_FILE PORT

# shellcheck source=../lib/pid.sh
source "${ROOT}/scripts/lib/pid.sh"

usage() {
  printf 'Usage: %s <start|stop|restart|run|status> dev\n' "${0##*/}" >&2
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 2
}

# 纯静态测试页，没有构建产物，也没有独立的「已安装正式包」形态可言，
# 因此只提供 dev（本机回环地址），不提供 prod：没有可区分于源码的产物，
# 强行保留 prod 只会诱导把源码目录当生产服务对外暴露。
frontend_command() {
  local env="$1"
  command -v python3 >/dev/null 2>&1 || die "缺少 python3，无法启动静态文件服务"
  case "${env}" in
    dev)
      COMMAND=(python3 -m http.server "${PORT}" --bind 127.0.0.1)
      ;;
    *)
      die "env 必须是 dev，得到：${env:-<empty>}"
      ;;
  esac
}

do_start() {
  local env="$1"
  frontend_command "${env}"
  ( cd "${FRONTEND_DIR}" && pid_start "${SERVICE_NAME}(${env})" "${PID_FILE}" "${LOG_FILE}" "${COMMAND[@]}" )
}

do_run() {
  local env="$1"
  frontend_command "${env}"
  cd "${FRONTEND_DIR}"
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
      [[ -n "${env}" ]] || { usage; die "${action} 必须指定 dev"; }
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
