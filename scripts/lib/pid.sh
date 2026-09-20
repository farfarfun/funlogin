#!/usr/bin/env bash
# 共享的 PID 文件生命周期辅助函数，供 scripts/services/*.sh 复用。
# 只处理「脚本自己后台拉起的进程」，不对第三方进程做任何假设。
set -euo pipefail

# 判断某个 PID 文件对应的进程是否还活着。
# 用法：pid_is_alive <pid_file>
pid_is_alive() {
  local pid_file="$1"
  [[ -f "${pid_file}" ]] || return 1
  local pid
  pid="$(cat "${pid_file}" 2>/dev/null || true)"
  [[ -n "${pid}" ]] || return 1
  kill -0 "${pid}" 2>/dev/null
}

# 以后台方式启动命令，写 PID 文件与日志；重复启动直接报错退出。
# 用法：pid_start <name> <pid_file> <log_file> <command...>
pid_start() {
  local name="$1" pid_file="$2" log_file="$3"
  shift 3
  if pid_is_alive "${pid_file}"; then
    echo "error: ${name} 已在运行（PID $(cat "${pid_file}")），先 stop 再 start" >&2
    exit 1
  fi
  rm -f "${pid_file}"
  mkdir -p "$(dirname "${pid_file}")" "$(dirname "${log_file}")"
  nohup "$@" </dev/null >>"${log_file}" 2>&1 &
  local pid=$!
  echo "${pid}" >"${pid_file}"
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
  if ! pid_is_alive "${pid_file}"; then
    rm -f "${pid_file}"
    echo "${name} 未在运行（无有效 PID 文件）"
    return 0
  fi
  local pid
  pid="$(cat "${pid_file}")"
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
  if pid_is_alive "${pid_file}"; then
    echo "${name}: running (PID $(cat "${pid_file}"), port ${port})"
  else
    echo "${name}: stopped"
  fi
}
