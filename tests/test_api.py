from __future__ import annotations

import asyncio

import pytest
import siyuanhelper.api

from siyuanhelper import exceptions
from siyuanhelper.api import DataType, RawSiyuanBlock, Siyuan


@pytest.fixture
async def siyuan():
    my_siyuan = Siyuan()
    yield my_siyuan
    await my_siyuan.close()


class TestSiyuan:
    @pytest.mark.asyncio_cooperative
    async def test_get_block_by_id(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501134149-qexauwn")
        assert ret.asdict() == {
            "alias": "",
            "box": "20220501134144-oqwd5yh",
            "content": "test block",
            "created": "20220501134149",
            "fcontent": "",
            "hash": "6f7a904",
            "hpath": "/test",
            "ial": '{: id="20220501134149-qexauwn" updated="20220501134155"}',
            "id": "20220501134149-qexauwn",
            "length": 10,
            "markdown": "test block",
            "memo": "",
            "name": "",
            "parent_id": "20220501134149-eafvjwu",
            "path": "/20220501134149-eafvjwu.sy",
            "root_id": "20220501134149-eafvjwu",
            "sort": 10,
            "subtype": "",
            "type": "p",
            "updated": "20220501134155",
        }

    @pytest.mark.asyncio_cooperative
    async def test_get_raw_block_by_id(self, siyuan: Siyuan):
        ret = await siyuan.get_raw_block_by_id("20220501134149-qexauwn")
        assert ret.id == "20220501134149-qexauwn"

    @pytest.mark.asyncio_cooperative
    async def test_get_attrs_by_id(self, siyuan: Siyuan):
        ret = await siyuan.get_attrs_by_id("20220501214630-ql8hhto")
        assert ret["custom-testattr"] == "value"

    def test_benchmark_raw(self, benchmark):
        ret = {
            "alias": "",
            "box": "20220501134144-oqwd5yh",
            "content": "test block",
            "created": "20220501134149",
            "fcontent": "",
            "hash": "6f7a904",
            "hpath": "/test",
            "ial": '{: id="20220501134149-qexauwn" updated="20220501134155"}',
            "id": "20220501134149-qexauwn",
            "length": 10,
            "markdown": "test block",
            "memo": "",
            "name": "",
            "parent_id": "20220501134149-eafvjwu",
            "path": "/20220501134149-eafvjwu.sy",
            "root_id": "20220501134149-eafvjwu",
            "sort": 10,
            "subtype": "",
            "type": "p",
            "updated": "20220501134155",
        }

        def init_raw():
            RawSiyuanBlock(**ret)

        benchmark(init_raw)

    def test_benchmark_filtered_raw(self, benchmark):
        ret = {
            "alias": "",
            "box": "20220501134144-oqwd5yh",
            "content": "test block",
            "created": "20220501134149",
            "fcontent": "",
            "hash": "6f7a904",
            "hpath": "/test",
            "ial": '{: id="20220501134149-qexauwn" updated="20220501134155"}',
            "id": "20220501134149-qexauwn",
            "length": 10,
            "markdown": "test block",
            "memo": "",
            "name": "",
            "parent_id": "20220501134149-eafvjwu",
            "path": "/20220501134149-eafvjwu.sy",
            "root_id": "20220501134149-eafvjwu",
            "sort": 10,
            "subtype": "",
            "type": "p",
            "updated": "20220501134155",
        }

        def init_filtered_raw():
            RawSiyuanBlock(**{key: ret[key] for key in siyuanhelper.api.block_fields})

        benchmark(init_filtered_raw)


class TestSiyuanBlock:
    @pytest.mark.asyncio_cooperative
    async def test_proxy_getattr(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501134149-qexauwn")
        assert ret.hash == "6f7a904"

    @pytest.mark.asyncio_cooperative
    async def test_invalid_attr(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501134149-qexauwn")
        assert ret.test is None

    @pytest.mark.asyncio_cooperative
    async def test_pull(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501134149-qexauwn", full=False)
        assert ret.raw is None
        await ret.pull()
        assert ret.content == "test block"

    @pytest.mark.asyncio_cooperative
    async def test_insert_delete(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501134149-qexauwn")
        inserted = await ret.insert(DataType.MARKDOWN, "test insert")
        await asyncio.sleep(4)
        await inserted.ensure()
        assert inserted.markdown == "test insert"
        await inserted.delete()
        await asyncio.sleep(4)
        with pytest.raises(exceptions.SiyuanNoResultException):
            await siyuan.get_block_by_id(inserted.id)


class TestBlockAttr:
    @pytest.mark.asyncio_cooperative
    async def test_attr_get(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501214630-ql8hhto")
        assert await ret.attrs.get("custom-testattr") == "value"

    @pytest.mark.asyncio_cooperative
    async def test_attr_set(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501214630-ql8hhto")
        assert await ret.attrs.get("custom-testattr") == "value"
        assert await ret.attrs.get("custom-testattr2") == ""
        await ret.attrs.set("custom-testattr2", "value2")
        assert await ret.attrs.get("custom-testattr2") == "value2"
        await ret.attrs.set("custom-testattr2", "")
        assert await ret.attrs.get("custom-testattr2") == ""

    @pytest.mark.asyncio_cooperative
    async def test_cache(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501214630-ql8hhto")
        assert ret.attrs.cached is False
        await ret.attrs._cache_attr()
        assert ret.attrs.values["custom-testattr"] == "value"
