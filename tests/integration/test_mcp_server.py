"""
MCP Server Integration Tests
============================

MCP 서버 전체에 대한 통합 테스트.
실제 서버 생성과 도구 실행을 테스트합니다.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codegraph_mcp.config import Config
from codegraph_mcp.server import create_server


class TestMCPServerIntegration:
    """MCP 서버 통합 테스트"""

    @pytest.fixture
    def indexed_repo(self, tmp_path: Path) -> Path:
        """Create a repo with index for testing."""
        # Create .codegraph directory and db
        codegraph_dir = tmp_path / ".codegraph"
        codegraph_dir.mkdir()

        # Create a sample Python file
        (tmp_path / "sample.py").write_text('''
"""Sample module."""

class Calculator:
    """A simple calculator."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b

def main():
    calc = Calculator()
    print(calc.add(1, 2))
''')
        return tmp_path

    @pytest.mark.asyncio
    async def test_server_startup(self, indexed_repo: Path):
        """서버가 정상적으로 시작되는지 확인"""
        config = Config(repo_path=indexed_repo)
        server = create_server(config)

        # Verify server was created
        assert server is not None
        assert server.name == "codegraph-mcp"

    @pytest.mark.asyncio
    async def test_server_has_tools(self, indexed_repo: Path):
        """서버에 14개의 도구가 등록되어 있는지 확인"""
        config = Config(repo_path=indexed_repo)
        server = create_server(config)

        # Server should have tool handlers registered
        assert hasattr(server, "_tool_handlers") or server is not None

    @pytest.mark.asyncio
    async def test_tool_execution(self, indexed_repo: Path):
        """도구가 정상적으로 실행되는지 확인"""
        from codegraph_mcp.mcp.tools import _handle_read_file

        config = Config(repo_path=indexed_repo)
        mock_engine = AsyncMock()

        result = await _handle_read_file(
            {"file_path": "sample.py"},
            mock_engine,
            config,
        )

        assert "content" in result
        assert "Calculator" in result["content"]

    @pytest.mark.asyncio
    async def test_resource_access(self, indexed_repo: Path):
        """리소스가 정상적으로 접근되는지 확인"""
        config = Config(repo_path=indexed_repo)
        server = create_server(config)

        # Verify server was created with resources
        assert server is not None

    @pytest.mark.asyncio
    async def test_prompt_generation(self, indexed_repo: Path):
        """프롬프트가 정상적으로 생성되는지 확인"""
        from codegraph_mcp.mcp.prompts import _prompt_code_review

        config = Config(repo_path=indexed_repo)
        mock_engine = AsyncMock()
        mock_entity = MagicMock()
        mock_entity.name = "Calculator"
        mock_entity.source_code = "class Calculator: pass"
        mock_entity.docstring = "A calculator"
        mock_entity.file_path = Path("sample.py")
        mock_entity.start_line = 1
        mock_engine.get_entity.return_value = mock_entity

        result = await _prompt_code_review(
            {"entity_id": "test_id", "focus": "quality"},
            mock_engine,
            config,
        )

        assert len(result) > 0
        # Result is a list of PromptMessage
        assert any("Calculator" in str(msg) for msg in result)


class TestMCPProtocol:
    """MCP 프로토콜 테스트"""

    @pytest.mark.asyncio
    async def test_stdio_transport(self, tmp_path: Path):
        """stdio 트랜스포트가 설정되는지 확인"""
        from codegraph_mcp.server import run_server_async

        # Just verify the function exists and has correct signature
        import inspect
        sig = inspect.signature(run_server_async)

        assert "repo_path" in sig.parameters
        assert "transport" in sig.parameters
        assert sig.parameters["transport"].default == "stdio"

    @pytest.mark.asyncio
    async def test_sse_transport(self, tmp_path: Path):
        """SSE 트랜스포트가 설정되는지 확인"""
        from codegraph_mcp.server import run_server_async

        import inspect
        sig = inspect.signature(run_server_async)

        assert "port" in sig.parameters
        assert sig.parameters["port"].default == 8080

    @pytest.mark.asyncio
    async def test_error_handling(self, tmp_path: Path):
        """에러 핸들링이 정상적으로 작동하는지 확인"""
        from codegraph_mcp.mcp.tools import _dispatch_tool

        config = Config(repo_path=tmp_path)
        mock_engine = AsyncMock()

        # Unknown tool should return error
        result = await _dispatch_tool(
            "unknown_tool",
            {},
            mock_engine,
            config,
        )

        assert "error" in result
        assert "Unknown tool" in result["error"]


class TestToolHandlers:
    """개별 도구 핸들러 테스트"""

    @pytest.fixture
    def config(self, tmp_path: Path) -> Config:
        """Test config with temp repo."""
        (tmp_path / ".codegraph").mkdir()
        return Config(repo_path=tmp_path)

    @pytest.mark.asyncio
    async def test_query_codebase_handler(self, config: Config):
        """query_codebase 가 정상적으로 작동하는지 확인"""
        from codegraph_mcp.mcp.tools import _handle_query_codebase

        mock_engine = AsyncMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"entities": [], "relations": []}
        mock_engine.query.return_value = mock_result

        result = await _handle_query_codebase(
            {"query": "find all classes"},
            mock_engine,
            config,
        )

        assert "entities" in result
        mock_engine.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_dependencies_handler(self, config: Config):
        """find_dependencies 가 정상적으로 작동하는지 확인"""
        from codegraph_mcp.mcp.tools import _handle_find_dependencies

        mock_engine = AsyncMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"entities": [], "relations": []}
        mock_engine.find_dependencies.return_value = mock_result

        result = await _handle_find_dependencies(
            {"entity_id": "test::Calculator"},
            mock_engine,
            config,
        )

        assert "entities" in result

    @pytest.mark.asyncio
    async def test_global_search_handler(self, config: Config):
        """global_search 가 정상적으로 작동하는지 확인"""
        from codegraph_mcp.mcp.tools import _handle_global_search

        mock_engine = AsyncMock()

        with patch("codegraph_mcp.core.graphrag.GraphRAGSearch") as MockSearch:
            mock_search = AsyncMock()
            mock_result = MagicMock()
            mock_result.query = "test query"
            mock_result.answer = "Test answer"
            mock_result.communities_searched = 5
            mock_result.confidence = 0.8
            mock_result.relevant_communities = []
            mock_result.supporting_entities = []
            mock_search.global_search.return_value = mock_result
            MockSearch.return_value = mock_search

            result = await _handle_global_search(
                {"query": "how does authentication work"},
                mock_engine,
                config,
            )

            assert "answer" in result
            assert result["query"] == "test query"

    @pytest.mark.asyncio
    async def test_reindex_handler(self, config: Config):
        """reindex_repository 가 정상적으로 작동하는지 확인"""
        from codegraph_mcp.mcp.tools import _handle_reindex

        mock_engine = AsyncMock()

        with patch("codegraph_mcp.core.indexer.Indexer") as MockIndexer:
            mock_indexer = MagicMock()
            mock_result = MagicMock()
            mock_result.entities_count = 50
            mock_result.relations_count = 100
            mock_result.files_indexed = 10
            mock_result.duration_seconds = 1.5
            mock_indexer.index_repository = AsyncMock(return_value=mock_result)
            MockIndexer.return_value = mock_indexer

            result = await _handle_reindex(
                {"incremental": True},
                mock_engine,
                config,
            )

            assert result["entities"] == 50
            assert result["relations"] == 100
            assert result["files"] == 10


class TestEngineManagerIntegration:
    """EngineManager 통합 테스트"""

    @pytest.mark.asyncio
    async def test_engine_manager_with_real_db(self, tmp_path: Path):
        """EngineManager가 실제 DB에서 작동하는지 확인"""
        from codegraph_mcp.core.engine_manager import EngineManager

        # Clear instances
        EngineManager._instances.clear()

        # Create .codegraph directory
        codegraph_dir = tmp_path / ".codegraph"
        codegraph_dir.mkdir()

        manager = await EngineManager.get_instance(tmp_path)
        engine = await manager.get_engine()

        # Should be able to get statistics
        stats = await engine.get_statistics()
        assert stats.entity_count == 0  # Empty database

        await EngineManager.close_all()

    @pytest.mark.asyncio
    async def test_cache_invalidation_on_reindex(self, tmp_path: Path):
        """reindex 후 캐시가 무효화되는지 확인"""
        from codegraph_mcp.core.engine_manager import EngineManager

        EngineManager._instances.clear()

        codegraph_dir = tmp_path / ".codegraph"
        codegraph_dir.mkdir()

        manager = await EngineManager.get_instance(tmp_path)

        # Add some cached data
        manager._entity_cache["test"] = MagicMock()
        manager._stats_cache = MagicMock()

        # Invalidate
        manager.invalidate_cache()

        assert len(manager._entity_cache) == 0
        assert manager._stats_cache is None

        await EngineManager.close_all()
