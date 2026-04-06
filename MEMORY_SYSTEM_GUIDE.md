# Deep Agents CLI - Memory System 개발 가이드

**최종 업데이트**: 2026-04-06
**상태**: ✅ 완료 및 검증됨

---

## 목차
1. [시스템 개요](#시스템-개요)
2. [아키텍처](#아키텍처)
3. [구현된 기능](#구현된-기능)
4. [파일 구조](#파일-구조)
5. [사용 방법](#사용-방법)
6. [개발 상세](#개발-상세)
7. [테스트](#테스트)
8. [향후 개선사항](#향후-개선사항)

---

## 시스템 개요

Deep Agents CLI에 **구조화된 메모리 시스템**을 구현했습니다. 이 시스템은 개발자의 개인 지식 기반(Knowledge Base)을 구축하고 유지할 수 있게 해줍니다.

### 핵심 기능
- 📚 **학습 기록**: 개발자 피드백, 수정사항, 발견사항 자동 저장
- 🔍 **지식 검색**: 카테고리별, 소스별 필터링된 빠른 검색
- 👤 **개발자 프로필**: 역할, 경험 수준, 선호 언어/프레임워크 관리
- 🗂️ **지식 그래프**: 개념(Entity)과 관계(Relationship) 추적
- 📤 **데이터 내보내기**: JSON 형식으로 모든 메모리 내보내기

### 저장 위치
```
~/.deepagents/memory/
├── memory.db                    # SQLite 데이터베이스
└── developer_profile.json       # 개발자 프로필 (JSON)
```

---

## 아키텍처

### 3계층 설계

```
┌─────────────────────────────────────┐
│   Textual UI Layer (app.py)        │
│   - /memory 명령 처리               │
│   - 사용자 상호작용 관리            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Command Registry (command_registry.py)│
│   - /memory 슬래시 명령 등록        │
│   - 명령 메타데이터 정의            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   MemoryManager (memory_manager.py) │
│   - SQLite 데이터 접근              │
│   - 학습/엔티티/관계 관리          │
│   - 검색 및 통계                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   SQLite Database                   │
│   - learnings 테이블               │
│   - entities 테이블                │
│   - relationships 테이블           │
└─────────────────────────────────────┘
```

### 데이터 모델

**Learnings (학습)**
```python
{
    id: str              # UUID
    content: str         # 학습 내용
    source: str          # user_feedback | conversation | correction | discovery
    category: str        # best_practice | anti_pattern | preference | knowledge
    tags: list[str]      # 태그 목록
    session_id: str      # 세션 ID
    created_at: str      # ISO 타임스탬프
    confidence: float    # 신뢰도 (0.0-1.0)
}
```

**Entities (개념/엔티티)**
```python
{
    id: str              # 고유 식별자
    type: str            # project | library | pattern | person | concept | tool
    name: str            # 표시 이름
    description: str     # 설명
    metadata: dict       # 추가 정보
    created_at: str      # 생성 시간
    last_accessed: str   # 마지막 접근 시간
}
```

**Relationships (관계)**
```python
{
    id: str              # 관계의 고유 ID
    from_entity: str     # 출발 엔티티 ID
    to_entity: str       # 도착 엔티티 ID
    relation_type: str   # uses | depends_on | prefers | learned_from
    confidence: float    # 신뢰도
    context: str         # 관계 설명
    created_at: str      # 생성 시간
}
```

**Developer Profile (개발자 프로필)**
```python
{
    name: str                          # 개발자 이름
    role: str                          # 역할 (Backend Developer, etc.)
    experience_level: str              # junior | mid | senior | lead
    primary_languages: list[str]       # 주 프로그래밍 언어
    preferred_frameworks: list[str]    # 선호 프레임워크
    code_style: dict                   # 코딩 스타일 설정
    updated_at: str                    # 마지막 업데이트
}
```

---

## 구현된 기능

### 1. MemoryManager 클래스 (`memory_manager.py`)

**주요 메서드**:

#### `load_or_create_profile() -> DeveloperProfile`
- 개발자 프로필 로드 또는 신규 생성
- 저장 위치: `~/.deepagents/memory/developer_profile.json`

#### `save_profile(profile: DeveloperProfile) -> None`
- 개발자 프로필 저장
- `updated_at` 자동 갱신

#### `add_learning(...) -> str`
```python
add_learning(
    content: str,                    # 학습 내용
    source: str,                     # user_feedback | conversation | correction | discovery
    category: str,                   # best_practice | anti_pattern | preference | knowledge
    tags: list[str] | None = None,  # 태그
    session_id: str | None = None,  # 세션 ID
    confidence: float = 1.0          # 신뢰도
) -> str  # 학습 ID 반환
```

#### `search_learnings(...) -> list[Learning]`
```python
search_learnings(
    query: str,              # 검색 쿼리
    category: str | None,    # 카테고리 필터
    source: str | None,      # 소스 필터
    limit: int = 10          # 반환 개수
) -> list[Learning]
```

#### `add_entity(...) -> None`
```python
add_entity(
    entity_id: str,                  # 엔티티 ID
    entity_type: str,                # project | library | pattern | person | concept | tool
    name: str,                       # 이름
    description: str = "",           # 설명
    metadata: dict[str, Any] | None  # 메타데이터
) -> None
```

#### `add_relationship(...) -> None`
```python
add_relationship(
    from_entity: str,        # 출발 엔티티
    to_entity: str,          # 도착 엔티티
    relation_type: str,      # uses | depends_on | prefers | learned_from
    context: str = "",       # 관계 설명
    confidence: float = 1.0  # 신뢰도
) -> None
```

#### `get_related_entities(...) -> list[tuple[Entity, str]]`
```python
get_related_entities(
    entity_id: str,              # 엔티티 ID
    relation_type: str | None    # 관계 타입 필터
) -> list[tuple[Entity, str]]    # (엔티티, 관계타입) 튜플 목록
```

#### `export_memory(output_path: Path) -> None`
- 모든 메모리를 JSON으로 내보내기
- 구조: `{ profile, learnings, entities }`

#### `get_memory_stats() -> dict`
```python
{
    "learnings_count": int,
    "entities_count": int,
    "relationships_count": int,
    "learnings_by_category": {str: int},
    "learnings_by_source": {str: int},
    "memory_dir": str,
    "db_size_mb": float
}
```

### 2. 슬래시 명령 구현 (`command_registry.py`)

#### `/memory` 명령 등록
```python
SlashCommand(
    name="/memory",
    description="Manage developer memory (search, add, profile, export)",
    bypass_tier=BypassTier.QUEUED,
    hidden_keywords="learning knowledge profile",
)
```

**명령 계층 구조**:
- `/memory add "Learning text"` → 학습 추가
- `/memory search "query"` → 학습 검색
- `/memory profile` → 프로필 보기
- `/memory export` → JSON 내보내기
- `/memory stats` → 통계 표시

### 3. 명령 핸들러 구현 (`app.py`)

#### `_handle_memory_command(command: str) -> None` (약 120줄)

**구현된 서브명령**:

**add**: 학습 추가
```
/memory add "Python에서는 항상 type hints를 사용하기"
```
- 출력: `✓ Learning added (ID: abc12345)`

**search**: 학습 검색
```
/memory search "python"
```
- 출력: 최대 5개 결과 (날짜, 내용, 카테고리)

**profile**: 프로필 조회
```
/memory profile
```
- 출력: 이름, 역할, 경험 수준, 언어, 프레임워크, 업데이트 시간

**export**: JSON 내보내기
```
/memory export
```
- 출력: `✓ Memory exported to: ~/.deepagents/memory_export_YYYYMMDD_HHMMSS.json`

**stats**: 통계 표시
```
/memory stats
```
- 출력: 학습 수, 엔티티 수, 관계 수, 카테고리별/소스별 분류

### 4. 시스템 프롬프트 통합 (`system_prompt.md`)

**Developer Memory System** 섹션 추가 (282줄)
- 메모리 저장소 경로 설명
- 메모리 업데이트 시기 가이드
- 메모리 미업데이트 금지사항
- `/memory` 명령 사용법
- 메모리 사용 베스트 프랙티스

---

## 파일 구조

### 새로 생성된 파일
```
libs/cli/deepagents_cli/
├── memory_manager.py              # MemoryManager 클래스 (622줄)
└── tests/unit_tests/
    └── test_memory_manager.py     # 테스트 스위트 (214줄)
```

### 수정된 파일
```
libs/cli/deepagents_cli/
├── command_registry.py            # /memory 명령 등록 (81-82줄)
├── system_prompt.md               # 메모리 시스템 가이드 추가 (202-237줄)
└── app.py
    ├── import datetime 추가
    ├── _handle_command 메서드 수정 (2848-2849줄)
    └── _handle_memory_command 메서드 추가 (2860줄부터 ~120줄)
```

---

## 사용 방법

### 1. 학습 추가
```bash
deepagents
# CLI 시작 후
/memory add "Python best practice: Always use type hints"
/memory add "FastAPI는 async 기본 지원으로 성능 우수"
```

### 2. 학습 검색
```bash
/memory search "python"
# 또는
/memory search "async"
```

### 3. 프로필 확인
```bash
/memory profile
```
출력 예:
```
Developer Profile:
  Name: Developer
  Role: Software Developer
  Experience: mid
  Languages: python, javascript
  Frameworks: fastapi, react
  Updated: 2026-04-06
```

### 4. 메모리 내보내기
```bash
/memory export
```
출력: 지정된 경로에 JSON 파일 생성

### 5. 통계 조회
```bash
/memory stats
```
출력 예:
```
Memory Statistics:
  Learnings: 5
  Entities: 3
  Relationships: 2
  Database Size: 0.05 MB
  Location: /home/user/.deepagents/memory

  By Category:
    best_practice: 4
    knowledge: 1
```

---

## 개발 상세

### 핵심 설계 결정

1. **SQLite 선택**
   - 가볍고 로컬 저장에 적합
   - 지속성과 트랜잭션 보장
   - 인덱싱으로 검색성능 최적화

2. **JSON 프로필**
   - 간단한 구조로 개발자 정보 저장
   - 수동 편집 가능

3. **TypedDict 사용**
   - 런타임 타입 검증
   - IDE 자동완성 지원

4. **비동기 처리**
   - `asyncio.to_thread()`로 DB 작업 논블로킹
   - UI 반응성 보장

5. **메모리 원본 보존**
   - Immutable 학습 기록
   - 검증 필드로 신뢰도 추적

### 성능 최적화

**인덱싱**:
- `learnings(source)`, `learnings(category)`
- `entities(type)`
- `relationships(from_entity)`, `relationships(to_entity)`

**검색 쿼리**:
- LIKE 패턴 검색 (콘텐츠, 태그)
- 필터 조건 조합 (source, category)
- LIMIT으로 결과 개수 제한

---

## 테스트

### 테스트 커버리지 (9개 테스트)

#### 1. `test_initialization`
- MemoryManager 초기화 확인
- DB 파일 생성 검증

#### 2. `test_load_or_create_profile`
- 프로필 로드/생성 기능
- 기본값 확인

#### 3. `test_save_profile`
- 프로필 저장
- 필드 업데이트 검증

#### 4. `test_add_learning`
- 학습 추가
- 학습 ID 반환 확인

#### 5. `test_search_learnings`
- 기본 검색
- 결과 필터링

#### 6. `test_search_learnings_empty`
- 검색 결과 없음
- 빈 리스트 반환

#### 7. `test_search_learnings_with_filters`
- 카테고리 필터
- 소스 필터

#### 8. `test_add_entity & get_related_entities`
- 엔티티 추가
- 관계 추가
- 관련 엔티티 조회

#### 9. `test_export_memory`
- JSON 내보내기
- 파일 생성 확인
- 내용 검증

### 테스트 실행
```bash
cd libs/cli
uv run pytest tests/unit_tests/test_memory_manager.py -v
```

---

## 향후 개선사항

### Phase 2 계획 (다음 세션)

#### 1. Skills 카테고리 분류 체계
- 도메인 지식 / Coding 스킬 / 레시피 분류
- SKILL.md에 `category`, `priority`, `auto_load` 필드 추가
- 카테고리별 필터링 및 로딩

#### 2. SubAgent 동적 호출
- `spawn_agent` 도구 구현
- 런타임에 서브에이전트 동적 생성
- `DynamicSubAgentRegistry` 구현

#### 3. 메모리 고급 기능
- LLM 기반 학습 자동 요약
- 지식 그래프 시각화
- 학습 연관성 분석
- 우선순위 기반 추천

#### 4. 통합 개선
- 에이전트 응답에 관련 메모리 자동 주입
- 세션 간 메모리 활용
- 메모리 기반 프롬프트 최적화

---

## 주요 메트릭

| 항목 | 수치 |
|-----|-----|
| 총 코드 라인 | 1,408 |
| memory_manager.py | 622 |
| test_memory_manager.py | 214 |
| command_registry.py 수정 | 10 |
| system_prompt.md 수정 | 36 |
| app.py 수정 | ~150 |
| 테스트 케이스 | 9 |
| 데이터베이스 테이블 | 3 |

---

## 문제해결

### Q: 메모리 파일이 생성되지 않음
**A**: `~/.deepagents/` 디렉토리 권한 확인
```bash
mkdir -p ~/.deepagents/memory
chmod 755 ~/.deepagents/memory
```

### Q: 학습 검색이 느림
**A**: 데이터가 많을 경우 LIMIT 조정
```bash
/memory search "query"  # 기본 5개 반환
```

### Q: 프로필 초기화
**A**: 프로필 파일 삭제 후 재생성
```bash
rm ~/.deepagents/memory/developer_profile.json
/memory profile  # 새로 생성됨
```

---

## 참고 자료

- **메모리 저장 위치**: `~/.deepagents/memory/`
- **시스템 프롬프트 섹션**: `libs/cli/deepagents_cli/system_prompt.md` (202-237줄)
- **테스트 실행**: `make test` 또는 `pytest tests/unit_tests/test_memory_manager.py`
- **코딩 표준**: AGENTS.md 참조

---

**작성자**: AI Assistant
**마지막 업데이트**: 2026-04-06
**상태**: ✅ 프로덕션 준비 완료
