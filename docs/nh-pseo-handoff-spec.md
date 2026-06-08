# US 요양원 데이터 유틸리티 pSEO — Claude Code 핸드오프 spec

> 상태: 기획 합의 완료 → Claude Code 실행 대기
> 작성 기준일: 2026-06-07
> 코드명: **NH-Data** (영문 브랜드/도메인 미확정 — §10 참조)
> 데이터: CMS Provider Data Catalog (Public Domain, 미국 정부 저작물)

---

## 0. 합의 요약 (3인 페르소나 리뷰 통합안)

| 결정 | 내용 |
|---|---|
| 정체성 | **공공데이터 유틸리티 툴** (콘텐츠/블로그 ❌). 구조화 표·비교·점수가 본체, AI 텍스트는 최소·사실 보조 |
| 리드 버티컬 | 요양원 (skilled nursing / nursing home), 미국·영어 |
| moat | CMS 6개 테이블 → 파생 신호(백분위·추세·deficiency 심각도·SFF 플래그). 복합지수는 v1 보류 |
| 수익화 | **AdSense 먼저** (enforcement/violation 페이지에 고CPC 법률 광고가 자동 유입) → 법률 리드젠 CPA → (먼 훗날) 시니어 리빙. **Medicare Advantage 리드 제외** (TCPA/CMS TPMO 규제) |
| 신뢰 | 실명 리뷰어 + 방법론 공개 + CMS 출처·기준일 + 정정 정책 (YMYL 생존 조건) |
| 램프 | 인구 많은 몇 개 주 → 전국. 시설+위치 MVP → 파생 → enforcement/법률 → CPA/전국 |

**가장 큰 전략 전환:** 수익 알파가 "시니어케어 CPA"가 아니라 **"enforcement 데이터 기반 고CPC AdSense(엘더로/PI 변호사 광고)"** 라는 점.

---

## 1. 프로젝트 개요

- **한 줄 정의:** 미국 요양원을 CMS 공공데이터로 비교·진단하게 해주는, Care Compare보다 나은 데이터 인터페이스.
- **타깃:** 부모/배우자의 요양원을 알아보는 미국 성인 자녀(adult-child caregiver) + 부수적으로 엘더로 변호사·연구자.
- **핵심 차별:** 별점 재노출 ❌ → 남이 안 보여주는 **파생 신호 + 위반/처분 투명성 + 비교**.
- **북극성 지표:** 인덱싱된 유틸리티 페이지의 organic 세션 → AdSense RPM.
- **경쟁 현실(직시):** Care Compare(원본), Caring.com, Healthgrades는 헤드텀 강자. **승부처는 헤드텀 ❌, 롱테일 + enforcement + 비교 + 의사결정 지원 ✅**. 헬스케어 YMYL은 트래픽 트랙션까지 6~12개월 가정.

---

## 2. 데이터 레이어 (Layer 1)

### 2.1 출처·라이선스
- CMS Provider Data Catalog. 미국 정부 저작물 = **Public Domain → 재배포 합법.** 라이선스 게이트 통과.
- 표기 의무는 없으나 신뢰(E-E-A-T) 목적상 **"출처: CMS, 기준일 YYYY-MM" 명시는 필수.**

### 2.2 API 구조 (검증 완료)
- Base URL: `https://data.cms.gov/provider-data/`
- Datastore Query 엔드포인트: `api/1/datastore/query/{datasetID}/0`
  - `datasetID`는 데이터 리프레시 간 **불변**, distribution index는 **항상 0**.
- 필터: `conditions[n][property]` / `conditions[n][value]` / `conditions[n][operator]` (JSON → query string 변환).
- 페이징: `size` & `offset`, **최대 페이지 5000행.**
- 토픽별 데이터셋 목록: Metastore `api/1/search` 엔드포인트.
- 조인 불가(API 레벨) → **테이블별로 받아 CCN 키로 우리 DB에서 조인.**

### 2.3 대상 데이터셋
| 테이블 | datasetID | 용도 | 상태 |
|---|---|---|---|
| Provider Information | `4pq5-n9py` | 마스터: 5-star(overall/health/staffing/QM), 병상, 소유유형, 위치, 거주자수 — 시설당 1행 | ✅ 확인 |
| Health Deficiencies | `r5ix-sfxw` | 점검 위반(F-tag)·심각도(scope/severity)·일자 (~3년) | ✅ 확인 |
| Penalties | TBD | 행정처분(CMP 벌금)·지불거부 | ⚠ Phase 0 검증 |
| Ownership | TBD | 시설별 소유구조 | ⚠ Phase 0 검증 |
| Quality Measures (MDS/claims) | TBD | 세부 품질지표 | ⚠ Phase 0 검증 |
| State/National Averages | TBD | 주·전국 평균(백분위 계산 재료) | ⚠ Phase 0 검증 |
| Special Focus Facility (SFF + 후보) | TBD | 문제·학대 적발 시설 플래그 | ⚠ Phase 0 검증 |

> ⚠ TBD ID는 절대 추측 금지. Phase 0에서 `api/1/search`(토픽=Nursing homes)로 실제 ID·필드명 매핑 후 확정.

### 2.4 ETL / 스냅샷 / 백필
- 각 월간 리프레시를 **스냅샷 보관**(추세 계산용). CMS 아카이브가 과거 버전을 제공하므로 **런칭 시 백필 → 추세 1일차부터 작동.**
- 파이프라인: API fetch(페이징 5000) → 정규화 → CCN 키 조인 → 파생 신호 계산 → Turso 적재 → 빌드.
- 갱신 주기: 요양원 데이터는 대략 월간. **Vercel Cron 월간 잡** + diff로 변경 시설만 재빌드.

---

## 3. 파생 신호 (Layer 2 — moat)

모두 **사실 기반**(의견 아님)이라 YMYL 리스크 낮음. 각 시설/위치 페이지에 노출.

1. **로컬 백분위:** State/National Averages 대비 시설의 staffing·QM·위반수 백분위. 예) "이 시설은 카운티 내 staffing 상위 8%".
2. **추세(trajectory):** 3년 스냅샷 기반 등급/지표 변화. 예) "18개월간 overall 4★ → 2★ 하락".
3. **Deficiency 심각도 점수:** F-tag별 scope/severity를 가중 합산 → 평이한 영어 라벨(예: "최근 점검에서 심각 위반 2건"). 원본은 raw 표만 제공 → **여기가 핵심 차별.**
4. **리스크 플래그:** SFF/SFF 후보/학대 적발 여부를 명시적 배지.
5. **복합지수(자체 종합 점수):** **v1 보류.** YMYL에서 블랙박스 점수는 신뢰 독. 도입 시 방법론 100% 공개 + 보수적 설계 조건.

> 모든 파생 신호는 "계산 로직 + 입력 데이터 + 기준일"을 방법론 페이지에서 공개.

---

## 4. 페이지 아키텍처

### 4.1 URL 구조 (예시)
```
/                                  홈 (검색 진입)
/state/{state}                     주 집계
/state/{state}/{county}            카운티 집계
/city/{state}/{city}               도시 집계
/facility/{ccn}/{slug}             시설 상세 (핵심)
/compare/{ccn-a}-vs-{ccn-b}        1:1 비교
/best/{filter}/{geo}               의도형 필터 (게이트 대상)
/methodology                       방법론·데이터 출처
/about , /corrections              편집주체·정정정책
```

### 4.2 페이지 타입
- **시설 상세(~15,000):** 5-star + 파생 신호 4종 + 위반/처분 타임라인 + 비교 CTA. **데이터가 시설마다 실제로 달라 thin-dup 위험 낮음.**
- **위치 집계(주/카운티/도시):** 해당 지역 시설 랭킹·평균·분포. 실수요 있는 geo만.
- **의도형 필터(`/best/...`):** "Medicaid 수용 + 4★+", "위반 0건 [카운티]" 등. **조합형 near-dup 위험 최다 → 실수요(검색량) + 최소 결과 수 임계치로 게이트.**
- **비교 페이지:** 고의도. 무한 조합 인덱싱 금지 → 수요 있는 쌍만 인덱스.

### 4.3 스키마 마크업
- `MedicalBusiness`/`Organization` + `address`/`geo`, `AggregateRating`(CMS 출처 명시), `Dataset`/`isBasedOn` → CMS. `BreadcrumbList`. (별점 스키마는 CMS 출처를 분명히.)

---

## 5. SEO / 콘텐츠 전략

- **툴 포지셔닝:** 페이지는 article이 아니라 tool. 표·비교·점수가 주, **AI 산문은 최소·사실 보조**(HCU 킬존 회피).
- **타깃 쿼리군:**
  - 시설명 직접형: "{facility} reviews / inspection / violations"
  - 의도형 롱테일: "nursing homes accepting medicaid in {city} 4 star", "nursing homes with no violations {county}"
  - **enforcement형(고가치):** "nursing homes cited for abuse in {state}", "{facility} penalties"
  - 비교형: "{A} vs {B}"
- **E-E-A-T 스캐폴딩:** 실명 리뷰어(노인복지/간호 자격) · 방법론 공개 · CMS 출처+기준일 · 편집주체 About · 정정 정책.

---

## 6. 수익화

| 단계 | 모델 | 비고 |
|---|---|---|
| 1차 | **Google AdSense (Auto Ads)** | enforcement/violation 페이지에 **엘더로·PI 변호사 고CPC 광고가 자동 유입** → RPM 상방. 헬스케어/시니어 RPM 자체도 최상위 |
| 2차 | **법률 리드젠 CPA** | 엘더로/요양원 소송 리드. Medicare 리드보다 규제 가볍고 단가 높음 |
| 3차(먼 훗날) | 시니어 리빙 추천 | assisted living은 요양원과 별개 카테고리. funnel로 연결 |
| 제외 | Medicare Advantage 리드 | TCPA·CMS TPMO 규제로 후순위/제외 |

- AdSense는 **트래픽 검증 후** 신청(YMYL 심사 대비 §7 신뢰요소 선행).
- CPA는 트래픽 확보 후 신중 도입. 사이트 1차 정체성은 **"가족용 신뢰 툴"** 유지 → ambulance-chaser화 방지(중립 톤).

---

## 7. 신뢰 / 컴플라이언스

### 7.1 YMYL E-E-A-T
- 실명 편집 주체 + 자격 보유 리뷰어 + 방법론 페이지 + CMS 출처/기준일 + `/corrections` 정정 정책.

### 7.2 표현 리스크 (명예훼손)
- "학대 적발" 등은 CMS 공개기록 → 리스크 낮음. **방어막 = "출처: CMS, 기준일" 병기 + 중립·사실 프레이밍 + 정정 절차.** 평가·단정 어휘 금지, 데이터 인용만.

### 7.3 Scaled Content Abuse 대응 (AdSense 핵심 리스크)
- **웨이브/램프 발행** (1일차 대량 인덱싱 금지).
- **신규 사이트 7일 dry run** 후 인덱싱.
- **dedup**: cosine similarity / n-gram Jaccard 임계치 — 특히 위치·필터 페이지.
- **차별화 임계치**: 각 페이지 고유 데이터 최소 기준 미달 시 noindex.
- **human review queue**: 자동 발행 전 표본 검수.
- 필터/비교 페이지는 **실수요 + 최소 결과 수** 게이트.

---

## 8. 기술 스택 / 아키텍처 (표준 스택)

- Frontend/배포: **Next.js 15 App Router + Vercel Pro**, pnpm.
- DB: **Turso (libSQL) + Drizzle ORM** — CMS 정규화 테이블 + 스냅샷 히스토리 + 파생 신호 사전계산.
- 자동화: **Vercel Cron**(월간 ETL/리프레시) + diff 재빌드.
- 렌더링: 시설/위치는 SSG(ISR) 위주, 비교는 on-demand.
- 검색엔진 통보: 사이트맵 lastmod 정확화 + IndexNow.
- 분석: GSC + GA4 + AdSense.

---

## 9. 로드맵 / 발행 램프

- **Phase 0 (검증·준비):**
  - `api/1/search`로 미확정 dataset ID·필드명 매핑 확정 (Penalties/Ownership/QM/Averages/SFF).
  - 영문 도메인/브랜드 확정 (§10).
  - 실명 리뷰어 영입(자격).
  - 아카이브 백필 범위 결정.
- **Phase 1 (MVP):** ETL + 시설 상세 + 위치 집계, **인구 많은 2~3개 주만**. 7일 dry run 후 램프 인덱싱. AdSense 신청.
- **Phase 2 (moat):** 파생 신호 4종 + 비교 페이지 + 방법론 페이지.
- **Phase 3 (수익 강화):** enforcement 페이지군 강화 → 고CPC 법률 광고 최적화 → 법률 리드젠 CPA 검토.
- **Phase 4 (확장):** 전국 주 확대 + (조건부) 복합지수 + 시니어 리빙 funnel.

---

## 10. 리스크 & Open Questions

1. **도메인/브랜드 미확정** — 영문 독립 브랜드 필요. 후보 도출 여부 결정 필요.
2. **실명 리뷰어 영입** — YMYL 핵심 병목. 자격 보유자 확보 경로 미정.
3. **CPA 네트워크 선정** — 엘더로/법률 리드젠 네트워크 실사 필요(Phase 3).
4. **경쟁** — Caring.com/Healthgrades 헤드텀 우위. 롱테일·enforcement·비교로 우회 전제.
5. **CMS 방법론 변경** — CMS가 staffing·QM 산정식을 주기적으로 개정(MDS 변경 등) → 파생 신호 산식이 영향받을 수 있음. ETL에 버전 인지 로직 필요.
6. **복합지수** — 도입 시 YMYL 신뢰/방법론 부담. v1 보류 유지 권장.

---

## 부록 A — Phase 0 즉시 액션
- [ ] Metastore `api/1/search` (토픽: Nursing homes including rehab services)로 7개 테이블 ID·필드 dump
- [ ] `4pq5-n9py`, `r5ix-sfxw` 실제 필드명 확인 (예: `cms_certification_number_ccn`, `overall_rating`, scope/severity 컬럼)
- [ ] 아카이브에서 추세용 과거 스냅샷 확보 가능 기간 확인
- [ ] 도메인/리뷰어/CPA 후보 리서치 착수
