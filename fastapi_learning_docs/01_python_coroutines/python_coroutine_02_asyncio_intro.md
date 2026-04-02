# Python 协程（二）asyncio 入门（完整版详细总结）

> 说明：本文只保留现代 Python 3 的 `asyncio` / `async` / `await` 核心；不包含 `yield`、`greenlet`、`gevent`。

---

## 一、`asyncio` 是什么

`asyncio` 是 Python 官方内置的**异步 I/O 框架**，用来在**单线程**内实现高并发。

核心思想是：**不阻塞等待 I/O**。当等待网络、数据库、文件等操作时，把执行权交还给事件循环，让 CPU 去跑其它任务，从而提升吞吐。

它的核心组件包括：

- **EventLoop（事件循环）**
- **协程（Coroutine）**
- **Task**
- **Future**

---

## 二、EventLoop（事件循环）

EventLoop 可以理解为一个持续运行的“调度循环”，它反复做三类事：

1. 查看是否有已经就绪的 I/O 事件（socket 可读/可写）
2. 查看是否有定时器到期（例如 `asyncio.sleep`）
3. 查看是否有可等待对象（Task/Future）完成

一旦某个事件就绪，EventLoop 就会唤醒对应协程继续执行。

它负责：

- 调度协程
- 暂停协程
- 恢复协程
- 切换协程

---

## 三、为什么 `asyncio` 能实现高并发（重点）

高并发的核心不是“同时执行”，而是：**不阻塞 + 快速切换**。

当协程 A 执行到 `await B` 时：

1. 协程 A 执行到 `await B`
2. **协程 A 暂停，并主动让出执行权**
3. EventLoop 不会空等，而是**切换执行其他就绪的协程**
4. 当 B 对应的 I/O 完成后，EventLoop 收到通知
5. EventLoop 唤醒 A，继续执行

在等待 I/O 的时间里，CPU 并没有闲着，而是在跑成千上万的其他任务。

结论：

**异步非阻塞 + 快速切换 = 高并发**

---

## 四、可等待对象（Awaitable）

能被 `await` 的对象通常归为三类：

- **协程（Coroutine）**
- **Task**
- **Future**

---

## 五、协程（Coroutine）

- `async def` 定义的函数叫 **协程函数**
- 调用协程函数不会立刻执行代码，只会返回一个 **协程对象**
- 协程对象不能“自己跑起来”，必须被 `await` 或交给事件循环调度（通常通过 Task）

示例：

```python
async def func():
    return 123


coro = func()  # 得到协程对象，但还没有执行
```

---

## 六、Future（异步结果占位符）

可以把 Future 理解为“未来会产生结果的容器”：

- 现在没有结果
- 未来会有结果
- 结果分两种：成功 / 失败

设置结果的两种方式：

- **成功**：`fut.set_result(value)`
- **失败**：`fut.set_exception(exc)`

### 完整可运行例子（成功）

```python
import asyncio


async def main():
    fut = asyncio.Future()

    async def set_later():
        await asyncio.sleep(1)
        fut.set_result("我是成功结果")

    asyncio.create_task(set_later())

    res = await fut
    print(res)  # 我是成功结果


if __name__ == "__main__":
    asyncio.run(main())
```

### 完整可运行例子（失败）

```python
import asyncio


async def main():
    fut = asyncio.Future()

    async def set_later():
        await asyncio.sleep(1)
        fut.set_exception(ValueError("出错啦！"))

    asyncio.create_task(set_later())

    try:
        await fut
    except ValueError as e:
        print("失败：", e)  # 失败： 出错啦！


if __name__ == "__main__":
    asyncio.run(main())
```

一句话总结：

**Future 是一个“空盒子”，用来存放异步任务未来的结果。**

---

## 七、Task（包装协程的调度单元）

Task 可以理解为：

- **被 EventLoop 管理的协程**
- **协程 + 调度能力**
- Task 在实现上也是一种可等待对象（并且与 Future 的语义高度一致）

它的作用：

- 把协程交给事件循环**自动调度**
- 让多个协程以并发方式运行
- 可取消、可查看状态

### 创建 Task

```python
task = asyncio.create_task(coro)
```

### 为什么叫“包装协程”？

因为：

- 协程对象本身只是“待执行的异步任务描述”
- 包装成 Task 后，事件循环才能把它纳入调度体系，按就绪状态推进执行

### Task 实现并发（关键例子）

```python
import asyncio


async def say(delay, msg):
    await asyncio.sleep(delay)
    print(msg)


async def main():
    t1 = asyncio.create_task(say(1, "hello"))
    t2 = asyncio.create_task(say(2, "world"))

    await t1
    await t2


if __name__ == "__main__":
    asyncio.run(main())
```

输出：

- 约 1 秒后打印 `hello`
- 约 2 秒后打印 `world`

总耗时约 2 秒（并发），而不是 3 秒（串行）。

---

## 八、`await` 的完整作用（必须重点理解）

在协程 A 内部写：

```python
await B
```

它可以按下面的“效果”去理解：

1. 启动/推进 B 的执行
2. **暂停当前协程 A**
3. **A 让出执行权给 EventLoop**
4. EventLoop 去执行其他就绪任务

记忆句：

**谁 `await`，谁暂停，谁让出执行权。**

---

## 九、三者关系（最清晰总结）

1. **Coroutine（协程）**：原始异步任务
2. **Future**：异步结果占位符（未来成功/失败）
3. **Task**：包装协程，使其可被 EventLoop 调度并并发运行

三者都能 `await`，因此都属于可等待对象（Awaitable）。

---

## 十、整体一句话串讲

`asyncio` 通过 EventLoop 监听 I/O 与定时器事件；
协程在 `await` 时主动让出执行权；
EventLoop 快速切换其他 Task 执行；
Future 存储异步结果；
Task 包装协程实现并发；
最终在单线程内实现高并发。

