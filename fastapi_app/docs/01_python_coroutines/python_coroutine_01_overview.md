# Python 协程（一）概述


---

## 一、协程介绍

**协程**（Coroutine），又称微线程或纤程，是一种**用户态**的轻量级调度单位，是实现多任务的一种方式。其本质仍运行在**单个线程**内，通过程序逻辑控制「在哪些代码块之间切换执行顺序」。

更直观的说法：

- 线程里有许多**子程序**（函数）。
- 子程序 A 执行到某处可以**中断**，切换到子程序 B。
- 在合适时机再切回 A，从**上次中断处**继续执行。

这种「协作式」的切换过程，就是常说的协程。

---

## 二、Python 3.x 协程与 asyncio（推荐只学这一套）

### 1. 早期风格：`@asyncio.coroutine` 与 `yield from`（Python 3.4+）

```python
import asyncio


@asyncio.coroutine
def get_body(i):
    print(f"start{i}")
    yield from asyncio.sleep(1)
    print(f"end{i}")


loop = asyncio.get_event_loop()
tasks = [get_body(i) for i in range(5)]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
```

多个任务会交错 `start` / `end`；`asyncio.sleep` 让出控制权给事件循环。

### 2. 推荐风格：`async` / `await`（Python 3.5+）

把装饰器协程改为原生协程函数：用 **`async def`** 定义，用 **`await`** 等待可等待对象。

```python
import asyncio


async def get_body(i):
    print(f"start{i}")
    await asyncio.sleep(1)
    print(f"end{i}")


async def main():
    await asyncio.gather(*(get_body(i) for i in range(5)))


if __name__ == "__main__":
    asyncio.run(main())
```

**Python 3.7+** 推荐使用 **`asyncio.run(...)`** 作为程序入口：创建事件循环、运行主协程、结束时关闭循环。尽量在整个进程内只作为**顶层入口**调用一次（具体场景可按框架要求调整）。

### 3.5 `await B()` 时，谁让出执行权（谁“放弃 CPU”）？

结论：当执行到 `await B()` 时，**让出执行权的是当前协程 A**（也就是“正在运行并执行到 `await` 的那个协程”），不是 B。

```python
async def A():
    print("A start")
    await B()
    print("A end")
```

执行流程可以按下面理解：

1. A 运行到 `await B()`。
2. 启动/推进 B 的执行（直到 B **完成**，或在内部再次遇到 `await` 需要等待）。
3. 若 B 需要等待（I/O / `sleep` 等），此时 **A 会暂停**，并把执行权交还给事件循环。
4. 事件循环去运行其它就绪任务；当 B 等待完成并最终结束后，A 才会被唤醒继续往下执行。

### 3. 协程对象不能直接「运行」

```python
import asyncio


async def work(x):
    for _ in range(3):
        print("Work {} is running ..".format(x))


coroutine_1 = work(1)  # 这是协程对象，不是函数调用结果

# 方式一（显式循环）：
loop = asyncio.get_event_loop()
result = loop.run_until_complete(coroutine_1)
print(result)  # 若无 return，一般为 None

# 方式二（推荐，3.7+）：
# asyncio.run(work(1))
```

### asyncio 协程的几条结论

1. `async def` 得到的是**协程对象**，需交给**事件循环**驱动执行。
2. 同一时刻在单线程内**只执行一个**协程片段；并发感来自**让出等待**（I/O、sleep 等），不是多核并行。
3. 若 `await` 后面是**同步阻塞**且很重的 CPU 工作，会卡住整个循环——应放到线程池/进程池或改写为异步 API。
4. 协程仍在**单线程**模型下协作，不等同于利用多核的**并行**（parallel）。

---

## 三、为什么要使用协程

CPython 有 **GIL**，多线程在 CPU 密集型场景下往往无法真正并行多核执行，且线程切换有成本。

协程常见优势（概括）：

1. **调度由程序结构表达**（`await`、事件循环），模型相对清晰。
2. 相比频繁操作系统线程切换，协作式切换开销通常更小（视场景而定）。
3. 单线程内共享状态，可减少部分锁的需求（但仍需注意逻辑正确性与异步安全）。

典型适用场景：**高并发 I/O**（如爬虫、网关、大量连接等待）、与 **FastAPI/Starlette** 等异步栈配合。CPU 密集任务仍应考虑多进程或 native 扩展。

---

-

## 与后续章节

下一主题建议：**Python 协程（二）Asyncio 入门**（可与官方文档 [asyncio](https://docs.python.org/3/library/asyncio.html) 对照）。

原文脉络参考：博客园「麦克煎蛋」《Python协程(一) 概述》（2020-08-14）。
