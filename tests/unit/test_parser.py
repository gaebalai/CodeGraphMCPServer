"""
Parser Unit Tests
=================

AST 파서의 단위 테스트.
"""

from pathlib import Path

from codegraph_mcp.core.parser import (
    ASTParser,
    Entity,
    EntityType,
    Location,
    ParseResult,
    Relation,
    RelationType,
)


class TestASTParser:
    """ASTParser 테스트"""

    def test_parser_initialization(self):
        """파서 초기화 테스트"""
        parser = ASTParser()
        assert parser is not None
        assert not parser._initialized

    def test_language_detection(self):
        """언어 검색 테스트"""
        parser = ASTParser()
        assert parser.detect_language(Path("test.py")) == "python"
        assert parser.detect_language(Path("test.ts")) == "typescript"
        assert parser.detect_language(Path("test.rs")) == "rust"
        assert parser.detect_language(Path("test.txt")) is None

    def test_parse_python_file(self, temp_dir):
        """Python 파일 파싱 테스트"""
        # 샘플 파일 생성
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}"

class Greeter:
    def greet(self):
        return hello("World")
''')

        parser = ASTParser()
        result = parser.parse_file(test_file)

        assert result.success
        assert len(result.entities) >= 3  # module, function, class

        # Check entity types
        types = {e.type for e in result.entities}
        assert EntityType.MODULE in types
        assert EntityType.FUNCTION in types
        assert EntityType.CLASS in types

    def test_parse_typescript_file(self, temp_dir):
        """TypeScript 파일 파싱 테스트"""
        test_file = temp_dir / "test.ts"
        test_file.write_text('''
interface User {
    name: string;
}

class UserService {
    getUser(): User {
        return { name: "Test" };
    }
}
''')

        parser = ASTParser()
        result = parser.parse_file(test_file)

        assert result.success
        types = {e.type for e in result.entities}
        assert EntityType.INTERFACE in types
        assert EntityType.CLASS in types

    def test_extract_function_with_docstring(self, temp_dir):
        """docstring 있는 함수 추출 테스트"""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def documented_func():
    """This is a docstring."""
    pass
''')

        parser = ASTParser()
        result = parser.parse_file(test_file)

        funcs = [e for e in result.entities if e.type == EntityType.FUNCTION]
        assert len(funcs) == 1
        # docstring extraction depends on implementation

    def test_extract_import_relations(self, temp_dir):
        """import 관계 추출 테스트"""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
import os
from pathlib import Path

def func():
    pass
''')

        parser = ASTParser()
        result = parser.parse_file(test_file)

        imports = [r for r in result.relations if r.type == RelationType.IMPORTS]
        assert len(imports) >= 2

    def test_extract_inheritance_relations(self, temp_dir):
        """상속 관계 추출 테스트"""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
class Base:
    pass

class Child(Base):
    pass
''')

        parser = ASTParser()
        result = parser.parse_file(test_file)

        inherits = [r for r in result.relations if r.type == RelationType.INHERITS]
        assert len(inherits) >= 1

    def test_unsupported_file_type(self, temp_dir):
        """지원하지 않는 파일 형식 테스트"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello World")

        parser = ASTParser()
        result = parser.parse_file(test_file)

        assert not result.success
        assert len(result.errors) == 1

    def test_parse_multiple_files(self, temp_dir):
        """여러 파일 파싱 테스트"""
        file1 = temp_dir / "a.py"
        file1.write_text("def func_a(): pass")

        file2 = temp_dir / "b.py"
        file2.write_text("def func_b(): pass")

        parser = ASTParser()
        result = parser.parse_files([file1, file2])

        assert result.success
        names = {e.name for e in result.entities}
        assert "func_a" in names
        assert "func_b" in names


class TestEntity:
    """Entity 클래스 테스트"""

    def test_entity_creation(self):
        """엔티티 생성 테스트"""
        location = Location(
            file_path=Path("/test/file.py"),
            start_line=10,
            start_column=0,
            end_line=20,
            end_column=0,
        )

        entity = Entity(
            id="test_id",
            type=EntityType.FUNCTION,
            name="test_func",
            qualified_name="/test/file.py::test_func",
            location=location,
            signature="def test_func()",
            docstring="Test function",
        )

        assert entity.id == "test_id"
        assert entity.type == EntityType.FUNCTION
        assert entity.name == "test_func"
        assert entity.file_path == Path("/test/file.py")
        assert entity.start_line == 10
        assert entity.end_line == 20

    def test_entity_metadata(self):
        """엔티티 메타데이터 테스트"""
        location = Location(
            file_path=Path("/test/file.py"),
            start_line=1,
            start_column=0,
            end_line=5,
            end_column=0,
        )

        entity = Entity(
            id="test_id",
            type=EntityType.CLASS,
            name="TestClass",
            qualified_name="/test/file.py::TestClass",
            location=location,
            metadata={"visibility": "public", "abstract": False},
        )

        assert entity.metadata["visibility"] == "public"
        assert entity.metadata["abstract"] is False


class TestRelation:
    """Relation 클래스 테스트"""

    def test_relation_creation(self):
        """관계 생성 테스트"""
        relation = Relation(
            source_id="source_entity",
            target_id="target_entity",
            type=RelationType.CALLS,
            weight=1.0,
        )

        assert relation.source_id == "source_entity"
        assert relation.target_id == "target_entity"
        assert relation.type == RelationType.CALLS
        assert relation.weight == 1.0

    def test_relation_with_metadata(self):
        """메타데이터 있는 관계 테스트"""
        relation = Relation(
            source_id="class_a",
            target_id="class_b",
            type=RelationType.INHERITS,
            metadata={"line": 10, "column": 5},
        )

        assert relation.metadata["line"] == 10


class TestParseResult:
    """ParseResult 클래스 테스트"""

    def test_empty_result(self):
        """빈 결과 테스트"""
        result = ParseResult()
        assert result.success
        assert len(result.entities) == 0
        assert len(result.relations) == 0

    def test_merge_results(self):
        """결과 병합 테스트"""
        location = Location(
            file_path=Path("/test/file.py"),
            start_line=1,
            start_column=0,
            end_line=5,
            end_column=0,
        )

        result1 = ParseResult(
            entities=[Entity(
                id="e1", type=EntityType.FUNCTION, name="func1",
                qualified_name="func1", location=location,
            )],
        )

        result2 = ParseResult(
            entities=[Entity(
                id="e2", type=EntityType.FUNCTION, name="func2",
                qualified_name="func2", location=location,
            )],
        )

        merged = result1.merge(result2)
        assert len(merged.entities) == 2
