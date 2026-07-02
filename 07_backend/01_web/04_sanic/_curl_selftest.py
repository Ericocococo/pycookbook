"""
_curl_selftest.py —— 配方自测工具(不是配方本身,下划线前缀 + 无序号)
================================================================================
所属: 05_frameworks/02_web 各框架共用 | Python 3.12

作用:让每个「Web 服务」配方能一条命令 `python xx.py` 自测跑通,
     并且是用**真实的 curl 命令**去打真实起起来的 HTTP 服务。

原理(双模式):
  1) 配方文件的 __main__ 里,无参运行 → 调用本模块 run_selftest():
       ① 用子进程拉起「python 配方文件 serve」→ 真实监听端口
       ② 轮询等端口就绪
       ③ 逐条执行真实 curl(subprocess 调系统 curl),打印命令与响应
       ④ 结束时终止子进程
  2) 配方文件带 "serve" 参数运行 → 阻塞启动服务,供你另开终端手动 curl。

case 字段说明(配方文件里的 CURL_CASES 每一项):
  desc         —— 该用例说明(必填)
  path         —— 请求路径,含查询串,如 "/user/1?q=hi"(必填)
  method       —— HTTP 方法,默认 "GET"
  json         —— 要发送的 JSON 请求体(dict/list),自动加 Content-Type
  headers      —— 额外请求头 dict
  show_headers —— True 则给 curl 加 -i,把响应头一起打印(演示响应头时用)

curl = 命令行 HTTP 客户端(client URL),Windows 10+ / git-bash 均自带。
================================================================================
"""
import json as _json
import shutil
import socket
import subprocess
import sys
import time

# Windows 控制台默认 GBK,统一切到 UTF-8 避免中文输出乱码(失败也不影响逻辑)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def wait_port(host, port, timeout=15.0):
    """轮询等待 host:port 可连接(服务已起来),超时抛错。"""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:   # 0 = 连接成功
                return True
        time.sleep(0.2)
    raise TimeoutError(f"等待 {host}:{port} 启动超时({timeout}s)")


def _build_curl_args(base, case):
    """把结构化 case 拼成 curl 的参数列表(不含开头的 'curl')。"""
    method = case.get("method", "GET")
    url = base + case["path"]
    # -s 静默进度; -w 在响应体后追加状态码标记,便于把状态码和响应体分开
    args = ["-s", "-w", "\nCURL_HTTP_STATUS:%{http_code}", "-X", method, url]
    if case.get("show_headers"):           # -i:把响应头也打印出来
        args.append("-i")
    if "json" in case:                     # 发送 JSON 请求体
        args += ["-H", "Content-Type: application/json",
                 "-d", _json.dumps(case["json"], ensure_ascii=False)]
    for k, v in case.get("headers", {}).items():
        args += ["-H", f"{k}: {v}"]
    return args


def _pretty_cmd(base, case):
    """给人看的等价 curl 命令(省略 -s/-w 这些噪音选项)。"""
    parts = ["curl"]
    if case.get("show_headers"):
        parts.append("-i")
    parts += ["-X", case.get("method", "GET"), f"'{base + case['path']}'"]
    if "json" in case:
        body = _json.dumps(case["json"], ensure_ascii=False)
        parts += ["-H 'Content-Type: application/json'", f"-d '{body}'"]
    for k, v in case.get("headers", {}).items():
        parts += [f"-H '{k}: {v}'"]
    return " ".join(parts)


def run_curls(host, port, cases):
    """对每条 case 执行真实 curl,打印命令与响应。"""
    base = f"http://{host}:{port}"
    for i, case in enumerate(cases, 1):
        print("-" * 60)
        print(f"【curl 用例 {i}】{case.get('desc', '')}")
        print("$", _pretty_cmd(base, case))          # 展示等价命令,可手动复制
        out = subprocess.run(
            ["curl", *_build_curl_args(base, case)],
            capture_output=True, text=True, encoding="utf-8",
        )
        # 把状态码标记从响应体尾部拆出来,分别打印
        body, _, status = out.stdout.rpartition("CURL_HTTP_STATUS:")
        for line in body.rstrip("\n").splitlines():
            print("  →", line)
        print(f"  → [HTTP {status.strip()}]")


def run_selftest(script_path, host, port, cases):
    """
    自测入口:拉起 serve 子进程 → 等端口 → 跑 curl → 收尾。
    script_path 传配方文件的 __file__。
    """
    if shutil.which("curl") is None:
        raise SystemExit("未找到 curl 命令,无法自测(Windows 10+ / git-bash 自带)")

    print("=" * 60)
    print(f"启动服务子进程: python {script_path} serve  (端口 {port})")
    # 静音开发服务器日志,自测输出只留 curl 用例,清爽
    proc = subprocess.Popen([sys.executable, script_path, "serve"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_port(host, port)
        print("服务就绪 → 开始用 curl 实际调用")
        run_curls(host, port, cases)
    finally:
        print("-" * 60)
        print("自测结束,关闭服务子进程")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
