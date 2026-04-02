# Python 协程（三）Asyncio 运行（终极完整版·MD笔记）

> **整合协程(一)+(二)+(三)核心逻辑，无冗余、无漏洞，重点突出，可直接作为正式教程使用**  
> 约束：全程不包含 `yield` / `greenlet` / `gevent`，只保留现代 `asyncio` 核心。

---

## 一、核心前置知识（协程(一)+(二)回顾）

在学习 **Asyncio 运行机制** 前，先明确 3 个底层核心概念。

### 1. 协程（Coroutine）的本质

- **协程函数**：由 `async def` 定义，例如 `async def main(): ...`
- **协程对象**：调用协程函数得到的对象（`coro = main()`），**此时代码不会执行**
- **核心特点**：可暂停、可恢复，必须通过 `await` 或被调度（通常是 Task）才能执行

关键限制（常见误区）：

- **协程对象不是线程**，不会自动运行
- EventLoop 调度的“单位”是 **Task/Future**；协程对象需要被纳入调度体系

### 2. EventLoop（事件循环）—— 整个异步程序的“大脑”

- **本质**：单线程内的调度循环（持续运行的事件驱动系统）
- **底层依赖**：I/O 多路复用（如 epoll/kqueue）、定时器
- **核心能力**：管理异步任务的执行、暂停、恢复、切换
- **常见入口**：通常由 `asyncio.run()` 创建并管理生命周期

### 3. 可等待对象（Awaitable）—— 能被 `await` 的对象

可等待对象是 asyncio 的核心抽象，常见三类：

| 类型 | 是否可被 EventLoop 调度/追踪 | 核心作用 | 直观理解 |
|------|------------------------------|----------|----------|
| **协程（Coroutine）** | 间接（需纳入调度体系） | 基础异步任务单元 | “待执行的异步函数调用” |
| **Task** | ✅ | 被 EventLoop 调度的并发任务 | 协程的“调度翅膀” |
| **Future** | ✅ | 异步结果占位符 | “未来会有结果的盒子” |

---

## 二、Asyncio 程序入口：`asyncio.run()`

### 1. 核心结论

只要你用到 `async/await`，**主入口通常应通过 `asyncio.run()` 启动**，它负责创建并管理 EventLoop 的生命周期。

> 注：某些框架（如 FastAPI/uvicorn）会自己创建并管理事件循环，你的代码不再直接调用 `asyncio.run()`，但“事件循环驱动协程”这一核心机制不变。

### 2. `asyncio.run()` 做了什么（4 步）

```python
import asyncio

async def main():
    ...

asyncio.run(main())
```

典型包含：

1. 创建新的 EventLoop
2. 运行入口协程（把 `main()` 放入循环驱动执行）
3. 等待入口协程结束（以及其所等待的任务链）
4. 关闭 EventLoop，释放资源

### 3. 核心规则（必须牢记）

- **不要在已运行 EventLoop 的线程里再调用 `asyncio.run()`**（会报错）
- 同步代码不能“直接”运行协程对象：需要事件循环驱动（`asyncio.run`/框架/loop）
- 进入异步世界后（在 `main()` 内），可以自由调用同步函数；但同步函数里想调用异步，需要谨慎设计（尽量在同一循环内完成）

### 4. 标准入口示例

```python
import asyncio


async def task(name: str, delay: float) -> None:
    await asyncio.sleep(delay)
    print(f"任务 {name} 完成")


async def main() -> None:
    print("异步程序启动")
    await task("A", 1)
    print("同步代码：仍然可以在协程里直接执行")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 三、Task：协程的“调度翅膀”

### 1. 为什么需要 Task？

你关心的关键点是：**EventLoop 如何调度并唤醒协程？**

- 协程对象本身只是“可暂停的执行流描述”
- 当它被包装为 **Task** 后，事件循环才能以“任务”的方式追踪其状态、推进执行、在 I/O 完成后唤醒继续跑

### 2. Task 的本质

**Task = 协程 + 调度能力**（可被 EventLoop 追踪、推进、取消、读取结果）。

### 3. 创建 Task：`asyncio.create_task()`

```python
import asyncio


async def task(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} done"


async def main():
    t1 = asyncio.create_task(task("A", 1))
    t2 = asyncio.create_task(task("B", 2))

    print(await t1)
    print(await t2)


asyncio.run(main())
```

### 4. “裸协程”的自动包装（关键）

当你写 `await b()`（其中 `b()` 是协程对象），事件循环会把它纳入可推进的等待链。

从“学习理解”角度，你可以把它近似理解为：

- 把协程纳入调度体系
- 在它完成或等待时做切换

当你需要“主动并发”（同时跑多个协程）时，就应该显式 `create_task()` 或使用 `gather()`。

### 5. Task 的常用操作（速查）

| 操作 | 方法 | 说明 |
|------|------|------|
| 创建 | `asyncio.create_task(coro)` | 纳入调度、并发执行 |
| 等待 | `await task` | 等待完成并取结果 |
| 取消 | `task.cancel()` | 触发取消（会引发 `CancelledError`） |
| 完成 | `task.done()` | 是否完成 |
| 结果 | `task.result()` | 取结果（需已完成） |
| 异常 | `task.exception()` | 取异常（需已完成） |

---

## 四、并发执行核心：`asyncio.gather()`

### 1. 核心作用

**批量并发运行多个可等待对象（协程/Task/Future），并等待全部完成，返回结果列表。**

### 2. gather 的核心逻辑（理解版）

你可以把 `gather()` 理解为：

1. 把传入的多个协程纳入调度（必要时包装为可追踪任务）
2. 并发推进它们执行
3. 等全部结束后，按传入顺序返回结果列表

### 3. 标准示例：并发计算阶乘（用 `sleep` 模拟 I/O）

```python
import asyncio


async def factorial(name: str, number: int) -> int:
    result = 1
    for i in range(2, number + 1):
        print(f"Task {name}：计算 {i}...")
        await asyncio.sleep(1)
        result *= i
    print(f"Task {name}：结果 = {result}")
    return result


async def main() -> None:
    print("并发任务启动")
    results = await asyncio.gather(
        factorial("A", 2),
        factorial("B", 3),
        factorial("C", 4),
    )
    print(f"所有任务结果：{results}")  # [2, 6, 24]


if __name__ == "__main__":
    asyncio.run(main())
```

### 4. `return_exceptions`

- **默认 `False`**：任何一个任务抛异常，`gather()` 直接抛出
- **`True`**：异常会作为结果放入列表，便于容错处理

```python
import asyncio


async def ok():
    await asyncio.sleep(0.2)
    return 1


async def fail():
    await asyncio.sleep(0.1)
    raise ValueError("任务执行失败")


async def main():
    results = await asyncio.gather(ok(), fail(), ok(), return_exceptions=True)
    print(results)  # [1, ValueError('任务执行失败'), 1]


asyncio.run(main())
```

---

## 五、终极执行流程（全链路闭环）

以 `await gather(coro1, coro2, coro3)` 为例：

1. 程序启动：`asyncio.run(main())` 创建 EventLoop 并运行 `main()`
2. `main()` 执行到 `await asyncio.gather(...)`
3. `gather()` 把多个协程纳入调度，形成多个并发推进的任务
4. EventLoop 轮转推进：哪个协程遇到 `await`（例如 `sleep` / I/O），哪个就暂停让出执行权
5. I/O 就绪后，EventLoop 唤醒对应任务继续执行
6. 所有任务完成 → `gather()` 返回结果列表 → `main()` 结束 → EventLoop 关闭

---

## 六、核心总结（必背）

1. **入口**：需要事件循环驱动；命令行脚本通常用 `asyncio.run()` 作为入口
2. **调度单位**：并发执行的核心载体是 **Task**（可被追踪、可切换、可取消）
3. **并发实现**：
   - `create_task()`：显式创建并发任务
   - `gather()`：批量并发 + 等待全部完成
4. **切换原理**：协程在 `await` 时暂停让出执行权 → EventLoop 切换执行其它就绪任务 → I/O 完成后唤醒继续跑

终极一句话：

**Asyncio 通过事件循环驱动协程执行，以 Task 为调度载体，协程在 await 处让出执行权，事件循环在等待期间切换其它任务，从而在单线程内实现高并发。**

