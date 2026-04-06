# 🚀 SubAgent CLI 데모 가이드

Deep Agents CLI에서 **SubAgent** 기능을 직접 사용해보는 방법입니다.

---

## 📖 시작하기

### 1. CLI 실행
```bash
cd /home/ubuntu/deepagents
uv run deepagents
```

출력 화면:
```
┌─────────────────────────────────────────────┐
│  >                                          │
└─────────────────────────────────────────────┘
manual | shift+tab to cycle   ~/deepagents

Ready to code! What would you like to build?
```

---

## 🎯 SubAgent 사용법

### 방법 1️⃣: 자동 SubAgent 호출 (권장)

메인 에이전트에게 직접 요청하면, 에이전트가 **필요시 자동으로** subagent를 호출합니다.

CLI 입력창에서 복잡한 작업을 요청하면:

```
입력: 세 가지 프로그래밍 언어를 비교해주세요: Python, Go, Rust
      각각에 대해:
      - 주요 특징
      - 적합한 사용 분야
      - 장단점
```

메인 에이전트가 판단하여 subagent(들)에게 연구 작업을 위임합니다.

---

## 💡 간단한 데모 시나리오

### 데모 1: 기본 조사 작업
```
/task

Description: 인공지능(AI)의 역사를 시간순으로 정리해주세요.
- 초기 개발 (1950s-1970s)
- 제1의 겨울과 회복 (1970s-1990s)
- 현대 AI 시대 (2010s-현재)

각 시대의 주요 성과와 기술 발전을 포함해주세요.

Agent type: general-purpose
```

### 데모 2: 코드 분석 작업
```
/task

Description: 다음 Python 코드 패턴을 설명해주세요:
- Context Manager (with 문)
- Generator 함수
- Decorator

각각의 사용 사례와 장점을 코드 예시와 함께 설명해주세요.

Agent type: general-purpose
```

### 데모 3: 병렬 SubAgent 호출
```
입력: 다음 세 가지를 각각 조사해주세요:

1. 클라우드 컴퓨팅의 주요 장점
2. 엣지 컴퓨팅의 주요 장점
3. 온프레미스 솔루션의 주요 장점

각각의 사용 사례와 비용 편익을 포함해서요.
```

이 경우 메인 에이전트가 3개의 독립적인 subagent를 **병렬로** 실행합니다.

---

## 🔄 기대되는 동작 흐름

```
┌───────────────────────────────────┐
│   CLI에 요청 입력                  │
│  "/task 조사 내용"                 │
└──────────────┬────────────────────┘
               │
┌──────────────▼────────────────────┐
│   Main Agent 분석                  │
│  - 요청 파싱                       │
│  - SubAgent 필요 여부 판단          │
└──────────────┬────────────────────┘
               │
         ┌─────▼─────┐
         │ SubAgent   │
         │ 생성 및    │
         │ 실행       │
         └─────┬─────┘
               │
┌──────────────▼────────────────────┐
│   결과 종합 및 응답                 │
│  - SubAgent 결과 수집              │
│  - 사용자 친화적 포맷으로 정렬      │
│  - CLI에 표시                      │
└──────────────┬────────────────────┘
               │
               ▼
         ┌─────────────┐
         │ 사용자 화면 │
         │  최종 결과  │
         └─────────────┘
```

---

## ✨ SubAgent의 이점

| 이점 | 설명 |
|------|------|
| **격리된 컨텍스트** | 각 SubAgent가 독립적인 메모리와 상태 유지 |
| **병렬 처리** | 여러 작업을 동시에 수행하여 시간 단축 |
| **전문화** | 특정 도메인에 최적화된 SubAgent 사용 |
| **토큰 효율** | 큰 작업을 작은 부분으로 나누어 비용 절감 |
| **명확한 구조** | 작업의 진행 과정을 명확하게 추적 |

---

## 🎮 직접 테스트해보기

### 권장 첫 번째 테스트:
```
입력: 한국의 현재 시간을 알려주세요
```

간단한 요청으로 시스템이 정상 작동하는지 확인합니다.

### 두 번째 테스트 (SubAgent 활용):
```
입력: 프로그래밍을 배우고 싶은데, JavaScript와 Python 중 어느 것부터 시작하면 좋을까요?
     각 언어의 학습 곡선, 커뮤니티 규모, 취업 전망을 비교해서 조언해주세요.
```

이 요청은 충분히 복잡하여 SubAgent의 도움을 받을 가능성이 높습니다.

---

## 📊 SubAgent 상태 확인

CLI에서는 다음 정보를 확인할 수 있습니다:
- ✅ SubAgent 생성 시점
- ✅ 작업 진행 상황
- ✅ 완료 시간
- ✅ 최종 결과

---

## 🛠️ 고급: 커스텀 SubAgent 설정

클릭/입력을 통해 커스텀 SubAgent를 생성할 수 있습니다:

```
입력: /task

Description: 해양 생물에 대해 조사해주세요

spawn_config:
  name: "marine-researcher"
  role: "해양 생물 전문가"
  instructions: "해양 생물의 특징, 서식지, 생태계 역할을 자세히 설명해주세요"
  tools: ["search", "write"]  # 사용 가능한 도구 지정
  model: "openai:gpt-4o"      # 모델 선택 (선택사항)
```

---

## ❓ FAQ

**Q1: SubAgent가 뭔가요?**
A: 복잡한 작업을 별도의 독립적인 에이전트에게 위임하는 기능입니다. 마치 팀 리더가 팀원에게 작업을 할당하는 것처럼요.

**Q2: 언제 SubAgent가 자동으로 호출되나요?**
A: 메인 에이전트가 요청이 "복잡하고 다단계적이고 독립적"이라고 판단할 때입니다.

**Q3: SubAgent 결과는 어디서 보나요?**
A: CLI 화면의 "Task Result" 섹션에서 확인할 수 있습니다.

**Q4: 여러 SubAgent를 동시에 실행할 수 있나요?**
A: 네! 메인 에이전트가 독립적인 작업들을 감지하면 여러 SubAgent를 **병렬로** 실행합니다.

**Q5: SubAgent의 모델은 어떤 것을 사용하나요?**
A: SubAgent는 **메인 에이전트와 동일한 모델**을 사용합니다.
- 기본값: `openai:gpt-4o`
- CLI에서 설정한 모델: 설정한 그 모델 사용
- 커스텀 모델: SpawnAgentConfig에서 명시적으로 지정 가능

**Q6: SubAgent도 메인 에이전트와 같은 권한을 가지나요?**
A: 기본적으로는 동일한 도구와 권한을 가집니다. 다만 시스템 프롬프트와 지시사항이 다를 수 있습니다.

**Q7: SubAgent 생성/삭제 과정은 자동인가요?**
A: 네! 완전히 자동입니다.
- 생성: 필요시 자동 생성
- 실행: 독립적으로 작업 수행
- 삭제: 작업 완료 후 자동 소멸 (메모리 정리)

**Q8: 메인 모델을 변경하면 SubAgent도 변경되나요?**
A: **네! 자동으로 변경됩니다.**

메인 에이전트의 모델을 `/model` 명령어로 변경하면:
```bash
/model gpt-4o           # 메인 모델 변경
→ SubAgent도 gpt-4o 사용

/model claude-3-5-sonnet  # 메인 모델 변경
→ SubAgent도 claude-3-5-sonnet 사용
```

**동작 방식:**
SubAgent는 메인 에이전트의 모델 설정을 **동적으로 참조**하므로,
메인 모델이 변경되면 새로 생성되는 모든 SubAgent가 자동으로 같은 모델을 사용합니다.

---

**Q9: SubAgent가 메인 에이전트와 다른 모델을 사용하게 하려면?**
A: **CLI에서는 현재 불가능합니다** (메인 에이전트와 동일한 모델 사용).
하지만 다음 두 가지 방법으로 확장할 수 있습니다:

### 방법 1: Python 코드로 커스텀 SubAgent 정의 (권장)

```python
from deepagents import create_deep_agent
from deepagents.middleware import SubAgentMiddleware

# 메인 에이전트용 모델
main_model = "openai:gpt-4o"

# SubAgent용 모델 (더 경제적인 모델)
subagent_config = {
    "name": "analyzer",
    "description": "분석 전문가",
    "system_prompt": "당신은 데이터 분석 전문가입니다.",
    "model": "openai:gpt-4o-mini",  # ← 다른 모델 지정
    "tools": [search_tool, analysis_tool],
}

agent = create_deep_agent(
    model=main_model,
    middleware=[
        SubAgentMiddleware(
            backend=backend,
            subagents=[subagent_config],
        )
    ],
)
```

**비용 최적화 팁:**
- 메인 에이전트: 정교한 모델 (예: `gpt-4o`)
- SubAgent: 경제적 모델 (예: `gpt-4o-mini`, `claude-3-haiku`)

---

## 📝 다음 단계

1. ✅ CLI 실행
2. ✅ 간단한 요청부터 시작
3. ✅ 점점 복잡한 요청으로 확대
4. ✅ 필요시 `/task` 명령어로 명시적 호출
5. 🚀 커스텀 SubAgent 정의 및 실행

즐거운 테스트되세요! 🎉
