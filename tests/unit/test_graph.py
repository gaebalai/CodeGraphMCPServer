"""
Graph Unit Tests
================

그래프 엔진의 단위 테스트.
"""

from pathlib import Path

import pytest

from codegraph_mcp.core.graph import (
    GraphEngine,
    GraphQuery,
    GraphStatistics,
    QueryResult,
)
from codegraph_mcp.core.parser import (
    Entity,
    EntityType,
    Location,
    Relation,
    RelationType,
)


def make_entity(
    name: str,
    entity_type: EntityType = EntityType.FUNCTION,
    file_path: str = "/test/file.py",
    line: int = 1,
) -> Entity:
    """Helper to create test entities."""
    return Entity(
        id=f"{file_path}::{name}::{line}",
        type=entity_type,
        name=name,
        qualified_name=f"{file_path}::{name}",
        location=Location(
            file_path=Path(file_path),
            start_line=line,
            start_column=0,
            end_line=line + 10,
            end_column=0,
        ),
    )


def make_relation(
    source_name: str,
    target_name: str,
    rel_type: RelationType = RelationType.CALLS,
) -> Relation:
    """Helper to create test relations."""
    return Relation(
        source_id=f"/test/file.py::{source_name}::1",
        target_id=f"/test/file.py::{target_name}::1",
        type=rel_type,
    )


class TestGraphEngine:
    """GraphEngine 테스트"""

    @pytest.mark.asyncio
    async def test_graph_initialization(self, temp_dir):
        """그래프 엔진 초기화 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        assert engine.db_path.exists()

        await engine.close()

    @pytest.mark.asyncio
    async def test_add_and_get_entity(self, temp_dir):
        """엔티티 추가와 검색 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        entity = make_entity("test_func")
        await engine.add_entity(entity)

        retrieved = await engine.get_entity(entity.id)
        assert retrieved is not None
        assert retrieved.name == "test_func"
        assert retrieved.type == EntityType.FUNCTION

        await engine.close()

    @pytest.mark.asyncio
    async def test_add_relation(self, temp_dir):
        """관계 추가 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        # Add entities first
        e1 = make_entity("func_a")
        e2 = make_entity("func_b", line=20)
        await engine.add_entity(e1)
        await engine.add_entity(e2)

        # Add relation
        rel = Relation(
            source_id=e1.id,
            target_id=e2.id,
            type=RelationType.CALLS,
        )
        await engine.add_relation(rel)

        # Verify via callees
        callees = await engine.find_callees(e1.id)
        assert len(callees) == 1
        assert callees[0].name == "func_b"

        await engine.close()

    @pytest.mark.asyncio
    async def test_find_callers(self, temp_dir):
        """호출자 검색 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        # func_a -> func_b, func_c -> func_b
        e_a = make_entity("func_a", line=1)
        e_b = make_entity("func_b", line=20)
        e_c = make_entity("func_c", line=40)

        await engine.add_entity(e_a)
        await engine.add_entity(e_b)
        await engine.add_entity(e_c)

        await engine.add_relation(Relation(
            source_id=e_a.id, target_id=e_b.id, type=RelationType.CALLS
        ))
        await engine.add_relation(Relation(
            source_id=e_c.id, target_id=e_b.id, type=RelationType.CALLS
        ))

        callers = await engine.find_callers(e_b.id)
        assert len(callers) == 2
        caller_names = {c.name for c in callers}
        assert "func_a" in caller_names
        assert "func_c" in caller_names

        await engine.close()

    @pytest.mark.asyncio
    async def test_query_by_name(self, temp_dir):
        """이름으로 쿼리 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        await engine.add_entity(make_entity("get_user", line=1))
        await engine.add_entity(make_entity("get_order", line=20))
        await engine.add_entity(make_entity("create_user", line=40))

        # Search for "get"
        result = await engine.query(GraphQuery(query="get"))
        assert len(result.entities) == 2

        # Search for "user"
        result = await engine.query(GraphQuery(query="user"))
        assert len(result.entities) == 2

        await engine.close()

    @pytest.mark.asyncio
    async def test_query_by_type(self, temp_dir):
        """타입으로 쿼리 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        await engine.add_entity(make_entity(
            "MyClass", EntityType.CLASS, line=1
        ))
        await engine.add_entity(make_entity(
            "my_func", EntityType.FUNCTION, line=20
        ))
        await engine.add_entity(make_entity(
            "OtherClass", EntityType.CLASS, line=40
        ))

        result = await engine.query(GraphQuery(
            query="",
            entity_types=[EntityType.CLASS],
        ))
        assert len(result.entities) == 2
        for e in result.entities:
            assert e.type == EntityType.CLASS

        await engine.close()

    @pytest.mark.asyncio
    async def test_get_statistics(self, temp_dir):
        """통계 정보 획득 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        await engine.add_entity(make_entity("func1", EntityType.FUNCTION))
        await engine.add_entity(make_entity("func2", EntityType.FUNCTION, line=20))
        await engine.add_entity(make_entity("MyClass", EntityType.CLASS, line=40))

        await engine.add_relation(Relation(
            source_id="/test/file.py::func1::1",
            target_id="/test/file.py::func2::20",
            type=RelationType.CALLS,
        ))

        stats = await engine.get_statistics()
        assert stats.entity_count == 3
        assert stats.relation_count == 1
        assert stats.entities_by_type["function"] == 2
        assert stats.entities_by_type["class"] == 1

        await engine.close()

    @pytest.mark.asyncio
    async def test_search_by_name(self, temp_dir):
        """이름 패턴 검색 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        await engine.add_entity(make_entity("UserService", EntityType.CLASS))
        await engine.add_entity(make_entity("OrderService", EntityType.CLASS, line=50))
        await engine.add_entity(make_entity("get_user", EntityType.FUNCTION, line=100))

        results = await engine.search_by_name("Service")
        assert len(results) == 2

        results = await engine.search_by_name(
            "Service",
            entity_types=[EntityType.CLASS],
        )
        assert len(results) == 2

        await engine.close()

    @pytest.mark.asyncio
    async def test_delete_file_entities(self, temp_dir):
        """파일 엔티티 삭제 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        await engine.add_entity(make_entity("func1", file_path="/test/a.py"))
        await engine.add_entity(make_entity("func2", file_path="/test/a.py", line=20))
        await engine.add_entity(make_entity("func3", file_path="/test/b.py"))

        deleted = await engine.delete_file_entities(Path("/test/a.py"))
        assert deleted == 2

        stats = await engine.get_statistics()
        assert stats.entity_count == 1

        await engine.close()

    @pytest.mark.asyncio
    async def test_clear(self, temp_dir):
        """클리어 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        await engine.add_entity(make_entity("func1"))
        await engine.add_entity(make_entity("func2", line=20))

        await engine.clear()

        stats = await engine.get_statistics()
        assert stats.entity_count == 0

        await engine.close()


class TestGraphQuery:
    """GraphQuery 테스트"""

    def test_query_defaults(self):
        """쿼리 기본값 테스트"""
        query = GraphQuery(query="test")
        assert query.max_depth == 3
        assert query.max_results == 100
        assert query.entity_types is None

    def test_query_with_filters(self):
        """필터 쿼리 테스트"""
        query = GraphQuery(
            query="service",
            entity_types=[EntityType.CLASS],
            file_patterns=["*.py"],
            max_results=10,
        )
        assert query.entity_types == [EntityType.CLASS]
        assert query.file_patterns == ["*.py"]
        assert query.max_results == 10


class TestQueryResult:
    """QueryResult 테스트"""

    def test_empty_result(self):
        """빈 결과 테스트"""
        result = QueryResult()
        assert len(result.entities) == 0
        assert len(result.relations) == 0

    def test_to_dict(self):
        """딕셔너리 변환 테스트"""
        entity = make_entity("test_func")
        result = QueryResult(entities=[entity])

        d = result.to_dict()
        assert "entities" in d
        assert len(d["entities"]) == 1
        assert d["entities"][0]["name"] == "test_func"

    def test_str_representation(self):
        """문자열 표현 테스트"""
        entity = make_entity("test_func")
        result = QueryResult(entities=[entity])

        s = str(result)
        assert "Found 1 entities" in s
        assert "test_func" in s


class TestGraphStatistics:
    """GraphStatistics 테스트"""

    def test_default_values(self):
        """기본값 테스트"""
        stats = GraphStatistics()
        assert stats.entity_count == 0
        assert stats.relation_count == 0
        assert stats.community_count == 0


class TestPartialEntityIdMatching:
    """Entity ID 부분 일치 기능 테스트"""

    @pytest.mark.asyncio
    async def test_resolve_exact_match(self, temp_dir):
        """완전 일치로 엔티티 해결 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        entity = make_entity("my_function")
        await engine.add_entity(entity)

        # 완전 일치
        resolved = await engine.resolve_entity_id(entity.id)
        assert resolved == entity.id

        await engine.close()

    @pytest.mark.asyncio
    async def test_resolve_by_name(self, temp_dir):
        """이름으로 엔티티 해결 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        entity = make_entity("unique_function")
        await engine.add_entity(entity)

        # 名前のみで解決
        resolved = await engine.resolve_entity_id("unique_function")
        assert resolved == entity.id

        await engine.close()

    @pytest.mark.asyncio
    async def test_resolve_ambiguous_name(self, temp_dir):
        """모호한 이름으로 엔티티 해결 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        # 동일한 이름의 엔티티를 여러 개 추가
        e1 = make_entity("common_func", file_path="/test/a.py")
        e2 = make_entity("common_func", file_path="/test/b.py")
        await engine.add_entity(e1)
        await engine.add_entity(e2)

        # 모호한 이름은 None을 반환
        resolved = await engine.resolve_entity_id("common_func")
        assert resolved is None

        await engine.close()

    @pytest.mark.asyncio
    async def test_resolve_by_file_pattern(self, temp_dir):
        """파일 패턴으로 엔티티 해결 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        e1 = make_entity("my_func", file_path="/test/module/service.py")
        e2 = make_entity("my_func", file_path="/test/module/utils.py")
        await engine.add_entity(e1)
        await engine.add_entity(e2)

        # 파일::이름 패턴으로 해결
        resolved = await engine.resolve_entity_id("service.py::my_func")
        assert resolved == e1.id

        resolved = await engine.resolve_entity_id("utils.py::my_func")
        assert resolved == e2.id

        await engine.close()

    @pytest.mark.asyncio
    async def test_search_entities(self, temp_dir):
        """엔티티 검색 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        e1 = make_entity("test_function_a")
        e2 = make_entity("test_function_b", line=20)
        e3 = make_entity("other_method", line=30)
        await engine.add_entity(e1)
        await engine.add_entity(e2)
        await engine.add_entity(e3)

        # パターン検索
        results = await engine.search_entities("test_function")
        assert len(results) == 2
        names = [e.name for e in results]
        assert "test_function_a" in names
        assert "test_function_b" in names

        await engine.close()

    @pytest.mark.asyncio
    async def test_find_dependencies_with_partial_id(self, temp_dir):
        """부분 ID로 의존성 검색 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        # 엔티티 추가
        e1 = make_entity("unique_source")
        e2 = make_entity("target_func", line=20)
        await engine.add_entity(e1)
        await engine.add_entity(e2)

        # 관계 추가
        rel = Relation(
            source_id=e1.id,
            target_id=e2.id,
            type=RelationType.CALLS,
        )
        await engine.add_relation(rel)

        # 부분 ID로 의존성 검색
        result = await engine.find_dependencies("unique_source", depth=1)
        assert len(result.entities) > 0

        await engine.close()

    @pytest.mark.asyncio
    async def test_find_callers_with_partial_id(self, temp_dir):
        """부분 ID로 호출자 검색 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        e1 = make_entity("caller_func")
        e2 = make_entity("unique_callee", line=20)
        await engine.add_entity(e1)
        await engine.add_entity(e2)

        rel = Relation(
            source_id=e1.id,
            target_id=e2.id,
            type=RelationType.CALLS,
        )
        await engine.add_relation(rel)

        # 부분 ID로 호출자 검색
        callers = await engine.find_callers("unique_callee")
        assert len(callers) == 1
        assert callers[0].name == "caller_func"

        await engine.close()

    @pytest.mark.asyncio
    async def test_find_callees_with_partial_id(self, temp_dir):
        """부분 ID로 호출자 검색 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        e1 = make_entity("unique_caller")
        e2 = make_entity("callee_func", line=20)
        await engine.add_entity(e1)
        await engine.add_entity(e2)

        rel = Relation(
            source_id=e1.id,
            target_id=e2.id,
            type=RelationType.CALLS,
        )
        await engine.add_relation(rel)

        # 부분 ID로 호출자 검색
        callees = await engine.find_callees("unique_caller")
        assert len(callees) == 1
        assert callees[0].name == "callee_func"

        await engine.close()

    @pytest.mark.asyncio
    async def test_nonexistent_entity_returns_empty(self, temp_dir):
        """존재하지 않는 엔티티에 대한 빈 결과 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        # 존재하지 않는 엔티티
        resolved = await engine.resolve_entity_id("nonexistent")
        assert resolved is None

        callers = await engine.find_callers("nonexistent")
        assert callers == []

        callees = await engine.find_callees("nonexistent")
        assert callees == []

        result = await engine.find_dependencies("nonexistent")
        assert result.entities == []
        assert result.relations == []

        await engine.close()


class TestQueryScoring:
    """쿼리 스코어링 기능 테스트"""

    @pytest.mark.asyncio
    async def test_exact_name_match_highest_score(self, temp_dir):
        """완전 일치가 가장 높은 스코어를 가지는 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        # 다른 이름의 엔티티 추가
        e1 = make_entity("calculate")
        e2 = make_entity("calculate_sum", line=20)
        e3 = make_entity("recalculate", line=30)
        await engine.add_entity(e1)
        await engine.add_entity(e2)
        await engine.add_entity(e3)

        # 쿼리 실행
        result = await engine.query(GraphQuery(query="calculate"))

        # 결과에 스코어가 포함되어 있는지 확인
        assert len(result.scores) > 0

        # 완전 일치 엔티티가 가장 높은 스코어를 가지는지 확인
        assert e1.id in result.scores
        assert result.scores[e1.id] >= result.scores.get(e2.id, 0)
        assert result.scores[e1.id] >= result.scores.get(e3.id, 0)

        await engine.close()

    @pytest.mark.asyncio
    async def test_score_in_to_dict_output(self, temp_dir):
        """to_dict 출력에 스코어가 포함되어 있는지 확인"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        e1 = make_entity("my_function")
        await engine.add_entity(e1)

        result = await engine.query(GraphQuery(query="my_function"))
        d = result.to_dict()

        # 엔티티에 스코어가 포함되어 있는지 확인
        assert len(d["entities"]) > 0
        assert "score" in d["entities"][0]

        await engine.close()

    @pytest.mark.asyncio
    async def test_query_with_include_related(self, temp_dir):
        """관련 엔티티를 포함하는 쿼리 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        # 엔티티와 관계를 추가
        e1 = make_entity("main_func")
        e2 = make_entity("helper_func", line=20)
        await engine.add_entity(e1)
        await engine.add_entity(e2)

        rel = Relation(
            source_id=e1.id,
            target_id=e2.id,
            type=RelationType.CALLS,
        )
        await engine.add_relation(rel)

        # include_related=True로 쿼리
        query = GraphQuery(
            query="main_func",
            include_related=True,
        )
        result = await engine.query(query)

        # 관련 엔티티가 포함될 수 있는지 확인
        assert len(result.entities) >= 1
        assert "include_related" in result.metadata

        await engine.close()

    @pytest.mark.asyncio
    async def test_query_with_entity_type_filter(self, temp_dir):
        """엔티티 타입 필터 쿼리 테스트"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        # 다른 타입의 엔티티 추가
        e1 = make_entity("MyClass", entity_type=EntityType.CLASS)
        e2 = make_entity("my_function", entity_type=EntityType.FUNCTION, line=20)
        await engine.add_entity(e1)
        await engine.add_entity(e2)

        # CLASS만 필터링
        query = GraphQuery(
            query="My",
            entity_types=[EntityType.CLASS],
        )
        result = await engine.query(query)

        # CLASS만 반환되는지 확인
        for entity in result.entities:
            assert entity.type == EntityType.CLASS

        await engine.close()


class TestCommunityIntegration:
    """커뮤니티 검색 통합 테스트"""

    @pytest.mark.asyncio
    async def test_community_result_in_query(self, temp_dir):
        """쿼리 결과에 커뮤니티 정보가 포함되어 있는지 확인"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        e1 = make_entity("test_func")
        await engine.add_entity(e1)

        # 커뮤니티 ID를 수동으로 설정
        await engine._connection.execute(
            "UPDATE entities SET community_id = ? WHERE id = ?",
            (1, e1.id),
        )
        await engine._connection.commit()

        # 쿼리 실행
        query = GraphQuery(
            query="test_func",
            include_community=True,
        )
        result = await engine.query(query)

        # 커뮤니티 정보가 포함되어 있는지 확인
        assert e1.id in result.communities
        assert result.communities[e1.id] == 1

        await engine.close()

    @pytest.mark.asyncio
    async def test_community_in_to_dict_output(self, temp_dir):
        """to_dict 출력에 커뮤니티 ID가 포함되어 있는지 확인"""
        engine = GraphEngine(temp_dir)
        await engine.initialize()

        e1 = make_entity("community_func")
        await engine.add_entity(e1)

        # 커뮤니티 ID를 설정
        await engine._connection.execute(
            "UPDATE entities SET community_id = ? WHERE id = ?",
            (5, e1.id),
        )
        await engine._connection.commit()

        # 쿼리 실행
        query = GraphQuery(
            query="community_func",
            include_community=True,
        )
        result = await engine.query(query)
        d = result.to_dict()

        # 엔티티에 community_id가 포함되어 있는지 확인
        assert len(d["entities"]) > 0
        assert "community_id" in d["entities"][0]
        assert d["entities"][0]["community_id"] == 5

        await engine.close()
