"""main API module."""
from __future__ import annotations

import dataclasses

from dataclasses import dataclass
from enum import Enum
from typing import Any, Union, cast

import aiohttp

from siyuanhelper import exceptions


data_type = Union[dict, list, None]


class Siyuan:
    """Siyuan Helper Instance."""

    def __init__(self, base_url: str = "http://127.0.0.1:6806", token: str = ""):
        """Init a Siyuan Helper.

        Args:
            base_url (str, optional): the url to invoke requests. Defaults to "http://127.0.0.1:6806".
            token (str, optional): API token, none if unused. Defaults to "".

        Raises:
            exceptions.SiyuanAuthFailedException: raised if Authorization Failed.
        """
        self.base_url = base_url
        self.token = token
        self.session = aiohttp.ClientSession(
            self.base_url,
            headers={
                "Authorization": f"Token {token}",
                "Content-Type": "application/json",
            },
        )

    async def close(self) -> None:
        """Close Siyuan Helper Session, should be explicitly called after use."""
        await self.session.close()

    async def _post(self, url: str, **params: Any) -> data_type:
        async with self.session.post(url=url, json=params) as resp:
            ret = SiyuanResponse(**(await resp.json()))
            if ret.code == 0:
                return ret.data
            if ret.code == -1 and ret.msg == "Auth failed":
                raise exceptions.SiyuanAuthFailedException((self, ret))
            else:
                raise exceptions.SiyuanApiException((self, ret))

    async def get_block_by_id(self, block_id: str, full: bool = True) -> SiyuanBlock:
        """Get SiyuanBlock by block id.

        Args:
            block_id (str): the desired block id.
            full (bool): whether to fetch all the informations. Defaults to True.

        Returns:
            SiyuanBlock: the block with all fields.
        """
        if not full:
            return SiyuanBlock(id=block_id, source=self)
        return SiyuanBlock(
            id=block_id, source=self, raw=await self._get_raw_block_by_id(block_id)
        )

    async def get_blocks_by_sql(
        self, cond: str, full: bool = True
    ) -> list[SiyuanBlock]:
        """Get a list of SiyuanBlock by sql.

        Args:
            cond (str): the conditions to apply, typically `where id = ''` or so.
            full (bool, optional): whether to fetch all the informations of the block. Defaults to True.

        Returns:
            list[SiyuanBlock]: result blocks
        """
        if not full:
            ret = await self.sql_query(f"SELECT id from BLOCKS {cond}")
            return [SiyuanBlock(id=x.id, source=self) for x in ret]
        ret = await self.sql_query(f"SELECT * from BLOCKS {cond}")
        return [
            SiyuanBlock(id=x["id"], source=self, raw=self._gen_block_by_sql_result(x))
            for x in ret
        ]

    def _gen_block_by_sql_result(self, result: dict) -> RawSiyuanBlock:
        # use block_fields filter to avoid compatibility issues.
        return RawSiyuanBlock(**{key: result[key] for key in block_fields})

    async def _get_raw_block_by_id(self, block_id: str) -> RawSiyuanBlock:
        """Generally, you should not use this function unless you know what you're doing. Get RawSiyuanBlock by block id.

        Args:
            block_id (str): the desired block id.

        Returns:
            RawSiyuanBlock: raw Siyuan Block, with only data fields defined.
        """
        ret = await self.sql_query(f"SELECT * from BLOCKS where ID = '{block_id}'")
        if type(ret) != list:
            raise exceptions.SiyuanApiTypeException(ret)
        if len(ret) == 0:
            raise exceptions.SiyuanNoResultException(ret)
        return self._gen_block_by_sql_result(ret[0])

    async def get_attrs_by_id(self, block_id: str) -> dict[str, str]:
        """Get attribute dictionary by block id.

        Args:
            block_id (str): target block.

        Returns:
            dict[str, str]: key-value dict, note that custom attributes starts with `custom-`
        """
        ret = await self._post("/api/attr/getBlockAttrs", id=block_id)
        if type(ret) != dict:
            raise exceptions.SiyuanApiTypeException
        return ret

    async def set_attrs_by_id(self, block_id: str, attrs: dict[str, str]) -> None:
        """Update the attributes of the block with given id. Won't delete attrs not given in the dict.

        Args:
            block_id (str): target block id
            attrs (dict[str, str]): block attrs dict to update
        """
        await self._post("/api/attr/setBlockAttrs", id=block_id, attrs=attrs)

    async def sql_query(self, sql: str) -> data_type:
        """Query SQL.

        Args:
            sql (str): the executed SQL string

        Returns:
            data_type: usually a list of dicts.
        """
        return await self._post(url="/api/query/sql", stmt=sql)

    async def delete_block_by_id(self, block_id: str) -> None:
        """Delete a block with given id.

        Args:
            block_id (str): target block id
        """
        await self._post("/api/block/deleteBlock", id=block_id)

    async def insert_block(
        self, data_type: DataType, data: str, previous_id: str
    ) -> SiyuanBlock:
        """Insert a block after the block with the given id.

        Args:
            data_type (DataType): markdown or dom
            data (str): data value
            previous_id (str): the block in front of the new block

        Raises:
            exceptions.SiyuanApiException: API Error

        Returns:
            SiyuanBlock: the new block, with id only.
        """
        ret = await self._post(
            "/api/block/insertBlock",
            dataType=data_type,
            data=data,
            previousID=previous_id,
        )
        if ret is None:
            raise exceptions.SiyuanApiException((self, ret))
        return await self.get_block_by_id(ret[0]["doOperations"][0]["id"], full=False)

    async def export_md_content_by_id(self, block_id: str) -> str:
        """Export Markdown Content by id.

        Args:
            block_id (str): blockid, only document block is supported.

        Returns:
            str: markdown
        """
        return cast(dict, await self._post("/api/export/exportMdContent", id=block_id))[
            "content"
        ]


@dataclass
class SiyuanResponse:
    """Response class for siyuan."""

    code: int
    msg: str
    data: data_type = None


class BlockAttr:
    """Block Attribute Class."""

    def __init__(self, block: SiyuanBlock):
        """Init.

        Args:
            block (SiyuanBlock): block that this BlockAttr adhere to.
        """
        self.block = block
        self.cached = False

    async def _cache_attr(self) -> None:
        self.values = await self.block.source.get_attrs_by_id(self.block.id)
        self.cached = True

    async def ensure(self) -> None:
        """Ensure the attributes are cached."""
        if not self.cached:
            await self._cache_attr()

    async def get(self, name: str) -> str:
        """Get attribute value by name.

        Args:
            name (str): name of the attribute, remember to add `custom-`

        Returns:
            str: the value of the attribute, `` if none.
        """
        await self.ensure()
        return self.values.get(name, "")

    async def set(self, name: str, val: str) -> None:
        """Modify the attribute.

        Args:
            name (str): name of the attribute
            val (str): new value
        """
        await self.ensure()
        self.values[name] = val
        await self.block.source.set_attrs_by_id(self.block.id, {name: val})


class DataType(str, Enum):
    """DataType Enum, used when modifying block's content."""

    MARKDOWN = "markdown"
    DOM = "dom"


class SiyuanBlock:
    """Block Class for Siyuan. An additional application layer is applied. For raw data, consider RawSiyuanBlock."""

    def __init__(self, id: str, source: Siyuan, raw: RawSiyuanBlock | None = None):
        """Init a SiyuanBlock.

        Args:
            id (str): id of the block.
            source (Siyuan): source of the block.
            raw (RawSiyuanBlock | None, optional): raw block data. Defaults to None.
        """
        self.id = id
        self.source = source
        self.raw = raw
        self.attrs = BlockAttr(self)

    async def pull(self) -> None:
        """Pull from Siyuan API. Refreshing everything."""
        self.raw = await self.source._get_raw_block_by_id(self.id)
        await self.attrs._cache_attr()

    async def ensure(self) -> None:
        """Ensure the information of the current block is cached."""
        if self.raw is None:
            self.raw = await self.source._get_raw_block_by_id(self.id)
        await self.attrs.ensure()

    def asdict(self) -> dict:
        """Parse Siyuan Block to a dict containing all its informations.

        Returns:
            dict: that block.
        """
        return dataclasses.asdict(self.raw)

    def __getattr__(self, __name: str) -> Any:
        """Expose RawSiyuanBlock's attributes.

        Args:
            __name (str): attribute name

        Returns:
            Any: result
        """
        if self.raw is not None and __name in self.raw.__slots__:  # type: ignore
            return self.raw.__getattribute__(__name)

    async def delete(self) -> None:
        """Delete this block. Mind that there is a delay between the execution and the result being synced into API database."""
        await self.source.delete_block_by_id(self.id)

    async def insert(self, data_type: DataType, data: str) -> SiyuanBlock:
        """Insert a block after this block.

        Args:
            data_type (DataType): markdown or dom
            data (str): the desired data

        Returns:
            SiyuanBlock: newly inserted block, only `id` is given.
        """
        return await self.source.insert_block(data_type, data, self.id)

    async def export(self) -> str:
        """Export the document current block belongs to in markdown format.

        Returns:
            str: markdown export output
        """
        return await self.source.export_md_content_by_id(self.id)


block_fields = (
    "id",
    "alias",
    "box",
    "content",
    "created",
    "updated",
    "fcontent",
    "hash",
    "hpath",
    "length",
    "markdown",
    "memo",
    "name",
    "parent_id",
    "path",
    "root_id",
    "sort",
    "subtype",
    "type",
    "ial",
)


@dataclass(frozen=True)
class RawSiyuanBlock:
    """Raw Siyuan Block, presents the raw output of the Siyuan API."""

    __slots__ = block_fields

    id: str
    alias: str
    box: str
    content: str
    created: str
    updated: str
    fcontent: str
    hash: str
    hpath: str
    length: int
    markdown: str
    memo: str
    name: str
    parent_id: str
    path: str
    root_id: str
    sort: int
    subtype: str
    type: str
    ial: str
