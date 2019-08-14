from elasticmagic.compiler import get_compiler_by_es_version

from ...cluster import BaseCluster
from .index import AsyncIndex
from .search import AsyncSearchQuery


class AsyncCluster(BaseCluster):
    _index_cls = AsyncIndex
    _search_query_cls = AsyncSearchQuery

    async def _do_request(self, compiler, *args, **kwargs):
        compiled_query = compiler(*args, **kwargs)
        api_method = compiled_query.api_method(self._client)
        if compiled_query.body is None:
            return compiled_query.process_result(
                await api_method(**compiled_query.params)
            )
        return compiled_query.process_result(
            await api_method(
                body=compiled_query.body, **compiled_query.params
            )
        )

    async def get_es_version(self):
        if not self._es_version:
            self._es_version = self._es_version_result(
                await self._client.info()
            )
        return self._es_version

    async def get_compiler(self):
        if self._compiler:
            return self._compiler
        else:
            return get_compiler_by_es_version(await self.get_es_version())

    async def get(
            self, doc_or_id, index=None, doc_cls=None, doc_type=None,
            source=None, realtime=None, routing=None, parent=None,
            preference=None, refresh=None, version=None, version_type=None,
            **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_get,
            doc_or_id, **self._get_params(locals())
        )

    async def multi_get(
            self, docs_or_ids, index=None, doc_cls=None, doc_type=None,
            source=None, parent=None, routing=None, preference=None,
            realtime=None, refresh=None, **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_multi_get,
            docs_or_ids, **self._multi_get_params(locals())
        )

    mget = multi_get

    async def search(
            self, q, index=None, doc_type=None, routing=None, preference=None,
            timeout=None, search_type=None, query_cache=None,
            terminate_after=None, scroll=None, **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_search_query,
            q, **self._search_params(locals())
        )

    async def count(
            self, q=None, index=None, doc_type=None, routing=None,
            preference=None, **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_count_query,
            q, **self._search_params(locals())
        )

    async def exists(
            self, q=None, index=None, doc_type=None, refresh=None,
            routing=None, **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_exists_query,
            q, **self._search_params(locals())
        )

    async def scroll(
            self, scroll_id, scroll, doc_cls=None, instance_mapper=None,
            **kwargs
    ):
        doc_cls, instance_mapper, params = self._scroll_params(locals())
        return self._scroll_result(
            doc_cls,
            instance_mapper,
            await self._client.scroll(**params)
        )

    async def clear_scroll(self, scroll_id, **kwargs):
        params = self._clear_scroll_params(locals())
        return self._clear_scroll_result(
            await self._client.clear_scroll(**params)
        )

    async def multi_search(
            self, queries, index=None, doc_type=None,
            routing=None, preference=None, search_type=None,
            raise_on_error=None, **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_multi_search,
            queries, **self._multi_search_params(locals())
        )

    msearch = multi_search

    async def put_mapping(
            self, doc_cls_or_mapping, index, doc_type=None,
            allow_no_indices=None, expand_wildcards=None,
            ignore_conflicts=None, ignore_unavailable=None,
            master_timeout=None, timeout=None, **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_put_mapping,
            doc_cls_or_mapping, **self._put_mapping_params(locals())
        )

    async def add(
            self, docs, index=None, doc_type=None, refresh=None,
            timeout=None, consistency=None, replication=None, **kwargs
    ):
        actions, params = self._add_params(locals())
        return await self.bulk(actions, **params)

    async def delete(
            self, doc_or_id, index, doc_cls=None, doc_type=None,
            timeout=None, consistency=None, replication=None,
            parent=None, routing=None, refresh=None, version=None,
            version_type=None,
            **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_delete,
            doc_or_id, **self._delete_params(locals())
        )

    async def delete_by_query(
            self, q, index=None, doc_type=None,
            timeout=None, consistency=None, replication=None, routing=None,
            **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_delete_by_query,
            q, **self._search_params(locals())
        )

    async def bulk(
            self, actions, index=None, doc_type=None, refresh=None,
            timeout=None, consistency=None, replication=None, **kwargs
    ):
        return await self._do_request(
            (await self.get_compiler()).compiled_bulk,
            actions, **self._bulk_params(locals())
        )

    async def refresh(self, index=None, **kwargs):
        params = self._refresh_params(locals())
        return self._refresh_result(
            await self._client.indices.refresh(**params)
        )

    async def flush(self, index=None, **kwargs):
        params = self._flush_params(locals())
        return self._flush_result(
            await self._client.indices.flush(**params)
        )
