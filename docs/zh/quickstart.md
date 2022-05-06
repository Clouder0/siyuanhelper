# 快速入门

在这一页中，你将看到思源助手的一角。

你可能需要对 Python 中的 async/await 有一些了解，才能让事情顺利进行，但这并不难。这个快速入门教程不会涉及很多相关内容。所以不用担心，我们直接开始吧。

## 初始化

大多数时候，你只需要使用下面的代码来生成一个思源实例。

```python
from siyuanhelper.api import Siyuan
import asyncio

async def main():
    siyuan = Siyuan()

asyncio.run(main())
```

## 获取一个块

一个频繁的需求是搜索一些特定的块。

我们可以通过它的id来寻找一个块。

```python
async def main():
    siyuan = Siyuan()
    block = await siyuan.get_block_by_id("20220501134149-qexauwn")
```

我们也可以通过SQL查询找到一个块的列表。

```python
blocks = await siyuan.get_blocks_by_sql("WHERE updated>20220504230000" )
```

## 使用一个块

我们可能想获得一个区块的一些信息。

```python
await block.ensure()  
# 有时，区块会被懒惰地加载，使用ensure()来保证其可用性
# pull()可以用来保证区块是最新的
# await block.pull()
print(block.id)
print(block.uped)
print(block.markdown)
print(await block.attrs.get("custom-attr"))
```

修改一个块也是可以的。

```python
another_block = await block.insert(DataType.markdown, "另一个**块**在我之后。")
await block.delete()
```

??? note

    在修改和思源 API 查询的数据之间有一个延迟。 
    也就是说，虽然你对一个块的修改是即时完成的，但由于某种缓存机制，我想你不能立即从思源的 API 中获得它的信息。

## 属性

Siyuan Note 最强大的功能之一是自定义属性。

在思源助手的帮助下，你可以很容易地读取和写入块属性。

```python
await block.attrs.get("custom-attr1")
await block.attrs.set("custom-attr2", "value")
```

到目前为止还不支持用属性条件搜索块，但[在我们的todo-list上](https://github.com/Clouder0/siyuanhelper/issues/8)。

## 清理

建议在你的脚本退出时关闭连接。但不是强制性的.

```python
await siyuan.close()
```
