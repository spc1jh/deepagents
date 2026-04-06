# CLI에서 동적 SubAgent 실제 작동 가이드

**질문**: "CLI에서 실제로 코드를 생성할 때 동적 subagent를 불러서 작동되게 할 수 있어?"

**답변**: ✅ **가능합니다!** 하지만 추가 통합 작업이 필요합니다.

---

## 📊 현재 상태

### ✅ SDK 레벨 (준비 완료)
```
libs/deepagents/deepagents/middleware/subagents.py
├── SpawnAgentConfig ✅
├── DynamicSubAgentRegistry ✅
├── TaskToolSchema (spawn_config 지원) ✅
└── task/atask 도구 (동적 생성 로직) ✅
```

### ❌ CLI 레벨 (미통합)
```
libs/cli/deepagents_cli/
├── app.py (아직 DynamicSubAgentRegistry 미사용)
├── agent.py (서브에이전트 로직 미통합)
├── system_prompt.md (동적 스폰 지시사항 부재)
└── /spawn-agent (미구현 슬래시 명령)
```

---

## 🔧 필요한 통합 작업 (5단계)

### 1️⃣ app.py에 DynamicSubAgentRegistry 통합

```python
# libs/cli/deepagents_cli/app.py

from deepagents.middleware.subagents import (
    DynamicSubAgentRegistry,
    SpawnAgentConfig,
)

class ChatScreen(Screen):
    def __init__(self, ...):
        ...
        # ✅ 레지스트리 생성
        self.dynamic_registry = DynamicSubAgentRegistry(
            backend=self.backend,
            parent_model=self.agent_model,
            parent_tools=self.get_available_tools(),
        )

    def get_available_tools(self) -> list[BaseTool]:
        """CLI에서 사용 가능한 도구 목록."""
        return [
            self.read_file_tool,
            self.write_file_tool,
            self.execute_tool,
            self.search_tool,
            # ... 기타 도구
        ]
```

### 2️⃣ agent.py에서 SubAgentMiddleware 설정 시 registry 전달

```python
# libs/cli/deepagents_cli/agent.py

from deepagents.middleware.subagents import SubAgentMiddleware

def create_agent_with_subagents(
    model,
    tools,
    dynamic_registry,  # ✅ 새로 추가
):
    """SubAgent 미들웨어에 DynamicSubAgentRegistry 통합."""

    middleware = [
        SubAgentMiddleware(
            backend=backend,
            subagents=[...],
            system_prompt=...,
        ),
    ]

    # ✅ 레지스트리를 task 도구에 전달
    # (현재 구현: _build_task_tool()에 dynamic_registry 파라미터 필요)

    return create_agent(
        model=model,
        tools=tools,
        middleware=middleware,
    )
```

### 3️⃣ system_prompt.md에 동적 스폰 지시사항 추가

```markdown
# system_prompt.md 추가 섹션

## 동적 SubAgent 스포닝 (Advanced)

`task` 도구로 런타임에 새로운 전문가 에이전트를 즉시 생성할 수 있습니다.

### 사용 예시

사용자: "이 코드의 보안 문제를 분석하고 고쳐줘"

당신: 먼저 보안 전문가 에이전트를 동적으로 생성합니다.

```json
{
  "name": "task",
  "arguments": {
    "description": "다음 코드의 OWASP Top 10 보안 취약점 분석...",
    "spawn_config": {
      "name": "security-expert",
      "role": "보안 전문가",
      "instructions": "당신은 보안 전문가입니다. OWASP Top 10...",
      "tools": ["read_file", "execute"],
      "model": "anthropic:claude-opus"
    }
  }
}
```

### 언제 사용할까?

✅ **사용하세요**:
- 복잡한 보안/코드 리뷰 분석
- 특화된 도메인 작업 (데이터 분석, ML, 등)
- 병렬 독립 작업

❌ **사용하지 마세요**:
- 간단한 파일 읽기/수정
- 빠른 응답 필요 시 (생성 오버헤드)
```

### 4️⃣ 슬래시 명령 추가: `/spawn-agent`

```python
# libs/cli/deepagents_cli/command_registry.py

SlashCommand(
    name="/spawn-agent",
    description="동적으로 전문가 에이전트 생성",
    bypass_tier=BypassTier.QUEUED,
    hidden_keywords="expert specialist create dynamic",
)
```

```python
# libs/cli/deepagents_cli/app.py (_handle_command에 추가)

async def _handle_spawn_agent(self, args: str) -> None:
    """
    /spawn-agent name:보안전문가 role:보안분석 tools:read_file,execute
    """
    # 파싱 → SpawnAgentConfig 생성 → registry.spawn_ephemeral()
    # 결과를 UI에 표시
```

### 5️⃣ _build_task_tool() 수정 (SDK 레벨)

```python
# libs/deepagents/deepagents/middleware/subagents.py

def _build_task_tool(
    subagents,
    task_description=None,
    dynamic_registry=None,  # ✅ 기본값 None
) -> BaseTool:
    """task 도구에 동적 레지스트리 전달."""

    def task(description, subagent_type="", runtime=None, spawn_config=None):
        # spawn_config와 dynamic_registry가 모두 있을 때
        if spawn_config and dynamic_registry:
            agent_name, spawned = dynamic_registry.spawn_ephemeral(spawn_config)
            ...
```

---

## 🎯 실제 작동 시나리오

### 사용자 입력
```
> /task 이 Python 파일의 보안 취약점을 찾아줘

[파일 context 제공]
```

### CLI 처리 플로우

```
1. Textual UI (chat_screen.py)
   ↓
2. app.py: _handle_user_message()
   ├─ 메시지 에이전트에 전송
   ├─ spawn_config 감지
   ↓
3. middleware/subagents.py: task() 함수
   ├─ dynamic_registry.spawn_ephemeral(spawn_config)
   │  ├─ create_agent() 호출 → 새 LLM 에이전트 생성
   │  ├─ 모델 해석 ("anthropic:claude-opus")
   │  ├─ 도구 해석 (["read_file", "execute"])
   │  └─ SpawnedSubAgent 반환 (고유 instance_id)
   ├─ 상태 관리: CREATED → RUNNING → COMPLETED → DESTROYED
   ├─ 에이전트 실행
   ↓
4. 결과 반환
   ├─ UI에 출력
   ├─ 메모리 정리 (destroy)
   ↓
5. 다음 요청 대기
```

---

## ✅ 구현 체크리스트

### 필수 (기본 작동)
- [ ] app.py에 DynamicSubAgentRegistry 생성
- [ ] agent.py에서 registry 초기화
- [ ] _build_task_tool()에 registry 파라미터 추가
- [ ] SubAgentMiddleware에 registry 전달

### 선택 (UI/UX 개선)
- [ ] `/spawn-agent` 슬래시 명령 (대화형 생성)
- [ ] system_prompt.md 업데이트 (에이전트 지시사항)
- [ ] 상태 추적 UI (생성 중... 실행 중... 완료)
- [ ] 메모리 사용량 모니터링

---

## 📝 코드 예시: 간단한 통합

```python
# 최소 구현 (app.py 일부)

class ChatScreen(Screen):
    def __init__(self, ...):
        # 1. 레지스트리 생성
        self.dynamic_registry = DynamicSubAgentRegistry(
            backend=self.backend,
            parent_model="openai:gpt-4o",
            parent_tools=[
                read_file_tool,
                write_file_tool,
                execute_tool,
            ],
        )

        # 2. 미들웨어 생성 (registry 통합 필요)
        middleware = [
            SubAgentMiddleware(
                backend=self.backend,
                subagents=self.subagents,
                system_prompt=...,
            ),
        ]

        # 3. 에이전트 생성
        self.agent = create_agent(
            model=model,
            tools=tools,
            middleware=middleware,
        )

        # 4. 사용 시
        # 사용자가 spawn_config와 함께 task 도구 호출
        # → dynamic_registry가 새 에이전트 생성
        # → 작업 실행
        # → 자동 정리
```

---

## 🚀 다음 단계

### 즉시 할 수 있는 것
1. **테스트**: SDK 테스트 실행 (29개 테스트)
2. **문서 검토**: SUBAGENT_DYNAMIC_GUIDE.md 읽기

### Phase 3 (다음 코드 작업)
1. SDK의 `spawn_ephemeral()` 구현 (상태 관리 추가)
2. CLI에 registry 통합
3. `/spawn-agent` 슬래시 명령
4. 엔드-투-엔드 테스트

---

## ❓ 자주 묻는 질문

**Q1**: CLI에서 지금 바로 사용할 수 있어?
**A1**: ❌ 아직 아닙니다. SDK는 준비됨, CLI 통합 필요.

**Q2**: 얼마나 복잡해?
**A2**: ✅ 간단합니다. 위의 5단계 (각 10-20줄 코드)

**Q3**: 기존 기능에 영향?
**A3**: ✅ 없습니다. 완전 하위호환 (spawn_config는 선택사항)

**Q4**: 성능 영향?
**A4**: ❌ 최소화. 캐싱으로 최적화 가능.

---

**상태**: 📋 구현 계획 수립 완료
**다음 작업**: Phase 3 CLI 통합 (별도 세션)
