"""⑥ 代码补全 —— 发一个请求，拿回补全列表

运行: python 06_lsp_completion.py

前面学了怎么启动 Pyright、怎么初始化、怎么打开文件。
现在请求代码补全——告诉 Pyright 光标在哪，它告诉你该补什么。

演示：
  ① 完整的 初始化→开文件→请求补全 流程
  ② 理解 LSP 三种消息：请求（有 id）、通知（无 id）、推送（服务器主动发）
"""

import json
import shutil
import subprocess


def _read_message(p) -> dict | None:
    content_length = 0
    while True:
        line = p.stdout.readline()
        if not line:
            return None
        if line.startswith(b"Content-Length:"):
            content_length = int(line.split(b":")[1])
        if not line.strip():
            break
    return json.loads(p.stdout.read(content_length))


def _send(p, data: dict) -> None:
    body = json.dumps(data).encode()
    cb = f"Content-Length: {len(body)}\r\n\r\n".encode() + body
    print(cb)
    p.stdin.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
    p.stdin.flush()


def demo():
    exe = shutil.which("pyright-langserver")
    p = subprocess.Popen([exe, "--stdio"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # ① 初始化
    _send(p, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"processId": None, "capabilities": {}, "rootUri": None}})
    while True:
        msg = _read_message(p)
        print(msg)
        if msg and msg.get("id") == 1:
            break

    print()
    _send(p, {"jsonrpc": "2.0", "method": "initialized", "params": {}})

    print()
    # ② 打开文件
    # code 是多行代码，\n 分行。三行分别是 line 0 / 1 / 2（从 0 数）：
    #   line 0: print('hello')
    #   line 1: x = [1, 2, 3]      ← x 是 list，有 append/extend/pop 等方法
    #   line 2: x.                 ← 光标停在这，待会请求补全 x 的成员
    code = "print('hello')\nx = [1, 2, 3]\nx."
    _send(p, {
        "jsonrpc": "2.0",
        "method": "textDocument/didOpen",
        "params": {
            "textDocument": {
                "uri": "file:///demo.py",  # 文件标识
                "languageId": "python",  # 按 Python 规则检查
                "version": 1,  # 首次打开版本号为 1
                "text": code  # 完整代码内容
            },
        }})
    # didOpen 是通知，Pyright 收到后先分析、推 publishDiagnostics（下面等它），
    # 分析完文档它才知道 x 是 list，第 ③ 步请求补全才能给出 list 的方法

    """
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Starting service instance "<default>"'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'No include entries specified; assuming \\<default workspace root>'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Auto-excluding **/node_modules'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Auto-excluding **/__pycache__'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Auto-excluding **/.*'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Assuming Python version 3.12.13.final.0'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 1, 'message': 'File or directory "\\<default workspace root>" does not exist.'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'No source files found.'}}
    {'jsonrpc': '2.0', 'method': 'textDocument/publishDiagnostics', 'params': {'uri': 'file:///demo.py', 'version': 1, 'diagnostics': [{'range': {'start': {'line': 2, 'character': 1}, 'end': {'line': 2, 'character': 2}}, 'message': 'Expected attribute name after "."', 'severity': 1, 'source': 'Pyright'}]}}
      诊断: 第3行2列 — Expected attribute name after "."
    """
    # ── Pyright 对上面 code 的诊断结果 ──
    # 因为最后一行是 "x."——点号后面没写属性名，Pyright 认为这是语法错误
    a = {
        'jsonrpc': '2.0',
        'method': 'textDocument/publishDiagnostics',  # 诊断推送（服务器主动发）
        'params': {
            'uri': 'file:///demo.py',  # 哪个文件
            'version': 1,  # 对应 didOpen 的版本号（确认诊断的是这一版）
            'diagnostics': [  # 错误列表，这里 1 个
                {'range': {'start': {'line': 2, 'character': 1},  # 第3行第2列（x. 的 . 处）
                           'end': {'line': 2, 'character': 2}},
                 'message': 'Expected attribute name after "."',  # "." 后面缺属性名
                 'severity': 1,  # 1=Error 红波浪线
                 'source': 'Pyright'}  # 谁报的
            ]}
    }
    # 注意：这个"错误"是我们故意留的——写 x. 就是为了触发补全，
    # 语法上确实不完整，但正好让 Pyright 知道"你想访问 x 的成员"，
    # 第 ③ 步请求补全时它就会列出 list 的所有方法

    # 等诊断推送
    #
    # ⚠ 澄清：补全 ≠ 必须先有诊断，两者是独立的功能。
    #   - 诊断 publishDiagnostics：Pyright didOpen 后【主动推】，你不请求也会来
    #   - 补全 completion：你【主动请求】，跟诊断无关
    #
    # 那这里为什么要等诊断？——把它当作"Pyright 分析完了"的信号。
    #   didOpen 后 Pyright 要花一点时间解析文档（才知道 x 是 list）。
    #   收到诊断推送 = 分析结束，这时再请求补全，结果最准最全。
    #   如果 didOpen 后立刻请求补全，可能 Pyright 还没分析完，返回空或不全。
    #
    # 所以：不是"补全必须先诊断"，而是"最好等分析完"，诊断恰好是那个信号。
    while True:
        msg = _read_message(p)
        print(msg)
        if msg and msg.get("method") == "textDocument/publishDiagnostics":
            diags = msg["params"]["diagnostics"]
            if diags:
                for d in diags:
                    line = d["range"]["start"]["line"] + 1
                    col = d["range"]["start"]["character"] + 1
                    print(f"  诊断: 第{line}行{col}列 — {d['message']}")
            break

    print()
    # ③ 请求补全
    print("\n③ 请求补全（光标在 x. 后面）...")
    _send(p, {
        "jsonrpc": "2.0",
        "id": 99,  # 请求 id，随便取（这里 99），响应会带回同样的 id
        "method": "textDocument/completion",  # 方法名：请求代码补全
        "params": {
            "textDocument": {"uri": "file:///demo.py"},  # 对哪个文件（要和 didOpen 的 uri 一致）
            # position = 光标位置，告诉 Pyright"在这里补什么"
            #   line 2      = 第 3 行（从 0 数），即 "x." 那行
            #   character 2 = 第 3 列（从 0 数），即 . 后面的位置
            # 组合起来：光标停在 "x." 的点号后面 → Pyright 返回 x（list）的所有成员
            "position": {"line": 2, "character": 2},
        }})
    # completion 是【请求】（有 id 99），所以下面用 while 等 id==99 的响应，
    # 响应的 result.items 就是补全列表（append/extend/pop/...）

    # ── 补全响应（id=99 对应上面的请求）——只保留前几项示意，实际有几十个 ──
    a = {
        'jsonrpc': '2.0',
        'id': 99,  # 对应请求的 id=99
        'result': {
            'items': [  # 补全项列表，编辑器把它渲染成下拉菜单
                # 每一项的字段：
                #   label     显示在下拉菜单里的文字（用户看到的补全名）
                #   kind      类型，决定图标：2=Method 方法, 6=Variable 变量, 10=Property 属性
                #   sortText  排序键，控制在菜单里的先后（常用的排前面，如 append=09 排在 __doc__=13 前）
                #   data      Pyright 内部数据，用于后续 completionItem/resolve 查详细文档（懒加载）
                {'label': 'append', 'kind': 2, 'sortText': '09.9999.append',
                 'data': {'uri': 'file:///demo.py', 'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True, 'symbolLabel': 'append'}},
                {'label': 'extend', 'kind': 2, 'sortText': '09.9999.extend',
                 'data': {'uri': 'file:///demo.py', 'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True, 'symbolLabel': 'extend'}},
                {'label': 'pop', 'kind': 2, 'sortText': '09.9999.pop',
                 'data': {'uri': 'file:///demo.py', 'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True, 'symbolLabel': 'pop'}},
                {'label': 'sort', 'kind': 2, 'sortText': '09.9999.sort',
                 'data': {'uri': 'file:///demo.py', 'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True, 'symbolLabel': 'sort'}},
                {'label': '__doc__', 'kind': 6, 'sortText': '13.9999.__doc__',
                 'data': {'uri': 'file:///demo.py', 'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True, 'symbolLabel': '__doc__'}},
                # ── 完整响应有 50+ 项，按 sortText 前缀分档、按 kind 分类 ──
                #
                # sortText = 排序键（字符串，编辑器按字典序排，不是按数字！）
                #   为什么补零成 09/11/13 两位数：字符串比较 "09"<"11"<"13" 才成立；
                #   若写 9/11/13，字典序里 "11"<"9" 就乱了，所以 Pyright 一律补零。
                #
                # 数字前缀是 Pyright 源码定的优先级档位（越小越靠前），完整档位：
                #   06 LiteralValue    字面量候选值（Literal 类型的可选值）
                #   07 NamedParameter  命名参数（func(参数名= 时补参数名）
                #   08 Keyword         关键字（if/for/return...）
                #   09 NormalSymbol    普通公开成员：append/extend/pop/sort/insert...  ← 本例
                #   11 PrivateSymbol   次要/半私有成员：clear/reverse
                #   13 DunderSymbol    双下划线魔术方法/属性：__len__/__iter__/__doc__...  ← 本例
                #   （06→13 跳号留空，方便以后插新档位不用重排，像目录序号留空间）
                #
                # 为什么本例只出现 09/11/13 三档：
                #   我们补的是 "x." —— 点号后只可能是【成员】，
                #   所以只有成员类档位(09/11/13)，不会出现关键字(08)、命名参数(07)等。
                #   若在别处补全（如空行开头），就会看到 08 关键字档。
                #   → 菜单效果：append(09) 排最前，clear(11) 居中，__doc__(13) 沉底
                #
                # kind = 补全项类型（决定图标）：
                #   2  = Method   方法（append/pop/__len__...）—— 大多数
                #   6  = Variable 变量（__doc__/__module__/__dict__...）
                #   10 = Property 属性（__class__）
            ],
            # isIncomplete=True → 列表不完整：用户继续输入时编辑器要重新请求补全
            #   （比如输入 x.ap 后，编辑器再发一次请求，Pyright 只返回 append 等匹配项）
            #   =False 则表示"这就是全部"，用户继续输入编辑器只需本地过滤，不用再问
            'isIncomplete': True}}
    # 编辑器拿到 items 后：按 sortText 排序 → 按 kind 配图标 → 渲染成下拉菜单
    # 用户选中某项，才用 data 发 completionItem/resolve 请求拉取该项的文档（省性能）
    while True:
        msg = _read_message(p)
        print(msg)
        if msg and msg.get("id") == 99:
            items = msg["result"]["items"]
            print(f"  收到 {len(items)} 个补全项：")
            for item in items[:8]:
                print(f"    · {item['label']:<20} {item.get('detail', '')}")
            break

    p.kill()
    p.wait()

    a = {
        'jsonrpc': '2.0',
        'id': 99,
        'result': {
            'items': [
                {'label': '__doc__', 'kind': 6, 'sortText': '13.9999.__doc__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__doc__'}},
                {'label': '__module__', 'kind': 6,
                 'sortText': '13.9999.__module__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__module__'}},
                {'label': '__qualname__', 'kind': 6,
                 'sortText': '13.9999.__qualname__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__qualname__'}},
                {'label': '__init__', 'kind': 2,
                 'sortText': '13.9999.__init__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__init__'}},
                {'label': 'copy', 'kind': 2, 'sortText': '09.9999.copy',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True, 'symbolLabel': 'copy'}},
                {'label': 'append', 'kind': 2, 'sortText': '09.9999.append',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': 'append'}},
                {'label': 'extend', 'kind': 2, 'sortText': '09.9999.extend',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': 'extend'}},
                {'label': 'pop', 'kind': 2, 'sortText': '09.9999.pop',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True, 'symbolLabel': 'pop'}},
                {'label': 'index', 'kind': 2, 'sortText': '09.9999.index',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': 'index'}},
                {'label': 'count', 'kind': 2, 'sortText': '09.9999.count',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': 'count'}},
                {'label': 'insert', 'kind': 2, 'sortText': '09.9999.insert',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': 'insert'}},
                {'label': 'remove', 'kind': 2, 'sortText': '09.9999.remove',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': 'remove'}},
                {'label': 'sort', 'kind': 2, 'sortText': '09.9999.sort',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True, 'symbolLabel': 'sort'}},
                {'label': '__len__', 'kind': 2, 'sortText': '13.9999.__len__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__len__'}},
                {'label': '__iter__', 'kind': 2,
                 'sortText': '13.9999.__iter__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__iter__'}},
                {'label': '__hash__', 'kind': 6,
                 'sortText': '13.9999.__hash__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__hash__'}},
                {'label': '__getitem__', 'kind': 2,
                 'sortText': '13.9999.__getitem__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__getitem__'}},
                {'label': '__setitem__', 'kind': 2,
                 'sortText': '13.9999.__setitem__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__setitem__'}},
                {'label': '__delitem__', 'kind': 2,
                 'sortText': '13.9999.__delitem__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__delitem__'}},
                {'label': '__add__', 'kind': 2, 'sortText': '13.9999.__add__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__add__'}},
                {'label': '__iadd__', 'kind': 2,
                 'sortText': '13.9999.__iadd__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__iadd__'}},
                {'label': '__mul__', 'kind': 2, 'sortText': '13.9999.__mul__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__mul__'}},
                {'label': '__rmul__', 'kind': 2,
                 'sortText': '13.9999.__rmul__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__rmul__'}},
                {'label': '__imul__', 'kind': 2,
                 'sortText': '13.9999.__imul__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__imul__'}},
                {'label': '__contains__', 'kind': 2,
                 'sortText': '13.9999.__contains__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__contains__'}},
                {'label': '__reversed__', 'kind': 2,
                 'sortText': '13.9999.__reversed__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__reversed__'}},
                {'label': '__gt__', 'kind': 2, 'sortText': '13.9999.__gt__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__gt__'}},
                {'label': '__ge__', 'kind': 2, 'sortText': '13.9999.__ge__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__ge__'}},
                {'label': '__lt__', 'kind': 2, 'sortText': '13.9999.__lt__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__lt__'}},
                {'label': '__le__', 'kind': 2, 'sortText': '13.9999.__le__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__le__'}},
                {'label': '__eq__', 'kind': 2, 'sortText': '13.9999.__eq__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__eq__'}},
                {'label': '__class_getitem__', 'kind': 2,
                 'sortText': '13.9999.__class_getitem__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__class_getitem__'}},
                {'label': 'clear', 'kind': 2, 'sortText': '11.9999.clear',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': 'clear'}},
                {'label': 'reverse', 'kind': 2, 'sortText': '11.9999.reverse',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': 'reverse'}},
                {'label': '__dict__', 'kind': 6,
                 'sortText': '13.9999.__dict__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__dict__'}},
                {'label': '__annotations__', 'kind': 6,
                 'sortText': '13.9999.__annotations__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__annotations__'}},
                {'label': '__class__', 'kind': 10,
                 'sortText': '13.9999.__class__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__class__'}},
                {'label': '__new__', 'kind': 2, 'sortText': '13.9999.__new__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__new__'}},
                {'label': '__setattr__', 'kind': 2,
                 'sortText': '13.9999.__setattr__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__setattr__'}},
                {'label': '__delattr__', 'kind': 2,
                 'sortText': '13.9999.__delattr__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__delattr__'}},
                {'label': '__ne__', 'kind': 2, 'sortText': '13.9999.__ne__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__ne__'}},
                {'label': '__str__', 'kind': 2, 'sortText': '13.9999.__str__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__str__'}},
                {'label': '__repr__', 'kind': 2,
                 'sortText': '13.9999.__repr__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__repr__'}},
                {'label': '__format__', 'kind': 2,
                 'sortText': '13.9999.__format__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__format__'}},
                {'label': '__getattribute__', 'kind': 2,
                 'sortText': '13.9999.__getattribute__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__getattribute__'}},
                {'label': '__sizeof__', 'kind': 2,
                 'sortText': '13.9999.__sizeof__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__sizeof__'}},
                {'label': '__reduce__', 'kind': 2,
                 'sortText': '13.9999.__reduce__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__reduce__'}},
                {'label': '__reduce_ex__', 'kind': 2,
                 'sortText': '13.9999.__reduce_ex__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__reduce_ex__'}},
                {'label': '__getstate__', 'kind': 2,
                 'sortText': '13.9999.__getstate__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__getstate__'}},
                {'label': '__dir__', 'kind': 2, 'sortText': '13.9999.__dir__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__dir__'}},
                {'label': '__init_subclass__', 'kind': 2,
                 'sortText': '13.9999.__init_subclass__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__init_subclass__'}},
                {'label': '__subclasshook__', 'kind': 2,
                 'sortText': '13.9999.__subclasshook__',
                 'data': {'uri': 'file:///demo.py',
                          'position': {'line': 2, 'character': 2},
                          'funcParensDisabled': True,
                          'symbolLabel': '__subclasshook__'}}],
            'isIncomplete': True}}


if __name__ == "__main__":
    demo()
