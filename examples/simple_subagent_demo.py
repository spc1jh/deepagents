#!/usr/bin/env python3
"""
간단한 SubAgent 데모 스크립트

이 스크립트는 Deep Agents의 SubAgent 기능을 리스트 정렬 방법 비교라는
간단한 작업을 통해 보여줍니다.

사용법:
    uv run examples/simple_subagent_demo.py
"""

import asyncio
from langchain_anthropic import ChatAnthropic
from deepagents import create_deep_agent
from deepagents.backends import LocalFileSystemBackend


async def main() -> None:
    """간단한 SubAgent 데모를 실행합니다."""

    # 백엔드 설정 (파일 시스템 사용)
    backend = LocalFileSystemBackend()

    # 모델 설정
    model = ChatAnthropic(model_name="claude-3-5-sonnet-20241022")

    # DeepAgent 생성 (subagent 기능 포함)
    agent = create_deep_agent(
        model=model,
        backend=backend,
        enable_subagents=True,  # SubAgent 기능 활성화
    )

    print("=" * 80)
    print("🚀 Deep Agents SubAgent 데모")
    print("=" * 80)
    print()

    # 데모 1: 간단한 작업
    print("📝 데모 1: 간단한 정보 요청")
    print("-" * 80)

    task1 = "한국의 수도는 어디인가요?"
    print(f"질문: {task1}")
    print()

    result1 = await agent.ainvoke({"messages": [{"role": "user", "content": task1}]})
    print("응답:")
    if result1.get("messages"):
        print(result1["messages"][-1].content)
    print()
    print()

    # 데모 2: SubAgent가 활용될 수 있는 복잡한 작업
    print("📝 데모 2: 복잡한 분석 작업 (SubAgent 활용)")
    print("-" * 80)

    task2 = """
파이썬에서 리스트를 정렬하는 3가지 방법을 비교 분석해주세요:
1. 내장 sort() 메서드 사용
2. sorted() 함수 사용
3. 람다 함수를 이용한 커스텀 정렬

각 방법에 대해:
- 동작 방식
- 사용 사례
- 성능 차이
- 코드 예시

를 포함해서 설명해주세요.
"""

    print(f"질문: {task2.strip()}")
    print()
    print("⏳ SubAgent가 독립적으로 분석 중...")
    print()

    result2 = await agent.ainvoke({"messages": [{"role": "user", "content": task2}]})
    print("응답:")
    if result2.get("messages"):
        # 긴 응답이므로 처음 500자만 표시
        full_response = result2["messages"][-1].content
        display_response = full_response[:500] + "..." if len(full_response) > 500 else full_response
        print(display_response)
    print()
    print()

    # 데모 3: 여러 독립적 작업 (병렬 SubAgent 호출 가능)
    print("📝 데모 3: 여러 도메인 분석 (병렬 SubAgent 활용 가능)")
    print("-" * 80)

    task3 = """
다음 세 가지 개념을 각각 설명해주세요:

1. REST API란 무엇이고 어떻게 작동하나요?
2. GraphQL은 REST API와 어떻게 다른가요?
3. 각각을 언제 사용하면 좋을까요?

각 질문에 대해 간단하지만 명확한 설명을 부탁합니다.
"""

    print(f"질문: {task3.strip()}")
    print()
    print("⏳ 메인 에이전트가 필요시 여러 SubAgent를 활용하여 분석 중...")
    print()

    result3 = await agent.ainvoke({"messages": [{"role": "user", "content": task3}]})
    print("응답:")
    if result3.get("messages"):
        full_response = result3["messages"][-1].content
        display_response = full_response[:500] + "..." if len(full_response) > 500 else full_response
        print(display_response)
    print()

    print("=" * 80)
    print("✅ 데모 완료!")
    print("=" * 80)
    print()
    print("💡 관찰 사항:")
    print("- 데모 1: 단순 조회 → SubAgent 불필요 (메인 에이전트가 직접 처리)")
    print("- 데모 2: 복잡 분석 → SubAgent 활용 가능 (독립적인 조사 작업)")
    print("- 데모 3: 다중 분석 → 여러 SubAgent 병렬 실행 가능")
    print()
    print("📚 더 알아보기:")
    print("- CLI를 통한 직접 사용: uv run deepagents")
    print("- 가이드 문서: SUBAGENT_DEMO_GUIDE.md")


if __name__ == "__main__":
    asyncio.run(main())
