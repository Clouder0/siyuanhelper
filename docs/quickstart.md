# Quickstart

In this page you will get a glimpse of SiyuanHelper.

You might need a bit understanding of async/await in python to get things work, but it won't be hard. This quickstart tutorial won't cover much related stuff. So don't worry, let's just start.

## Initialize

Most of the time, you'll only use the following code to generate a Siyuan instance.

```python
from siyuanhelper.api import Siyuan
import asyncio

async def main():
    siyuan = Siyuan()

asyncio.run(main())
```

## Get a Block

A frequent demand is to search for some specific blocks.

We can look for a Block by its id.

```python
async def main():
    siyuan = Siyuan()
    block = await siyuan.get_block_by_id("20220501134149-qexauwn")
```

We can also find a list of blocks by SQL query:

```python
blocks = await siyuan.get_blocks_by_sql("WHERE updated>20220504230000")
```

## Use a Block

We might want to get some information about a block.

```python
await block.ensure()  
# sometimes, blocks are lazily-loaded, use ensure() to guarantee its availability
# pull() can be used to ensure the block is up-to-date
# await block.pull()
print(block.id)
print(block.updated)
print(block.markdown)
print(await block.attrs.get("custom-attr"))
```

Modifying a block is also possible.

```python
another_block = await block.insert(DataType.markdown, "Another **block** after me.")
await block.delete()
```

??? note

    There is a delay between the modification and data queried by Siyuan API.  
    That is to say, though your modification to a block is instantly done, you can't immediately get its information from Siyuan API due to some caching mechanism I guess.

## Play with Attributes

One of Siyuan Note's most powerful features is the custom attributes.

You can easily read and write block attributes with the help of Siyuan Helper.

```python
await block.attrs.get("custom-attr1")
await block.attrs.set("custom-attr2", "value")
```

Searching for blocks with attribute conditions hasn't been supported so far, but [on our todo-list](https://github.com/Clouder0/siyuanhelper/issues/8).

## Cleaning Up

It is recommended to close the connection when your script exits. Not mandatory though.

```python
await siyuan.close()
```
