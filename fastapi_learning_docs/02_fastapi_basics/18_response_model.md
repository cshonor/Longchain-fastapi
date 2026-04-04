# FastAPI response_model（响应模型）

在路径装饰器上用 **response_model=...** 声明接口返回结构。底层仍是 **Pydantic**：转换、校验、OpenAPI 文档、**字段过滤**。

（与 [Request Body](./07_request_body.md)、[复杂嵌套模型](./12_pydantic_complex_nested_models.md) 一起看。）

---

## 一、response_model 做什么

1. 把返回值约束/转换成声明的模型形态  
2. 对返回值做校验  
3. 生成 /docs 里的响应 Schema  
4. **过滤字段**：只输出模型里声明的字段（防泄露敏感字段）

```python
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item
```

支持 response_model=Item、response_model=list[Item]，各 HTTP 方法均可使用。

---

## 二、输入输出分离（推荐）

请求体与响应用不同模型，避免把 password 等返回给客户端。

```python
class UserIn(BaseModel):
    username: str
    password: str
    email: str
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: str
    full_name: str | None = None


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user
```

若使用 EmailStr，通常需安装 email-validator。

---

## 三、装饰器常用参数

### response_model_exclude_unset=True

只序列化本次实际赋值过的字段。

```python
@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
```

### response_model_include / response_model_exclude

```python
# 只返回 name、description
response_model_include={"name", "description"}

# 不返回 tax
response_model_exclude={"tax"}
```

临时白名单或黑名单。长期维护优先拆成不同 Out 模型。

---

## 四、联合类型

返回多种模型之一时用 **Union** 或 **X | Y**（Python 3.10+）：

```python
@app.get("/things/{kind}", response_model=PlaneItem | CarItem)
async def read_thing(kind: str):
    ...
```

---

## 五、列表与字典

```python
@app.get("/items/", response_model=list[Item])
async def list_items():
    ...
```

```python
@app.get("/keyword-weights/", response_model=dict[str, float])
async def weights():
    return {"a": 0.2, "b": 0.8}
```

---

## 一句话

response_model 规范返回值并过滤敏感字段；入参出参用不同模型；exclude_unset 只返设置过的字段；include/exclude 尽量少用。

---

## 可运行示例

见 [fastapi_response_model_demo.py](./fastapi_response_model_demo.py)。
