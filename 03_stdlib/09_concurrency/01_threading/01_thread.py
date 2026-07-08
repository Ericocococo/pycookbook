"""threading —— Thread 创建与生命周期

标准库。Python 3.12。
运行: python 01_thread.py

演示：
  ① Thread 基础：创建 / start / join
  ② 传参：args / kwargs
  ③ daemon 线程：主线程退出时自动终止
  ④ 继承 Thread：把逻辑封装成类
  ⑤ threading.current_thread / enumerate / active_count
"""
import threading
import time


def demo01_basic():
    """① Thread 基础：创建 / start / join

    术语：
      start()  启动线程，操作系统分配时间片开始执行
      join()   主线程阻塞等待子线程结束；不调用 join 则主线程不等子线程
      target   线程执行的函数
    """
    print("① Thread 基础")

    def worker(name):
        print(f"  [{name}] 开始")
        time.sleep(0.2)
        print(f"  [{name}] 结束")

    t1 = threading.Thread(target=worker, args=("线程A",))
    t2 = threading.Thread(target=worker, args=("线程B",))

    t1.start()
    t2.start()

    print("  主线程：两个线程已启动，等待结束...")
    t1.join()
    t2.join()
    print("  主线程：所有线程已结束")


def demo02_args():
    """② 传参：args（位置参数元组）/ kwargs（关键字参数字典）"""
    print("\n② 传参")

    def greet(name, greeting="你好"):
        print(f"  {greeting}, {name}！（线程 {threading.current_thread().name}）")

    threads = [
        threading.Thread(target=greet, args=("Alice",)),
        threading.Thread(target=greet, args=("Bob",), kwargs={"greeting": "Hi"}),
        threading.Thread(target=greet, kwargs={"name": "Charlie", "greeting": "Hey"}),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def demo03_daemon():
    """③ daemon 线程

    术语：
      daemon  守护线程，当所有非 daemon 线程结束后，daemon 线程自动被强制终止。
              主线程本身是非 daemon 线程。

    适合：后台任务（心跳、日志刷新），不需要等它做完，主程序退出时一起结束。
    注意：daemon 线程被强制终止，可能在 IO 中途被打断，不适合有清理工作的任务。
    """
    print("\n③ daemon 线程")

    def background():
        for i in range(10):
            print(f"  [后台] 第 {i} 次心跳")
            time.sleep(0.1)

    t = threading.Thread(target=background, daemon=True)
    t.start()

    # 主线程只等 0.25 秒，daemon 线程还没跑完就会被终止
    time.sleep(0.25)
    print("  主线程退出，daemon 线程自动终止（可能还没跑完）")


def demo04_subclass():
    """④ 继承 Thread：把线程逻辑封装成类

    适合：线程需要维护状态，或者逻辑较复杂时。
    重写 run() 方法，start() 内部会调用 run()。
    """
    print("\n④ 继承 Thread")

    class DownloadThread(threading.Thread):
        def __init__(self, url):
            super().__init__(name=f"下载-{url}")
            self.url = url
            self.result = None          # 用实例变量保存结果

        def run(self):
            # 模拟下载
            time.sleep(0.1)
            self.result = f"{self.url} 的内容"
            print(f"  [{self.name}] 下载完成")

    threads = [DownloadThread(f"url_{i}") for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        print(f"  结果: {t.result}")


def demo05_thread_info():
    """⑤ 线程信息：current_thread / enumerate / active_count"""
    print("\n⑤ 线程信息")

    def worker():
        t = threading.current_thread()
        print(f"  当前线程: name={t.name!r}, ident={t.ident}, daemon={t.daemon}")
        time.sleep(0.1)

    threads = [threading.Thread(target=worker, name=f"Worker-{i}") for i in range(3)]
    for t in threads:
        t.start()

    time.sleep(0.05)
    print(f"  活跃线程数: {threading.active_count()}")
    print(f"  所有活跃线程: {[t.name for t in threading.enumerate()]}")

    for t in threads:
        t.join()


if __name__ == "__main__":
    demo01_basic()
    demo02_args()
    demo03_daemon()
    demo04_subclass()
    demo05_thread_info()
