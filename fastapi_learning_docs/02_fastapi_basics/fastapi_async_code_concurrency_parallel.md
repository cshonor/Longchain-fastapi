# FastAPI 异步、并发与并行（学习笔记）

> 作者：麦克煎蛋  出处：https://www.cnblogs.com/mazhiyong/ 转载请保留这段声明，谢谢！

---

## 一、什么时候用 async def / 普通 def
1. 如果调用的库需要 `await`
   ```python
   results = await some_library()
   ```
   必须用：
   ```python
   @app.get('/')
   async def read_results():
       results = await some_library()
       return results
   ```

2. 如果库**不支持 await**，用普通 def 即可：
   ```python
   @app.get('/')
   def results():
       results = some_library()
       return results
   ```

3. 不知道用啥 → 一律用普通 `def`。

FastAPI 无论哪种写法都能异步运行，只是规范写法性能更好。

---

## 二、什么是异步代码
异步 = 程序在**等待 I/O 时可以去干别的事**，而不是死等。

典型等待场景：
- 网络请求
- 文件读写
- 数据库操作
- 调用第三方 API

这些都叫 **I/O 密集型**，非常适合异步。

---

## 三、并发 vs 并行（最通俗理解）

### 1. 并发（Concurrency）
- 你在等汉堡的时候，可以和朋友聊天
- 一个人**交替做多个任务**，看起来像同时进行
- 适合：大量等待、I/O 多的场景（Web 接口）

> 吃饭到一半接电话，接完继续吃 = 并发

### 2. 并行（Parallelism）
- 多个人同时干活
- 真正**同时执行多个任务**
- 适合：计算密集型（视频处理、机器学习、数学计算）

> 一边吃饭一边打电话 = 并行

### 3. 总结
- **并发**：有处理多个任务的能力（不一定同时）
- **并行**：能真正同时处理多个任务

Web 应用大多是 **I/O 密集型 → 并发就够强**。

---

## 四、async / await 语法规则
1. `await` 只能放在 `async def` 函数里
2. `async def` 函数叫 **协程函数**
3. 调用 `async def` 必须加 `await`，否则不执行

```python
async def get_burgers(number: int):
    return burgers

# 正确
burgers = await get_burgers(2)

# 错误，不会真正执行
burgers = get_burgers(2)
```

---

## 五、协程是什么
`async def` 定义的函数返回的对象就叫 **协程（coroutine）**。

特点：
- 可以暂停（遇到 await）
- 可以恢复
- 是 Python 异步的核心单元

---

## 六、FastAPI 内部怎么运行
1. **普通 def 路由**
   不在主线程跑，丢进 **线程池**，不会阻塞服务器。

2. **async def 路由**
   以协程方式运行，遇到 await 自动切换任务。

3. **依赖项**
   - `def` 依赖 → 线程池
   - `async def` 依赖 → 协程方式
   混用也能正常运行。

---

## 七、最简单记忆口诀
- 等待网络/数据库/API → 用 `async def + await`
- 纯计算、普通库 → 用普通 `def`
- 不知道怎么选 → 一律 `def`
- FastAPI 会自动处理得很快

---

参考：
- https://fastapi.tiangolo.com/async/