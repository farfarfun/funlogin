#!/usr/bin/env bash
# funlogin 示例服务统一入口：负责参数解析与分发，具体启停逻辑在
# scripts/services/<service>.sh 里。funlogin 本身是被其他项目挂载的库，
# 这里管理的是 example/ 下用于本地联调的演示后端 + 静态前端。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="${ROOT}/scripts/services"
readonly ROOT SERVICE_DIR

readonly -a ACTIONS=(start stop restart run status)
readonly -a SERVICES=(backend frontend)

usage() {
  cat >&2 <<'EOF'
Usage: scripts/setup.sh <action> <service> [env]

  action  start|stop|restart|run|status
  service backend|frontend
  env     dev|prod（start/stop/restart/run 必须指定；status 不需要）

示例：
  scripts/setup.sh start backend dev     # 后台启动后端（热重载）
  scripts/setup.sh run frontend dev      # 前台启动前端静态服务
  scripts/setup.sh stop backend dev
  scripts/setup.sh status                # 汇报两个服务在所有环境下的状态
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 2
}

contains() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
    [[ "${item}" == "${needle}" ]] && return 0
  done
  return 1
}

service_script_for() {
  case "$1" in
    backend) printf '%s\n' "${SERVICE_DIR}/backend.sh" ;;
    frontend) printf '%s\n' "${SERVICE_DIR}/frontend.sh" ;;
    *) return 1 ;;
  esac
}

# status 是唯一允许不指定 service/env 的动作：非交互汇报所有已配置服务。
status_all() {
  local service script
  for service in "${SERVICES[@]}"; do
    script="$(service_script_for "${service}")"
    bash "${script}" status
  done
}

dispatch() {
  local action="$1" service="$2" env="${3:-}"
  local script
  script="$(service_script_for "${service}")" || die "unknown service: ${service}"
  [[ -f "${script}" ]] || die "missing service script: ${script}"
  if [[ "${action}" == "status" ]]; then
    bash "${script}" status
  else
    [[ -n "${env}" ]] || die "${action} 必须指定 dev 或 prod"
    bash "${script}" "${action}" "${env}"
  fi
}

main() {
  local action="${1:-}"

  [[ -n "${action}" ]] || { usage; die "缺少 action"; }
  contains "${action}" "${ACTIONS[@]}" || { usage; die "unknown action: ${action}"; }

  if [[ "${action}" == "status" && $# -le 1 ]]; then
    status_all
    return 0
  fi

  (( $# <= 3 )) || { usage; die "too many arguments"; }

  local service="${2:-}"
  [[ -n "${service}" ]] || { usage; die "缺少 service"; }
  contains "${service}" "${SERVICES[@]}" || { usage; die "unknown service: ${service}"; }

  dispatch "${action}" "${service}" "${3:-}"
}

main "$@"
