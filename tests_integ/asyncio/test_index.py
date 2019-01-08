import pytest

from elasticmagic.search import SearchQuery

from .conftest import Car


@pytest.mark.asyncio
async def test_get(es_index, docs):
    doc = await es_index.get(1, doc_cls=Car)
    assert doc.name == 'Lightning McQueen'
    assert doc._id == '1'
    assert doc._index == es_index.get_name()
    assert doc._score is None

    doc = await es_index.get(2, doc_cls=Car)
    assert doc.name == 'Sally Carerra'
    assert doc._id == '2'
    assert doc._index == es_index.get_name()
    assert doc._score is None


@pytest.mark.asyncio
async def test_multi_get(es_index, docs):
    fetched_docs = await es_index.multi_get(docs)

    doc = fetched_docs[0]
    assert doc.name == 'Lightning McQueen'
    assert doc._id == '1'
    assert doc._index == es_index.get_name()
    assert doc._score is None

    doc = fetched_docs[1]
    assert doc.name == 'Sally Carerra'
    assert doc._id == '2'
    assert doc._index == es_index.get_name()
    assert doc._score is None


@pytest.mark.asyncio
async def test_search(es_index, docs):
    res = await es_index.search(
        SearchQuery(Car.name.match("Lightning"))
    )

    assert res.total == 1
    assert len(res.hits) == 1
    doc = res.hits[0]
    assert doc.name == 'Lightning McQueen'
    assert doc._id == '1'
    assert doc._index == es_index.get_name()
    assert doc._score > 0
    assert doc._score == res.max_score


@pytest.mark.asyncio
async def test_count(es_index, docs):
    res = await es_index.count(
        SearchQuery(Car.name.match("Lightning"))
    )

    assert res.count == 1


@pytest.mark.asyncio
async def test_scroll(es_index, docs):
    search_res = await es_index.search(
        SearchQuery(), scroll='1m',
    )

    assert search_res.total == 2
    assert len(search_res.hits) == 2
    assert search_res.scroll_id is not None

    scroll_res = await es_index.scroll(search_res.scroll_id, scroll='1m')

    assert scroll_res.total == 2
    assert len(scroll_res.hits) == 0

    clear_scroll_res = await es_index.clear_scroll(scroll_res.scroll_id)

    assert clear_scroll_res.succeeded is True


@pytest.mark.asyncio
async def test_multi_search(es_index, docs):
    results = await es_index.multi_search([
        SearchQuery(Car.name.match("Lightning")),
        SearchQuery(Car.name.match("Sally")),
    ])

    assert len(results) == 2

    res = results[0]
    assert res.total == 1
    assert len(res.hits) == 1
    doc = res.hits[0]
    assert doc.name == 'Lightning McQueen'
    assert doc._id == '1'
    assert doc._index == es_index.get_name()
    assert doc._score > 0
    assert doc._score == res.max_score

    res = results[1]
    assert res.total == 1
    assert len(res.hits) == 1
    doc = res.hits[0]
    assert doc.name == 'Sally Carerra'
    assert doc._id == '2'
    assert doc._index == es_index.get_name()
    assert doc._score > 0
    assert doc._score == res.max_score


@pytest.mark.asyncio
async def test_delete(es_index, docs):
    res = await es_index.delete(1, doc_type='car')

    assert res.found is True


@pytest.mark.asyncio
async def test_delete_by_query(es_index, docs):
    res = await es_index.delete_by_query(
        SearchQuery(Car.name.match("Lightning"))
    )

    assert res


@pytest.mark.asyncio
async def test_flush(es_index, docs):
    await es_index.add([Car(name='Mater')])
    res = await es_index.flush()

    assert res
