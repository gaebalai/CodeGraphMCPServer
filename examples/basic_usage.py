#!/usr/bin/env python3
"""
기본 사용 예제
===================

CodeGraphMCPServer의 기본적인 사용 방법을 보여주는 예제입니다.

실행 방법:
    cd /path/to/CodeGraphMCPServer
    source .venv/bin/activate
    python examples/basic_usage.py
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from codegraph_mcp.core.parser import ASTParser
from codegraph_mcp.core.graph import GraphEngine, GraphQuery
from codegraph_mcp.core.indexer import Indexer
from codegraph_mcp.config import Config


async def example_1_index_repository():
    """
    예제 1: 리포지토리를 인덱싱하기

    이 예제에서는 테스트 픽스처 디렉터리를 인덱싱합니다.
    """
    print("=" * 60)
    print("예제 1: 리포지토리 인덱스 생성")
    print("=" * 60)
    
    # 테스트 픽스처 경로
    fixture_path = project_root / "tests" / "fixtures" / "python"
    
    if not fixture_path.exists():
        print(f"픽스처를 찾을 수 없습니다: {fixture_path}")
        return

    print(f"대상 디렉터리: {fixture_path}")

    # 인덱서 생성
    indexer = Indexer()

    # 인덱싱 실행
    result = await indexer.index_repository(fixture_path)

    print(f"\n결과:")
    print(f"  - 엔티티 수: {result.entities_count}")
    print(f"  - 릴레이션 수: {result.relations_count}")
    print(f"  - 처리 파일 수: {result.files_indexed}")
    print(f"  - 처리 시간: {result.duration_seconds:.2f}초")
    
    return result


async def example_2_query_entities():
    """
    예제 2: 엔티티 검색하기

    이 예제에서는 그래프 엔진을 사용해 엔티티를 검색합니다.
    """
    print("\n" + "=" * 60)
    print("예제 2: 엔티티 검색")
    print("=" * 60)
    
    fixture_path = project_root / "tests" / "fixtures" / "python"
    
    # 그래프 엔진 초기화
    engine = GraphEngine(fixture_path)
    await engine.initialize()

    try:
        # 쿼리 생성
        query = GraphQuery(query="Calculator", max_results=10)

        # 쿼리 실행
        result = await engine.query(query)

        print(f"\n검색 쿼리: 'Calculator'")
        print(f"결과: {len(result.entities)}건의 엔티티를 찾았습니다")
        
        for entity in result.entities[:5]:
            print(f"  - {entity.name} ({entity.type.value})")
            print(f"    파일: {entity.file_path}:{entity.start_line}")
    finally:
        await engine.close()


async def example_3_find_callers():
    """
    예제 3: 호출자(호출 원) 검색하기

    이 예제에서는 특정 메서드를 호출하는 쪽을 검색합니다.
    """
    print("\n" + "=" * 60)
    print("예제 3: 호출자 검색")
    print("=" * 60)
    
    fixture_path = project_root / "tests" / "fixtures" / "python"
    
    engine = GraphEngine(fixture_path)
    await engine.initialize()
    
    try:
        # 먼저 엔티티를 검색
        query = GraphQuery(query="add", max_results=5)
        result = await engine.query(query)

        if not result.entities:
            print("엔티티를 찾을 수 없습니다")
            return

        target_entity = result.entities[0]
        print(f"\n대상 엔티티: {target_entity.qualified_name}")

        # 호출자 검색
        callers = await engine.find_callers(target_entity.id)

        print(f"호출자: {len(callers)}건")
        for caller in callers:
            print(f"  - {caller.name} ({caller.type.value})")
    finally:
        await engine.close()


async def example_4_analyze_dependencies():
    """
    예제 4: 의존 관계 분석하기

    이 예제에서는 엔티티의 의존 관계를 분석합니다.
    """
    print("\n" + "=" * 60)
    print("예제 4: 의존 관계 분석")
    print("=" * 60)
    
    fixture_path = project_root / "tests" / "fixtures" / "python"
    
    engine = GraphEngine(fixture_path)
    await engine.initialize()
    
    try:
        # 클래스 검색
        query = GraphQuery(query="Calculator", max_results=1)
        result = await engine.query(query)

        if not result.entities:
            print("엔티티를 찾을 수 없습니다")
            return

        target = result.entities[0]
        print(f"\n대상 엔티티: {target.qualified_name}")

        # 의존 관계 검색
        deps = await engine.find_dependencies(target.id, depth=2)

        print(f"\n의존 관계:")
        for dep in deps.entities[:10]:
            print(f"  - {dep.name} ({dep.type.value})")
    finally:
        await engine.close()


async def example_5_get_statistics():
    """
    예제 5: 통계 정보 가져오기

    이 예제에서는 그래프 통계 정보를 가져옵니다.
    """
    print("\n" + "=" * 60)
    print("예제 5: 통계 정보 조회")
    print("=" * 60)
    
    fixture_path = project_root / "tests" / "fixtures" / "python"
    
    engine = GraphEngine(fixture_path)
    await engine.initialize()
    
    try:
        stats = await engine.get_statistics()
        
        print(f"\n그래프 통계:")
        print(f"  - 엔티티 수: {stats.get('entity_count', 0)}")
        print(f"  - 릴레이션 수: {stats.get('relation_count', 0)}")
        print(f"  - 파일 수: {stats.get('file_count', 0)}")

        if "entities_by_type" in stats:
            for entity_type, count in stats["entities_by_type"].items():
                print(f"    - {entity_type}: {count}")
    finally:
        await engine.close()


async def example_6_use_parser_directly():
    """
    예제 6: 파서를 직접 사용하기

    이 예제에서는 AST 파서를 직접 사용해 코드를 분석합니다.
    """
    print("\n" + "=" * 60)
    print("예제 6: 파서 직접 사용")
    print("=" * 60)
    
    # 샘플 코드
    sample_code = '''
class Calculator:
    """간단한 계산기 클래스"""

    def add(self, a: int, b: int) -> int:
        """두 수를 더합니다"""
        return a + b

    def multiply(self, a: int, b: int) -> int:
        """두 수를 곱합니다"""
        return a * b


def main():
    """메인 함수"""
    calc = Calculator()
    result = calc.add(1, 2)
    print(f"Result: {result}")
'''
    
    # 파서 생성
    parser = ASTParser()

    # 코드 분석
    entities, relations = parser.parse_code(
        code=sample_code,
        language="python",
        file_path="sample.py"
    )
    
    print(f"\n분석 결과:")
    print(f"  - 엔티티 수: {len(entities)}")
    print(f"  - 릴레이션 수: {len(relations)}")

    print(f"\n엔티티 목록:")
    for entity in entities:
        print(f"  - {entity.name} ({entity.type.value}) [행 {entity.start_line}-{entity.end_line}]")

    print(f"\n릴레이션 목록:")
    for rel in relations:
        print(f"  - {rel.source_id} --[{rel.type.value}]--> {rel.target_id}")


async def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("CodeGraphMCPServer 사용 예시")
    print("=" * 60 + "\n")
    
    # 각 예제를 순서대로 실행
    await example_1_index_repository()
    await example_2_query_entities()
    await example_3_find_callers()
    await example_4_analyze_dependencies()
    await example_5_get_statistics()
    await example_6_use_parser_directly()
    
    print("\n" + "=" * 60)
    print("모든 예제가 완료되었습니다")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
