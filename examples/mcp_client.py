#!/usr/bin/env python3
"""
MCP 클라이언트 예제
==================

MCP 클라이언트에서 CodeGraphMCPServer를 사용하는 예제입니다.

실행 방법:
    # 1. 별도 터미널에서 서버를 기동
    codegraph-mcp serve --repo /path/to/project

    # 2. 이 스크립트를 실행
    python examples/mcp_client.py

주의:
    이 예제를 실행하려면 MCP Python SDK가 필요합니다.
    pip install mcp
"""

import asyncio
import json
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


async def example_1_list_tools():
    """
    예제 1: 사용 가능한 도구 목록 출력

    MCP 서버에 연결해 사용 가능한 도구 목록을 가져옵니다.
    """
    print("=" * 60)
    print("예제 1: 사용 가능한 도구 목록")
    print("=" * 60)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        # 서버 파라미터 설정
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "codegraph_mcp", "serve", "--repo", str(project_root)],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 도구 목록 가져오기
                tools = await session.list_tools()
                print(f"\n사용 가능한 도구: {len(tools.tools)}개")
                for tool in tools.tools:
                    print(f"  - {tool.name}")
                    print(f"    {tool.description[:60]}...")

    except ImportError:
        print("\nMCP SDK가 설치되어 있지 않습니다.")
        print("아래 명령으로 설치해 주세요:")
        print("  pip install mcp")


async def example_2_call_tool():
    """
    예제 2: 도구 호출하기

    query_codebase 도구를 호출해 코드를 검색합니다.
    """
    print("\n" + "=" * 60)
    print("예제 2: 도구 호출")
    print("=" * 60)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="python",
            args=["-m", "codegraph_mcp", "serve", "--repo", str(project_root)],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # query_codebase 도구 호출
                print("\nquery_codebase 도구 호출 중...")
                result = await session.call_tool(
                    "query_codebase",
                    arguments={
                        "query": "GraphEngine",
                        "max_results": 5,
                    },
                )

                print(f"\n결과:")
                for content in result.content:
                    print(content.text)

    except ImportError:
        print("\nMCP SDK가 설치되어 있지 않습니다.")


async def example_3_list_resources():
    """
    예제 3: 리소스 목록 출력

    MCP 서버에서 사용 가능한 리소스를 가져옵니다.
    """
    print("\n" + "=" * 60)
    print("예제 3: 사용 가능한 리소스 목록")
    print("=" * 60)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="python",
            args=["-m", "codegraph_mcp", "serve", "--repo", str(project_root)],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 리소스 목록 가져오기
                resources = await session.list_resources()
                print(f"\n사용 가능한 리소스: {len(resources.resources)}개")
                for resource in resources.resources:
                    print(f"  - {resource.uri}")
                    print(f"    {resource.description[:60]}...")

    except ImportError:
        print("\nMCP SDK가 설치되어 있지 않습니다.")


async def example_4_read_resource():
    """
    예제 4: 리소스 읽기

    통계 정보 리소스를 읽어옵니다.
    """
    print("\n" + "=" * 60)
    print("예제 4: 리소스 읽기")
    print("=" * 60)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="python",
            args=["-m", "codegraph_mcp", "serve", "--repo", str(project_root)],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 통계 리소스 읽기
                print("\ncodegraph://stats 리소스 읽는 중...")
                content = await session.read_resource("codegraph://stats")

                print(f"\n통계 정보:")
                for item in content.contents:
                    print(item.text)

    except ImportError:
        print("\nMCP SDK가 설치되어 있지 않습니다.")


async def example_5_list_prompts():
    """
    예제 5: 프롬프트 목록 출력

    MCP 서버에서 사용 가능한 프롬프트를 가져옵니다.
    """
    print("\n" + "=" * 60)
    print("예제 5: 사용 가능한 프롬프트 목록")
    print("=" * 60)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="python",
            args=["-m", "codegraph_mcp", "serve", "--repo", str(project_root)],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 프롬프트 목록 가져오기
                prompts = await session.list_prompts()
                print(f"\n사용 가능한 프롬프트: {len(prompts.prompts)}개")
                for prompt in prompts.prompts:
                    print(f"  - {prompt.name}")
                    print(f"    {prompt.description[:60]}...")

    except ImportError:
        print("\nMCP SDK가 설치되어 있지 않습니다.")


async def example_6_get_prompt():
    """
    예제 6: 프롬프트 가져오기

    code_review 프롬프트를 가져옵니다.
    """
    print("\n" + "=" * 60)
    print("예제 6: 프롬프트 가져오기")
    print("=" * 60)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="python",
            args=["-m", "codegraph_mcp", "serve", "--repo", str(project_root)],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 프롬프트 가져오기
                print("\ncode_review 프롬프트 가져오는 중...")
                result = await session.get_prompt(
                    "code_review",
                    arguments={
                        "entity_id": "sample_entity",
                        "focus_areas": "performance,security",
                    },
                )

                print(f"\n생성된 프롬프트:")
                for message in result.messages:
                    print(f"  Role: {message.role}")
                    print(f"  Content: {message.content.text[:200]}...")

    except ImportError:
        print("\nMCP SDK가 설치되어 있지 않습니다.")


def show_manual_usage():
    """MCP를 쓰지 않는 수동 사용 예시를 출력"""
    print("\n" + "=" * 60)
    print("MCP SDK 없이 사용하는 방법")
    print("=" * 60)

    print("""
MCP 클라이언트가 없는 경우, CLI를 직접 사용할 수 있습니다:

1. 인덱스 생성:
   codegraph-mcp index /path/to/repository --full

2. 쿼리 실행:
   codegraph-mcp query "Calculator" --repo /path/to/repository

3. 통계 정보:
   codegraph-mcp stats /path/to/repository

4. 서버 기동:
   codegraph-mcp serve --repo /path/to/repository

자세한 내용은 README.md를 참고해 주세요.
""")


async def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("CodeGraphMCPServer MCP 클라이언트 예제")
    print("=" * 60)

    # MCP SDK 존재 여부 확인
    try:
        import mcp
        print(f"\nMCP SDK 버전: {mcp.__version__}")
        has_mcp = True
    except ImportError:
        has_mcp = False
        print("\nMCP SDK를 찾을 수 없습니다.")
        print("설치: pip install mcp")

    if has_mcp:
        print("\n주의: 아래 예제는 MCP 서버를 서브프로세스로 기동합니다.")
        print("Ctrl+C로 중단할 수 있습니다.")

        try:
            await example_1_list_tools()
            await example_2_call_tool()
            await example_3_list_resources()
            await example_4_read_resource()
            await example_5_list_prompts()
            await example_6_get_prompt()
        except KeyboardInterrupt:
            print("\n\n중단되었습니다.")
        except Exception as e:
            print(f"\n에러: {e}")
            print("서버를 정상적으로 기동하지 못했을 가능성이 있습니다.")

    # 수동 사용 예시 출력
    show_manual_usage()

    print("\n" + "=" * 60)
    print("완료")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
