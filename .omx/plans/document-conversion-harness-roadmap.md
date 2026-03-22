# 문서 변환 하네스 + 점진적 품질개선 계획

## Requirements Summary
- 목표는 원본문서와 UI 싱크가 최대한 일치하는 **편집 가능한 HTML**을 만드는 변환 파이프라인을 구축하는 것이다.
- 파이프라인은 단순 1회성 변환기가 아니라, **문서를 하나 처리할 때마다 하네스와 에이전트가 같이 발전**하도록 설계해야 한다.
- 현재 저장소에는 소스 HWP 1건(`260121 일일 주요경제지표.hwp`)과 참조 산출물(`today_major_economy/`)이 있으며, 아직 범용 실행 파이프라인/평가 하네스 코드는 없다.
- 첫 마일스톤은 **현재 HWP 샘플 1건을 기준 케이스(golden case)로 고정**하고, 구조는 이후 PDF/DOCX/DOCS 어댑터를 추가할 수 있게 잡는다.

## Evidence Snapshot
- 소스 문서: `260121 일일 주요경제지표.hwp`
- 현재 HTML 산출물은 편집용 toolbar, `data-table-id`, `data-semantic-field`를 이미 포함하고 있어 하네스의 초기 대상 포맷으로 적합하다 (`today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.html:12671-12755`).
- 공통 스타일 토큰과 폰트 스택이 별도 CSS로 분리되어 있어, 공통 레이어와 문서별 fit 레이어를 나누는 전략이 유효하다 (`today_major_economy/daily_economic_indicators_common.css:1-25`, `today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.css:1-31`).
- 현재 fit CSS는 summary/table/dense appendix별로 미세 조정 토큰을 운영하고 있어, 자동화 대상은 “생성 → 측정 → 보정” 루프여야 한다 (`today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.css:33-240`).
- 추출 JSON은 semantic field와 table cell 좌표를 함께 들고 있어, 시각 품질뿐 아니라 구조적 품질도 하네스에서 검증 가능하다 (`today_major_economy/extracted_fields.json:1-120`).
- 폰트 자산이 이미 번들되어 있어 초기 fidelity 검증은 현 저장소 내부 자산만으로도 일부 가능하다 (`today_major_economy/assets/fonts/*.woff2`).

## Scope
- 현재 기준: 1개 소스 문서 + 5개 핵심 참조 산출물(HTML, common CSS, fit CSS, fields JSON, tokens JSON)
- Estimated complexity: HIGH
- 비목표(1차): 모든 문서 포맷 동시 지원, 완전 무인 자동 수정, 대규모 서비스 배포

## Acceptance Criteria
1. 단일 명령/단일 진입점으로 **입력 문서 1건을 케이스 단위로 실행**할 수 있어야 한다.
2. 각 실행 결과는 최소한 다음 산출물을 남겨야 한다: 원본 참조 렌더, 생성 HTML/CSS, 구조화 JSON, 평가 리포트, 실행 메타데이터.
3. 평가 하네스는 최소 3개 품질축을 수치 또는 체크리스트로 기록해야 한다: **visual fidelity / structural fidelity / editability**.
4. 현재 샘플 문서에서 `extracted_fields.json`에 정의된 semantic/table mapping이 결과 리포트와 연결되어야 한다.
5. 새 문서를 추가하면 기존 golden case도 같이 재평가되어, 개선이 기존 문서를 깨지 않았는지 확인할 수 있어야 한다.
6. 문서별 임시 patch와 재사용 가능한 공통 개선사항을 분리 기록할 수 있어야 한다.

## Implementation Steps

### 1) 케이스 기반 하네스 골격을 먼저 정의한다
**Why:** 지금 저장소는 결과물 묶음은 있지만, 반복 실행 가능한 “케이스/런” 구조가 없다.

**Plan:**
- 문서 1건을 `case` 단위로 다루는 표준 디렉터리/매니페스트 규약을 만든다.
- 현재 HWP + `today_major_economy/` 산출물을 첫 golden case로 승격한다.
- 케이스는 최소한 source, reference, generated, reports, patches, metadata 계층을 갖게 한다.

**Acceptance criteria:**
- 현재 샘플 문서를 케이스 1건으로 재구성할 수 있는 디렉터리 규약이 문서화된다.
- 케이스 매니페스트에서 소스 파일, 참조 HTML/CSS, 폰트, semantic/table mapping 위치를 모두 역참조할 수 있다.
- 이후 문서를 추가할 때 코드 변경 없이 케이스 추가만으로 하네스 입력이 가능해야 한다.

### 2) 변환 파이프라인을 “어댑터 + 공통 IR” 구조로 나눈다
**Why:** 사용자 목표는 문서를 처리할 때마다 하네스와 에이전트를 발전시키는 것이므로, 포맷별 파서와 공통 품질 루프를 분리해야 한다.

**Plan:**
- 입력 어댑터(HWP 우선)와 공통 intermediate representation(IR)을 분리한다.
- IR에는 block, table, typography token, semantic field, asset/font, page/layout anchor를 포함한다.
- 현재 HTML의 `data-table-id` / `data-semantic-field`와 `extracted_fields.json`을 IR 검증의 기준면으로 사용한다.

**Acceptance criteria:**
- IR이 현재 문서의 title box, summary bars, market tables, dense appendix tables를 모두 표현할 수 있다.
- HWP 어댑터 출력이 IR 검증 규칙을 통과하거나, 실패 시 어떤 정보가 비는지 리포트에 남는다.
- 향후 PDF/DOCX/DOCS는 새 어댑터 추가로 연결 가능하고 공통 evaluator는 재사용된다.

### 3) 생성 경로를 “기본 생성 + fit layer” 2단계로 설계한다
**Why:** 현재 산출물도 common CSS와 fit CSS가 분리되어 있고, 실제 fidelity 개선은 대부분 fit layer에서 일어난다.

**Plan:**
- 1차 생성기는 편집 가능한 HTML + 공통 CSS를 만든다.
- 2차 fit 단계는 문서별/섹션별 토큰과 patch를 적용해 UI 싱크를 올린다.
- fit 결과는 공통 승격 가능 여부를 함께 판정해, 재사용 가능한 개선은 common layer로 이동시키고 문서특화 수정만 fit layer에 남긴다.

**Acceptance criteria:**
- 생성 산출물에서 base/common 레이어와 document-specific fit 레이어가 명시적으로 분리된다.
- fit 단계가 수정한 항목은 토큰/patch 로그로 남고, 어떤 변경이 공통화 후보인지 분류된다.
- 결과 HTML은 계속 contenteditable/field-aware 상태를 유지한다.

### 4) 평가 하네스를 시각/구조/편집성 3축으로 구축한다
**Why:** “원본과 최대한 동일”은 감각적 표현이라서, 점진 개선을 위해서는 측정 가능한 실패 모드로 바꿔야 한다.

**Plan:**
- visual fidelity: 원본 참조 렌더와 생성 HTML 렌더의 페이지 단위/영역 단위 diff를 남긴다.
- structural fidelity: table count, cell map, semantic field coverage, token coverage를 체크한다.
- editability: 주요 블록이 편집 가능한지, 편집 후 구조가 깨지지 않는지, JSON export/import가 가능한지 점검한다.
- 결과는 문서 전체 점수 + 섹션/테이블별 hotspot 목록으로 정리한다.

**Acceptance criteria:**
- 각 실행(run)마다 full-page 비교, hotspot 목록, field coverage, editability 체크 결과가 리포트로 남는다.
- `stock_summary`, `stock_table` 등 `data-table-id` 단위로 문제 구간을 특정할 수 있다.
- 실패는 “어느 축에서 왜 실패했는지”를 에이전트가 후속 조치 가능한 형태로 남긴다.

### 5) 에이전트 개선 루프를 하네스에 내장한다
**Why:** 사용자가 원하는 핵심은 문서를 변환할 때마다 하네스와 에이전트가 같이 좋아지는 구조다.

**Plan:**
- 하네스 출력(visual diff, hotspot, 구조 누락, patch 로그)을 에이전트의 입력 컨텍스트로 표준화한다.
- 에이전트는 실패 유형별로 다음 액션을 제안한다: extractor 보정, token 조정, layout patch, 공통화 승격, 수동 검토 요청.
- 새 문서를 추가할 때마다 기존 golden cases 전체를 회귀 실행하여, “새 문서 대응이 기존 문서를 악화시켰는지”를 확인한다.

**Acceptance criteria:**
- 실행 결과로부터 다음 개선 액션 목록이 자동 생성된다.
- 개선 액션은 reusable/common, document-specific, manual-review 3가지로 분류된다.
- 새 케이스 추가 후 기존 케이스 회귀 결과가 함께 기록되어, 개선/퇴보 추세를 비교할 수 있다.

## Risks and Mitigations
- **리스크:** 원본 렌더 기준면이 없으면 visual fidelity 평가가 흔들린다.
  - **대응:** 원본 문서 렌더 캡처를 케이스의 필수 산출물로 승격한다.
- **리스크:** 문서별 임시 CSS patch가 누적되면 범용성이 무너진다.
  - **대응:** common layer와 fit layer를 강제로 분리하고, patch를 reusable/document-specific로 태깅한다.
- **리스크:** 시각 싱크만 맞추고 편집성이 깨질 수 있다.
  - **대응:** visual score와 별개로 contenteditable, field binding, export/import 체크를 필수 품질축으로 둔다.
- **리스크:** 새 문서 최적화가 기존 문서를 깨뜨릴 수 있다.
  - **대응:** 케이스 회귀군(regression corpus)을 유지하고 모든 개선에 대해 재실행한다.

## Verification Steps
1. 현재 HWP 샘플을 golden case 1호로 등록한다.
2. 원본 렌더 / 생성 HTML 렌더 / 구조 JSON / 평가 리포트가 한 run 아래 함께 생성되는지 확인한다.
3. `extracted_fields.json`의 semantic/table mapping 일부를 샘플링해 evaluator 리포트와 연결되는지 확인한다.
4. `stock_summary`, `stock_table`, dense appendix table 최소 1개씩을 hotspot 단위로 리포트할 수 있는지 확인한다.
5. 새 케이스 1건 추가 시 기존 golden case가 자동 재평가되는지 확인한다.

## Recommended First Milestone
- 범용 멀티포맷보다 **HWP-first + 확장 가능한 어댑터 경계**로 시작한다.
- 현재 문서에서 우선 잠가야 할 것은 다음 4가지다:
  1. 케이스/런 규약
  2. 원본 렌더 기준면 확보
  3. visual/structural/editability evaluator
  4. common vs fit patch 승격 규칙
- 이 4가지를 먼저 고정해야 이후 PDF/DOCX/DOCS 확장이 “새 어댑터 추가” 문제가 된다.

## Deliverables
1. 케이스 기반 변환 하네스 설계안
2. fidelity 평가 리포트 규격
3. 에이전트 개선 루프/회귀 운영 규칙

## Handoff Notes
- 이 계획은 **HWP 샘플 1건을 golden case로 삼아 하네스를 먼저 세운 뒤, 포맷 확장과 자동 개선을 올리는 전략**을 전제로 한다.
- 만약 1차부터 HWP/PDF/DOCX 동시 지원이 필요하면, Step 2의 어댑터 설계와 Step 4의 evaluator 범위를 더 넓혀 재계획해야 한다.
