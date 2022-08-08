from __future__ import annotations

import asyncio
import random

import pytest
import siyuanhelper.api

from siyuanhelper import exceptions
from siyuanhelper.api import DataType, RawSiyuanBlock, Siyuan, SiyuanBlock


@pytest.fixture
async def siyuan():
    my_siyuan = Siyuan(token="mhfj23ilil7bafg0")
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
            "tag": "",
        }

    @pytest.mark.asyncio_cooperative
    async def test_get_raw_block_by_id(self, siyuan: Siyuan):
        ret = await siyuan._get_raw_block_by_id("20220501134149-qexauwn")
        assert ret.id == "20220501134149-qexauwn"

    @pytest.mark.asyncio_cooperative
    async def test_get_attrs_by_id(self, siyuan: Siyuan):
        ret = await siyuan.get_attrs_by_id("20220501214630-ql8hhto")
        assert ret["custom-testattr"] == "value"

    @pytest.mark.benchmark
    @pytest.mark.longrun
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
            "tag": "",
        }

        def init_raw():
            RawSiyuanBlock(**ret)

        benchmark(init_raw)

    @pytest.mark.benchmark
    @pytest.mark.longrun
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
            "tag": "",
        }

        def init_filtered_raw():
            RawSiyuanBlock(**{key: ret[key] for key in siyuanhelper.api.block_fields})

        benchmark(init_filtered_raw)

    @pytest.mark.asyncio_cooperative
    async def test_auth(self):
        new_siyuan = Siyuan(token="invalid")
        with pytest.raises(exceptions.SiyuanAuthFailedException):
            await new_siyuan.sql_query("select * from blocks limit 0")

    @pytest.mark.asyncio_cooperative
    async def test_get_blocks_by_sql(self, siyuan: Siyuan):
        blocks: list[SiyuanBlock] = await siyuan.get_blocks_by_sql(
            "WHERE (id='20220501134149-qexauwn') or (id='20220501134156-v82db6e')"
        )
        assert (
            blocks[0].id == "20220501134149-qexauwn"
            and blocks[1].id == "20220501134156-v82db6e"
        ) or (
            blocks[1].id == "20220501134149-qexauwn"
            and blocks[0].id == "20220501134156-v82db6e"
        )

    @pytest.mark.asyncio_cooperative
    async def test_create_remove_document(self, siyuan: Siyuan):
        block = await siyuan.create_doc_with_md(
            "20220501134144-oqwd5yh", "/testfolder/testdoc", "test content\n\ntest2"
        )
        await asyncio.sleep(4)
        await block.ensure()
        content = await block.export()
        assert content == "test content\n\ntest2\n"
        await siyuan.remove_doc("20220501134144-oqwd5yh", block.path)
        await asyncio.sleep(4)
        with pytest.raises(exceptions.SiyuanApiException):
            await siyuan.get_hpath_by_id(block.id)

    @pytest.mark.asyncio_cooperative
    async def test_get_doc_path_by_id(self, siyuan: Siyuan):
        doc = await siyuan.get_doc_path_by_id("20220728223910-bkzr0sb")
        assert doc["box"] == "20220501134144-oqwd5yh"
        assert doc["path"] == "/20220728220136-wi8vton/20220728223910-bkzr0sb.sy"

    @pytest.mark.asyncio_cooperative
    async def test_get_hpath_by_id(self, siyuan: Siyuan):
        hpath = await siyuan.get_hpath_by_id("20220728223630-00qikyt")
        assert hpath == "/testfolder/testhpathbyid"

    @pytest.mark.asyncio_cooperative
    async def test_get_hpath_by_path(self, siyuan: Siyuan):
        hpath = await siyuan.get_hpath_by_path(
            "20220501134144-oqwd5yh",
            "/20220728220136-wi8vton/20220728223910-bkzr0sb.sy",
        )
        assert hpath == "/testfolder/hpath by path"

    @pytest.mark.asyncio_cooperative
    async def test_rename_doc(self, siyuan: Siyuan):
        doc = await siyuan.get_doc_path_by_id("20220808150136-2h756le")
        rd = str(random.randint(0, 100))
        await siyuan.rename_doc(doc["box"], doc["path"], "renamed" + rd)
        await asyncio.sleep(5)
        content = await siyuan.sql_query(
            f"select content from blocks where path='{doc['path']}'"
        )
        assert content[0]["content"] == "renamed" + rd


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

    @pytest.mark.longrun
    @pytest.mark.asyncio_cooperative
    async def test_insert_delete(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501134149-qexauwn")
        inserted = await ret.insert(DataType.MARKDOWN, "test insert")
        await asyncio.sleep(5)
        await inserted.ensure()
        assert inserted.markdown == "test insert"
        await inserted.delete()
        await asyncio.sleep(5)
        with pytest.raises(exceptions.SiyuanNoResultException):
            await siyuan.get_block_by_id(inserted.id)

    @pytest.mark.asyncio_cooperative
    async def test_export(self, siyuan: Siyuan):
        block = await siyuan.get_block_by_id("20220507183011-c3lt1k8")
        ret = await block.export()
        assert (
            ret
            == "**content1**\n\n*content2*\n\n## Header 2\n\ncontent 3\n\ncontent 4\n"
        )

    @pytest.mark.asyncio_cooperative
    async def test_tags(self, siyuan: Siyuan):
        block = await siyuan.get_block_by_id("20220501231358-j4mnnht")
        assert (await block.tags) == ("tag", "tag2")
        assert (await block.tags) == ("tag", "tag2")  # test cache


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
        assert (await ret.attrs.values)["custom-testattr"] == "value"
        assert (await ret.attrs.values)["custom-testattr"] == "value"

    @pytest.mark.asyncio_cooperative
    async def test_attr_get_default(self, siyuan: Siyuan):
        ret = await siyuan.get_block_by_id("20220501214630-ql8hhto")
        assert await ret.attrs.get("custom-testattr-none") == ""
        assert await ret.attrs.get("custom-testattr-none", "default") == "default"
