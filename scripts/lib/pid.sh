#!/usr/bin/env bash
# 共享的 PID 文件生命周期辅助函数，供 scripts/services/*.sh 复用。
# 只处理「脚本自己后台拉起的进程」，不对第三方进程做任何假设。
set -euo pipefail

# 读取 Linux 进程的启动时间标识。PID 被复用后该值会变化。
pid_start_marker() {
  local pid="$1"
  [[ -r "/proc/${pid}/stat" ]] || return 1
  awk '{print $22}' "/proc/${pid}/stat"
}

# 返回进程命令及参数的校验摘要，用于识别同一 PID 的其他进程。
pid_command_marker() {
  local pid="$1"
  [[ -r "/proc/${pid}/cmdline" ]] || return 1
  tr '\0' ' ' <"/proc/${pid}/cmdline" | cksum | awk '{print $1 ":" $2}'
}

# 返回 PID 文件的归属状态：owned、stale、mismatch、unverified 或 missing。
# 旧版只有 PID 的文件无法可靠确认归属，绝不将其视为本服务。
pid_file_state() {
  local pid_file="$1" pid start_marker command_marker current_start current_command
  [[ -f "${pid_file}" ]] || { printf 'missing\n'; return 0; }
  read -r pid start_marker command_marker <"${pid_file}" || { printf 'unverified\n'; return 0; }
  [[ "${pid}" =~ ^[0-9]+$ && -n "${start_marker:-}" && -n "${command_marker:-}" ]] || { printf 'unverified\n'; return 0; }
  kill -0 "${pid}" 2>/dev/null || { printf 'stale\n'; return 0; }
  current_start="$(pid_start_marker "${pid}" 2>/dev/null || true)"
  current_command="$(pid_command_marker "${pid}" 2>/dev/null || true)"
  [[ -n "${current_start}" && -n "${current_command}" ]] || { printf 'unverified\n'; return 0; }
  [[ "${start_marker}" == "${current_start}" && "${command_marker}" == "${current_command}" ]] && printf 'owned\n' || printf 'mismatch\n'
}

# 判断某个 PID 文件是否仍对应脚本启动的同一进程。
# 用法：pid_is_alive <pid_file>
pid_is_alive() {
  local pid_file="$1"
  [[ "$(pid_file_state "${pid_file}")" == "owned" ]]
}

# 以后台方式启动命令，写 PID 文件与日志；重复启动直接报错退出。
# 用法：pid_start <name> <pid_file> <log_file> <command...>
pid_start() {
  local name="$1" pid_file="$2" log_file="$3"
  shift 3
  local state pid start_marker command_marker
  state="$(pid_file_state "${pid_file}")"
  if [[ "${state}" == "owned" ]]; then
    read -r pid start_marker command_marker <"${pid_file}"
    echo "error: ${name} 已在运行（PID ${pid}），先 stop 再 start" >&2
    exit 1
  fi
  if [[ "${state}" != "missing" && "${state}" != "stale" ]]; then
    echo "error: ${name} 的 PID 文件无法确认进程归属（${state}），拒绝覆盖或启动" >&2
    exit 1
  fi
  rm -f "${pid_file}"
  mkdir -p "$(dirname "${pid_file}")" "$(dirname "${log_file}")"
  nohup "$@" </dev/null >>"${log_file}" 2>&1 &
  local pid=$!
  start_marker="$(pid_start_marker "${pid}" 2>/dev/null || true)"
  command_marker="$(pid_command_marker "${pid}" 2>/dev/null || true)"
  if [[ -z "${start_marker}" || -z "${command_marker}" ]]; then
    echo "error: 无法读取 ${name} 的进程启动或命令标识，拒绝写入 PID 文件" >&2
    kill "${pid}" 2>/dev/null || true
    exit 1
  fi
  printf '%s %s %s\n' "${pid}" "${start_marker}" "${command_marker}" >"${pid_file}"
  sleep 1
  if ! kill -0 "${pid}" 2>/dev/null; then
    rm -f "${pid_file}"
    echo "error: ${name} 启动后立即退出，查看日志：${log_file}" >&2
    exit 1
  fi
  echo "${name} 已启动：PID ${pid}，日志 ${log_file}"
}

# 停止 PID 文件对应的进程；区分「陈旧 PID 文件」与「进程确实存活」。
# 用法：pid_stop <name> <pid_file>
pid_stop() {
  local name="$1" pid_file="$2"
  local state pid start_marker command_marker
  state="$(pid_file_state "${pid_file}")"
  if [[ "${state}" == "missing" || "${state}" == "stale" ]]; then
    rm -f "${pid_file}"
    echo "${name} 未在运行（无有效 PID 文件）"
    return 0
  fi
  if [[ "${state}" != "owned" ]]; then
    echo "error: ${name} 的 PID 文件无法确认进程归属（${state}），拒绝停止" >&2
    return 1
  fi
  read -r pid start_marker command_marker <"${pid_file}"
  kill "${pid}" 2>/dev/null || true
  for _ in $(seq 1 20); do
    kill -0 "${pid}" 2>/dev/null || break
    sleep 0.2
  done
  if kill -0 "${pid}" 2>/dev/null; then
    kill -9 "${pid}" 2>/dev/null || true
  fi
  rm -f "${pid_file}"
  echo "${name} 已停止（PID ${pid}）"
}

# 非交互汇报状态。
# 用法：pid_status <name> <pid_file> <port>
pid_status() {
  local name="$1" pid_file="$2" port="$3"
  local state pid start_marker command_marker
  state="$(pid_file_state "${pid_file}")"
  case "${state}" in
    owned)
      read -r pid start_marker command_marker <"${pid_file}"
      echo "${name}: running (PID ${pid}, port ${port})"
      ;;
    missing|stale) echo "${name}: stopped" ;;
    *) echo "${name}: unknown (PID 文件无法确认进程归属：${state})" ;;
  esac
}
