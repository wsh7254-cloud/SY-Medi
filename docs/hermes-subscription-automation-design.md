# Hermes 기반 마케팅 자동화 설계서 — 구독 활용·연결 방식·비용 구조·설치 순서

- 조사·작성일(모든 공식 문서·가격·정책 확인일): **2026-09-30**
- 대상 제품: **Hermes Desktop** (Nous Research), 확인 버전 **v2026.9.24** (2026-09-24 태그)
- 전제: ChatGPT Pro + Claude Pro 구독 중, API 결제·크레딧 없음, 개인 PC 24시간 운영, 사람 승인 후 게시
- 이전 설계서 [`docs/content-system-design.md`](content-system-design.md)(2026-09-28)는 n8n + 유료 API 전제였습니다. 이 문서는 **"추가 LLM 비용 0 + Hermes"** 조건으로 다시 설계했습니다. 법규·근거 검증 기준(이전 문서 부록 A·B·C)은 그대로 씁니다.

### 표기 규칙

| 표시 | 뜻 |
|---|---|
| **[공식]** | 공식 문서·공식 저장소·공식 도움말에서 이번에 직접 확인한 사실 |
| **[보도]** | 공식 페이지에 접속하지 못해 검색 요약·언론 보도로만 확인 (사용 전 공식 페이지 재확인 필요) |
| **[설계]** | 제 설계 제안 (사실이 아님) |
| **[추정]** | 가정에 기반한 판단·계산 |
| **[확인 필요]** | 확정하지 못한 항목 |

> 조사 환경 제약: 이번 조사 환경에서 `hermes-agent.nousresearch.com`, `openai.com`, `help.openai.com`, `developers.openai.com` 접속이 막혀 있었습니다. Hermes는 **공식 GitHub 저장소에 들어 있는 문서 원본**(웹사이트와 같은 파일)으로 확인했고, OpenAI 정책·한도는 **검색 요약과 보도**로만 확인했습니다. 그래서 OpenAI 관련 항목에는 [보도]·[확인 필요]가 많습니다.

---

## 0. 결론 — 현재 두 Pro 구독만으로 원하는 구성이 가능한가?

**조건부로 가능합니다. "ChatGPT Pro가 주력 두뇌, Claude Pro는 보조 검수"로 구성할 때만 추가 LLM 비용 0이 성립합니다.**

| 질문 | 답 | 근거 |
|---|---|---|
| ChatGPT Pro로 Hermes의 두뇌(LLM)를 돌릴 수 있나? | ✅ 가능. Hermes가 공식 지원하는 **"ChatGPT or Codex Subscription"** 로그인 | [공식] Hermes 공급자 문서 |
| 그때 추가 요금이 붙나? | 토큰당 청구 없음. ChatGPT 요금제의 **Codex·Work 사용량**에서 차감. 한도에 닿으면 멈춤(크레딧 사용을 직접 허용하지 않는 한) | [보도] OpenAI 도움말 검색 요약. Hermes 문서에는 "차감 방식 미기재" |
| Claude Pro를 Hermes에 직접 연결할 수 있나? | ❌ **불가.** Hermes의 Anthropic 로그인은 Claude **Max + 유료 추가 사용량**에서만 동작하고 Pro는 안 됨 | [공식] Hermes 문서, Anthropic 약관 |
| Claude Pro를 쓸 방법은 전혀 없나? | ⚠️ Hermes가 **공식 Claude Code(`claude -p`)를 도구처럼 실행**하면 Pro 한도에서 차감됨. 한도가 작고 정책이 바뀔 수 있어 **검수 2차 의견 같은 보조 역할만** 권장 | [공식] Anthropic 도움말(2026-06-15 공지), Claude Code 법적 고지 |
| 이미지·영상은? | LLM 구독과 별개. **웹 구독 ≠ API 권한**. 1단계는 사람이 웹에서 생성(추가 LLM 비용 0), 2단계에서 원하면 API 선불(허용하신 제작 비용) | [보도] Kling·Seedance, [공식] Hermes 도구 문서 |
| 24시간 무인 운영이 되나? | 됨. 단 "완전 무인"은 아님: 재부팅 후 Windows 로그인, 로그인 만료 시 재로그인, 사용량 한도 도달 시 대기가 필요 | [공식] Hermes Windows·cron 문서 |
| 승인 전 게시를 막을 수 있나? | 1단계는 자동화 PC에 **SNS 게시 권한 자체를 주지 않아** 구조적으로 불가능하게 만듦 | [설계] |

### 가능한 범위와 불가능한 범위

| 구분 | 내용 |
|---|---|
| ✅ 가능 (추가 LLM 비용 0) | 자료 수집 → 기획 → 원고 → 이미지·영상 **제작 지시서** → 검수 → 승인 요청 → 게시 패키지 → 게시 기록 |
| ⚠️ 제한 | 처리량 = ChatGPT Pro 주간 사용량 중 본인이 직접 쓰는 몫을 뺀 나머지. 한도에 닿으면 **자동으로 기다림**(유료로 넘어가지 않게 설정) |
| ❌ 불가 | Claude Pro를 Hermes의 기본 두뇌로 쓰기 / 네이버 블로그·클립 자동 게시(공식 글쓰기 API 없음, 이전 설계서) / 웹 구독 크레딧으로 Kling·Seedance API 자동 호출 |
| ❓ 확인 필요 | OpenAI가 **Hermes의 ChatGPT 로그인 사용**을 개별적으로 허용하는지. DevDay(2026-09-29)에 발표된 "다른 앱에서 ChatGPT 요금제 사용"의 파트너 목록에서 Hermes는 확인하지 못함 |

**솔직한 평가**: "추가 LLM 비용 0"과 "24시간 안정 무인 운영"은 서로 부딪힙니다. 비용 0을 지키려면 한도에 닿았을 때 **멈추는 것**이 정답이고, 그만큼 무인 처리량은 구독 한도가 정합니다. 하루 1~2편 수준이면 충분할 가능성이 높지만 [추정], 실제 여유는 7단계 시험 운영에서 측정해야 합니다.

---

## 0-1. "Hermes Agent Desktop" 제품 확인 결과

| 항목 | 확인 결과 |
|---|---|
| 정확한 이름 | **Hermes Desktop** — Nous Research의 오픈소스 에이전트 **Hermes Agent**의 공식 데스크톱 앱 [공식] |
| 공식 저장소 | `github.com/NousResearch/hermes-agent` — MIT 라이선스(무료) [공식] |
| 공식 다운로드 | `hermes-agent.nousresearch.com` 의 Desktop 페이지 [공식 문서에 명시] |
| 최신 버전 | 태그 **v2026.9.24**(2026-09-24). 저장소 최신 수정 2026-09-29 [공식] |
| 지원 OS | Windows 10·11(네이티브), macOS(**Apple Silicon만**, Intel Mac 미지원), Linux [공식] |
| CLI와 관계 | Desktop 앱, 터미널 명령어(`hermes`), 웹 대시보드가 **같은 설정·로그인·세션**을 공유 [공식] |
| ⚠️ 혼동 주의 | `fathah/hermes-desktop`(hermesone.org)은 README에 "Nous Research와 무관한 커뮤니티 프로젝트"라고 적혀 있음. `hermes-ai.net`, `hermesaiagent.app` 등은 공식 도메인이 아님 → **여기서 설치 파일을 받지 마세요** [공식 README 문구 / 도메인 판단] |
| 이전 설계서와 차이 | 이전 문서의 "v0.15.2 공개 프리뷰(2026-06)"는 현재 날짜형 버전(v2026.9.x)으로 바뀜 |

→ **확인 요청**: 알고 계신 프로그램이 `hermes-agent.nousresearch.com`에서 받는 Nous Research 제품이 맞나요? 다른 곳에서 받으셨다면 그 링크를 알려주세요.

## 0-2. 명령어를 확정하려면 필요한 정보

이 문서의 설치 명령은 **Windows 11 기준 초안**입니다. 아래를 알려주시면 확정본으로 바꿉니다.

| # | 확인할 것 | 왜 필요한가 |
|---|---|---|
| 1 | PC 운영체제 (Windows 10/11, Mac Apple Silicon/Intel) | 설치 파일·명령이 다름. Intel Mac은 Desktop 미지원 |
| 2 | 자동화 PC가 **조제·청구 프로그램 PC와 같은지** | 같으면 환자정보 노출 위험 → 별도 PC 또는 별도 Windows 계정 필요 |
| 3 | RAM·저장공간(·로컬 AI를 쓸 경우 GPU) | 동시 실행 수, 로컬 AI 가능 여부 |
| 4 | 이미 설치된 것: Hermes Desktop / Claude Code / Git for Windows / Python | 건너뛸 단계 결정 |
| 5 | ChatGPT Pro 등급: $100(Pro 5x) / $200 / $500 | 사용량이 크게 다름 [보도] |
| 6 | 게시 채널 확정 | 프로필 기준 인스타그램·유튜브 쇼츠·네이버 블로그·클립으로 가정. Threads 포함 여부 |
| 7 | Kling·Seedance를 웹 구독 중인지, API를 쓸 의향이 있는지 | 미디어 단계 방식 결정 |
| 8 | 승인용 메신저로 **텔레그램** 사용 가능 여부 | Hermes는 카카오톡을 지원하지 않음 [공식: 지원 플랫폼 목록] |

---

## 1. 구독과 API 비용의 관계

### 1-1. 먼저 용어 (약국 업무 비유)

| 용어 | 한 줄 뜻 | 약국 비유 |
|---|---|---|
| 구독(Subscription) | 월정액으로 정해진 사용량을 쓰는 권리 | 정액 회원권. 한도 안에서는 더 안 냄 |
| API | 프로그램끼리 주고받는 창구. **쓴 만큼 청구**(종량제) | 도매상 외상장부. 가져간 만큼 월말 정산 |
| 토큰(token) | AI가 읽고 쓰는 글자 조각. API 요금의 단위 | 낱알 단위 |
| OAuth | 비밀번호를 넘기지 않고 "출입증"만 받아오는 로그인 방식 | 도매몰에 "카카오로 로그인". 출입증일 뿐 요금표가 아님 |
| 에이전트 | 모델(두뇌) + 도구 + 반복 실행 틀 | Hermes는 "틀"이고, 두뇌 값은 연결한 회사에 냄 |

**핵심**: 구독과 API는 **다른 계정·다른 결제**입니다. Claude Pro를 결제해도 Anthropic API 키 사용은 "구독과 무관한 종량제"입니다 [공식: Hermes 문서·Anthropic 도움말]. ChatGPT Pro도 OpenAI API(Platform) 결제와 별개입니다 [보도: OpenAI 공식 페이지 접속 불가].

### 1-2. ChatGPT Pro

| 항목 | 내용 | 표시 |
|---|---|---|
| 포함 권한 | ChatGPT 앱 + **Codex**(OpenAI의 코딩 에이전트: CLI·IDE·웹) + ChatGPT Work 사용량 | [보도] |
| API 권한 | 포함 안 됨. OpenAI Platform API는 별도 계정·선불 결제. Hermes에서도 별도 공급자(`OPENAI_API_KEY`)로 구분 | [보도] / [공식: Hermes 공급자 표] |
| Hermes에서 쓰는 법 | `hermes model` → **ChatGPT or Codex Subscription** (기기 코드 로그인). 접속처는 `chatgpt.com/backend-api/codex` | [공식: Hermes 문서·소스 코드] |
| 어디서 차감되나 | ChatGPT 요금제의 **Codex(및 Work) 사용량**. Hermes 문서는 "요금제별 차감 방식은 아직 문서화되지 않음"이라고 명시 | [공식: Hermes] / [보도: OpenAI] |
| 새 정책 (2026-09-29 DevDay) | "다른 앱·사이트에서 ChatGPT 요금제 사용": Plus·Pro만 가능, 요청은 **Work·Codex 사용량에서 차감**, **앱별 주간 상한** 설정 가능, 한도 도달 시 멈춤(앱의 크레딧 사용을 명시적으로 허용한 경우만 크레딧 차감) | [보도: OpenAI 도움말 검색 요약] |
| 한도 구조 | 5시간 창 + 주간 한도. 보도상 **Pro 요금제는 Work·Codex에 5시간 한도 없음(주간만)**. Pro $200은 10/30부터 Plus 대비 20배 → 10배로 축소, Pro $500 신설 | [보도] |
| 등급 | Pro $100(Plus의 5배) / Pro $200 / Pro $500 | [보도] |
| 한도 초과 시 선택지 | 기다리기(리셋) / 리셋 구매 / 크레딧 구매 → **기본안은 "기다리기"만** | [보도] |
| 무엇이 가장 많이 먹나 | 상위 모델일수록 소모가 큼. 한 단계 가벼운 모델로 바꾸면 체감 한도가 크게 늘어남 | [보도] |

### 1-3. Claude Pro

| 항목 | 내용 | 표시 |
|---|---|---|
| 포함 권한 | claude.ai 웹·앱 + **Claude Code**. 둘이 같은 사용량을 공유 | [공식] |
| 한도 | **5시간마다 리셋되는 세션 한도 + 주간 한도**(모든 모델 합산) | [공식: What is the Pro plan] |
| API 권한 | 없음. API 키는 Claude Console 종량제로 별도 | [공식] |
| Hermes 직접 연결 | ❌ Pro 불가. Max + 구매한 추가 사용량에서만 동작하고, 그때도 **Max 기본 한도가 아니라 유료 추가 사용량에서만 차감** | [공식: Hermes 문서] |
| Anthropic 약관 | 구독 로그인(OAuth)은 Claude Code 등 **Anthropic 자체 앱의 일반 사용**용. 타사 앱이 구독 자격증명으로 요청을 보내는 것은 불허. 단 "**수정하지 않은 Claude Code에 본인 구독으로 로그인**"은 허용. Pro·Max 한도는 "일반적인 개인 사용"을 전제 | [공식: Claude Code 법적 고지] |
| `claude -p`(비대화형 실행) | 2026-06-15 공지: Agent SDK·`claude -p`·타사 앱 사용은 **계속 구독 한도에서 차감**. 원래 월 $20 별도 크레딧으로 분리하려던 계획은 **보류** → 다시 바뀔 수 있음 | [공식: Claude 도움말] |
| 참고 이력 | 2026-04-04부터 OpenClaw 같은 타사 에이전트는 구독 한도 대신 유료 추가 사용량으로 전환됨 | [보도: TechCrunch] |
| 한도 초과 시 | "사용량 크레딧(usage credits)"을 켜면 **표준 API 요금**으로 추가 청구 → **꺼 둠** | [공식] |
| 함정 | 컴퓨터에 `ANTHROPIC_API_KEY` 가 설정돼 있으면 Claude Code가 구독 대신 API로 청구 | [공식: Claude 도움말] |

### 1-4. 역할별 에이전트를 여러 개 돌리면 비용은?

- **Hermes 자체는 무료**(MIT 라이선스). 별도 "에이전트 요금제"는 **없고**, 에이전트 개수로 청구되지도 않습니다. [공식]
- 비용·사용량은 **공급자 계정 단위로 합산**됩니다. 역할 프로필 4개가 모두 같은 ChatGPT 계정에 로그인하면 **하나의 주간 사용량을 나눠 씁니다.** 동시에 여러 개가 돌면 그만큼 빨리 줄어듭니다. [설계·추정]
- 숨은 소모: Hermes는 요청 1번에 모델을 여러 번 부릅니다(도구 반복, 제목 생성·대화 압축·기억 정리 같은 보조 작업). 보조 작업도 기본값은 메인 모델을 씁니다. [공식]
- 계정을 여러 개 만들어 한도를 늘리는 방식은 **권장하지 않습니다**(약관 위반 소지) [확인 필요].
- Nous Portal(Nous Research의 유료 통합 구독)은 선택 사항이며 **LLM 비용이므로 기본안에서 제외**합니다. [공식: 존재, 가격 미확인]

### 1-5. 추가 LLM 비용이 새는 구멍 7개 — 기본안은 모두 막습니다

| # | 구멍 | 어떻게 생기나 | 막는 법 |
|---|---|---|---|
| 1 | 종량제 API 키 | `.env`·환경변수에 `OPENAI_API_KEY` 등이 들어감 | 만들지 않음. `health_check.py`가 매일 이름만 점검 |
| 2 | Claude 사용량 크레딧·자동 충전 | claude.ai 설정에서 켜짐 | **끔** |
| 3 | ChatGPT 크레딧·리셋 구매, 앱의 크레딧 사용 허용 | 한도 도달 시 구매 제안 | 사지 않음, 허용 안 함 |
| 4 | Hermes 대체 공급자(fallback) | 한도 도달 시 다른 유료 공급자로 자동 전환 | 설정하지 않음 (`hermes fallback list`가 비어 있어야 함) |
| 5 | 보조 모델(auxiliary)을 유료 공급자로 지정 | 설정 화면에서 바꿈 | 기본값 `auto`(메인 모델) 유지 |
| 6 | Hermes가 Claude Code 로그인을 빌려 Anthropic에 직접 연결 | 기본값 `auth.adopt_external_logins: true` | **false로 변경** (Pro에서는 동작하지도 않고 약관상 불허) |
| 7 | OpenRouter·Nous Portal 로그인 | OpenRouter는 OAuth로 로그인해도 결국 **종량제 키**가 발급됨 | 로그인하지 않음 |

---

## 2. 연결 방식별 비교

Hermes가 실제로 지원하는 경로만 비교했습니다. [공식: Hermes 공급자 문서]

| 연결 경로 | Hermes 지원 | 필요한 계정·구독 | 기존 Pro 구독 활용 | 과금 기준 | 사용량 제한 | 무인 운영 적합성 | 장단점 |
|---|---|---|---|---|---|---|---|
| ① OpenAI API 키 직접 | ✅ | OpenAI Platform 계정 + 결제 | ❌ | 토큰당 종량제 | 계정 등급·지출 한도 | 높음 | 안정적 / **추가 비용** |
| ② Anthropic API 키 직접 | ✅ | Claude Console + 결제 | ❌ | 토큰당 종량제 | 계정 등급·지출 한도 | 높음 | 안정적 / **추가 비용** |
| ③ ChatGPT 계정 로그인(OAuth) | ✅ `openai-codex` | ChatGPT Plus·Pro | ✅ | 구독 정액(Codex·Work 사용량 차감) | 주간 한도(Pro는 5시간 한도 없음 [보도]) | 중상: 한도 시 대기, 만료 시 재로그인 | **추가 비용 0** / OpenAI의 Hermes 개별 허용 [확인 필요] |
| ④ Claude 계정 로그인(OAuth) | ⚠️ Max+추가 사용량만 | Claude **Max** + 추가 사용량 구매 | ❌ (Pro 불가) | 추가 사용량 = API 요금 | – | – | Pro 사용자는 **사용 불가** |
| ⑤ 공식 CLI 경유: Codex app-server 런타임 | ✅ 선택 기능 | ChatGPT Plus·Pro + Codex CLI 설치·`codex login` | ✅ | 구독 정액(Codex 사용량) | ③과 같음 | 중: cron 공식 "미검증", 하위 에이전트·기억 도구 불가 | OpenAI 공식 프로그램을 그대로 씀(정책상 가장 보수적) / 설정 복잡 |
| ⑥ 공식 CLI 경유: Claude Code `claude -p` | ✅ 번들 스킬·터미널 | Claude Pro + Claude Code 설치 | ✅ | 구독 정액(Pro 한도, 웹 대화와 공유) | 5시간 + 주간, **작음** | 중하: "일반적 개인 사용" 전제, 정책 변경 가능성 | Claude 품질을 비용 0으로 / 보조 역할만 |
| ⑦ 모델 중계 서비스(OpenRouter, Nous Portal) | ✅ | 중계 서비스 계정 + 크레딧 또는 구독 | ❌ | 종량제 또는 별도 구독 | 서비스별 | 높음 | 모델 선택 폭 넓음 / **추가 비용** |
| ⑧ 로컬 LLM(LM Studio, Ollama, Hermes Local Models) | ✅ | 없음(PC 성능 필요) | – | 전기요금·하드웨어 | PC 성능 | 중: PC 사양 의존 | 한도 없음 / 한국어 의학 정확도·속도 한계 |

### OAuth는 "인증 방식"일 뿐 — 실제로 어디에 접속하고 무엇으로 청구되나

| OAuth 로그인 | 실제 접속처 | 적용되는 권한 | 과금 기준 |
|---|---|---|---|
| Hermes → ChatGPT 로그인(③) | ChatGPT Codex 백엔드(`chatgpt.com/backend-api/codex`) [공식: 소스] | ChatGPT 요금제의 Codex 사용량 | 구독 정액. 크레딧 허용 시 크레딧 차감 [보도] |
| Hermes → Claude 로그인(④) | Anthropic에 "Claude Code로서" 요청 [공식: Hermes] | Max 계정의 **추가 사용량** | 표준 API 요금 [공식] |
| Claude Code 자체 로그인(⑥) | Anthropic (공식 앱) | Pro 구독 사용량 | 구독 정액. 사용량 크레딧을 켜면 API 요금 [공식] |
| Hermes → OpenRouter 로그인(⑦) | OpenRouter. 로그인 결과로 **API 키가 발급**돼 저장됨 [공식: Hermes] | OpenRouter 크레딧 | 종량제 — "OAuth인데 유료"인 대표 예 |

→ **"OAuth = 무료, API 키 = 유료"가 아닙니다.** 같은 OAuth라도 ③⑥은 구독 한도, ④⑦은 종량제입니다.

**비공식 우회 연결은 쓰지 않습니다.** (예: 브라우저 화면을 자동 조작해 ChatGPT·Claude 웹을 대신 쓰게 하는 방식, 비공식 프록시, Claude 로그인 토큰을 다른 프로그램에 복사하는 방식)

---

## 3. 내 조건에 맞는 추천 구성

### 3-1. 기본안 — 추가 LLM 비용 0

```
[매일 07:00] Hermes 예약 작업(규칙 스크립트, LLM 사용 0)
   └ content_calendar.csv 에서 오늘 주제 읽기 → 칸반 카드 3장 생성(같은 날 두 번 실행돼도 중복 안 됨)
        ① researcher(자료조사)  → evidence.md
        ② writer(기획·원고·제작 지시서) → draft_*.md, media_brief.md
        ③ reviewer(검수, 선택: Claude Code 2차 의견) → review.md
[매일 12:00] 규칙 스크립트 → 텔레그램으로 진행 현황 보고
[약사] 텔레그램: "승인 검토 N" → 요약 확인 → "승인 N"          ← 승인 A (원고·제작 지시서)
   └ 이미지·영상: 1단계는 약사(또는 직원)가 Kling·Seedance 웹에서 media_brief.md 대로 생성 → 작업 폴더에 저장
[약사] 최종본 확인                                              ← 승인 B (완성본)
   └ Hermes가 채널별 "붙여넣기용 게시 패키지" 작성
[약사] 각 앱·Studio에서 직접 게시·예약 → "게시완료 N 채널 URL" → publish_log.csv 기록
[매일 21:00] 규칙 스크립트 health_check → 문제가 있을 때만 알림
```

- **칸반(Kanban)** = Hermes의 작업 게시판. 카드 1장 = 일 1건, 담당자(프로필)가 정해져 있고, 앞 카드가 끝나야 다음 카드가 시작됩니다. 모든 인수인계가 기록으로 남습니다. [공식]
- **프로필(profile)** = Hermes 안의 "직원 1명". 각자 설정·로그인·기억·직무 기술서(SOUL.md)를 따로 가집니다. [공식]
- **cron(예약 작업)** = 정해진 시각에 자동 실행되는 작업. Hermes는 **LLM 없이 스크립트만 실행하는 모드**(no-agent)를 지원해 사용량 0으로 순서를 관리할 수 있습니다. [공식]

**왜 이렇게 나눴나** [설계]
1. **순서·중복 방지·잠금은 코드(규칙)로, 판단만 AI로.** 이전 설계서의 원칙(워크플로 방식이 의약 콘텐츠에 더 안전) 그대로입니다. 오케스트레이터를 LLM으로 두면 순서를 건너뛰거나 사용량을 더 씁니다.
2. **게시 권한을 PC에 주지 않는 것이 가장 확실한 승인 잠금.** 1단계에서는 Hermes가 SNS에 게시할 방법 자체가 없습니다.
3. **유료 미디어 생성도 1단계에서는 API 키를 주지 않아** 비용이 새지 않게 합니다.

### 3-2. 역할 6개 → 프로필 4개로 운영

| 요청하신 역할 | 맡는 곳 | 이유 |
|---|---|---|
| 오케스트레이터 | **규칙 스크립트**(카드 생성·현황 보고) + **default 프로필**(결과 통합·승인 요청) | 순서는 코드가 더 확실하고 사용량 0 |
| 자료 조사 담당 | **researcher** 프로필 | 독립 판단 필요 |
| 기획·원고 담당 | **writer** 프로필 | 독립 판단 필요 |
| 이미지·영상 담당 | 지시서 = **writer**, 생성 = 1단계 **사람(웹)** / 2단계 **default**(승인 후 API) | 유료 생성은 사람이 있는 대화에서만 |
| 검수 담당 | **reviewer** 프로필 (+ Claude Code 2차 의견) | 쓴 사람과 검수자를 분리 |
| 게시·운영 담당 | **default** 프로필 | 승인은 사람과 대화하는 창구에서만 확인 가능 |

프로필을 6개로 늘릴 수도 있지만, 프로필마다 **ChatGPT 로그인·설정·기억이 따로** 생겨 관리할 것이 늘고 보조 호출도 늘어납니다. 제작량이 늘면 그때 `media`, `publisher`를 분리하세요. [설계]

Hermes 지원 여부 확인 [공식]:
- 역할별 **프로필**: 지원 (`hermes profile create`). 각 프로필에 다른 모델 지정 가능.
- **하위 에이전트**(`delegate_task`): 지원. 단 하위 에이전트 전체가 **하나의 모델**만 쓰고(작업별 모델 지정 불가), 사람 개입·재시작·기록 보존이 안 됨 → 이 설계에서는 칸반을 씀.
- **칸반 카드별 모델 지정**: 지원 (`--model` / `hermes kanban set-model`).
- **사람 개입**: 칸반은 지원(멈춤·재개·댓글), `delegate_task`는 미지원.

### 3-3. 하나의 모델 공유 vs 역할별 다른 모델

| 방식 | 구독 사용량 | 설정 복잡도 | 품질 | 판단 |
|---|---|---|---|---|
| A. 전 역할 같은 중간 등급 모델 | 중간 | 가장 쉬움 | 균일. 같은 모델이 쓰고 검수해 **같은 실수를 놓칠 수 있음** | 시작용 |
| B. 역할별 등급 조정 (조사·원고·검수 = 중간 등급, 형식 변환·요약 = 가벼운 등급) | **절약** | 약간 증가 | 핵심 단계 품질 유지 | ✅ 추천 |
| C. B + 검수에 **다른 회사 모델**(Claude Code 2차 의견) | Claude Pro 한도 추가 사용 | 증가(설치 1개) | 서로 다른 모델이 교차 확인 → 오류 상관 감소 | ✅ 추천(선택) |
| D. 최상위 모델을 전 역할에 | **매우 큼** | 쉬움 | 약간 향상 | ❌ 오버스펙, 한도 빨리 소진 |

- 모델 이름은 자주 바뀝니다. Hermes 소스의 기본 목록에는 `gpt-6-sol`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-luna` 등이 있고 [공식: 소스], DevDay에서 GPT-6.1 Sol이 발표됐습니다 [보도]. **실제 선택지는 `hermes model` 화면에 나오는 목록을 기준**으로 고르세요. [확인 필요]
- 보도된 OpenAI 기준으로 가장 무거운 모델(예: GPT-6 Astra)은 한도 소모가 가장 커서 일상 파이프라인에 쓰지 않습니다. [보도]

### 3-4. 대안 — 추가 LLM 비용이 발생 (선택하실 때만)

| 대안 | 좋아지는 점 | 비용이 필요한 이유 | 비용 구조 |
|---|---|---|---|
| 대안 1. 검수만 API 키(OpenAI 또는 Anthropic) | 구독 한도·정책 변경과 무관하게 검수가 안정적 | API는 구독과 별개 결제 | 토큰당 종량제. 콘솔에서 월 지출 한도 설정 가능 [공식: 가격은 공급자 가격표] |
| 대안 2. Claude Max + 추가 사용량 | Hermes에서 Claude를 기본 두뇌로 사용 | Hermes는 Max의 **추가 사용량**만 씀 | Max 월정액 + 추가 사용량(API 요금) [공식] |
| 대안 3. Nous Portal 구독 | 모델 300여 개 + 웹검색·이미지 도구를 로그인 1번으로 | 별도 구독 | 월 구독 [가격 확인 필요] |
| 대안 4. OpenRouter | 모델·영상 모델(Seedance 등) 선택 폭 | 크레딧 종량제 | 사용량만큼 [공식: 존재, 단가는 OpenRouter 확인] |
| 참고: 로컬 LLM (비용 0) | 한도 없음 | – | 전기요금·GPU. 의학 정확도 검증 부담이 커서 **형식 변환 같은 단순 작업에만** [설계] |

---

## 4. 역할별 모델·도구 배치

| 역할 | 담당 업무 | 추천 모델·도구 | 연결 방식 | 기존 구독 활용 | 추가 비용 발생 조건 | 추천 이유 |
|---|---|---|---|---|---|---|
| 오케스트레이터 | 카드 생성·순서 관리·현황 보고 / 결과 통합·승인 요청 | 규칙: `mk_daily_cards.py`, `daily_report.py`(LLM 없음) / 대화: default 프로필, 중간 등급 모델 | Hermes cron(no-agent) / ③ ChatGPT 로그인 | ChatGPT Pro (대화 부분만) | 대체 공급자·API 키를 설정할 때만 | 순서는 코드가 더 확실, 사용량 0 |
| 자료 조사 | 정보 수집, 출처 기록, 사실 확인 | researcher 프로필, 중간 등급 모델 + Hermes 웹검색·추출(무료 기본값) | ③ + 무료 검색 | ChatGPT Pro | 유료 검색 API 키를 넣을 때만 | 정확성이 가장 중요한 단계 |
| 기획·원고 | 채널별 문안·대본 + **이미지·영상 제작 지시서** | writer 프로필, 중간 등급 모델 | ③ | ChatGPT Pro | 없음 | 한국어 품질 + 근거 밖 주장 금지 |
| 이미지·영상 | 지시서 → 실제 생성 → 결과 취합 | 지시서: writer / 생성: 1단계 **사람이 Kling·Seedance 웹**, 2단계 Hermes `image_generate`·`video_generate`(FAL 경유 Kling) | 웹 구독 / FAL API 키 | LLM 부분만 | **실제 미디어 생성 시**(허용하신 제작 비용) | 비용이 드는 단계를 사람 승인 뒤로 |
| 검수 | 정확성, 표현, 브랜드, 게시 적합성 | reviewer 프로필(중간 등급) + **Claude Code `claude -p --model sonnet`** 2차 의견(선택) | ③ + ⑥ | ChatGPT Pro + Claude Pro | Claude 사용량 크레딧을 켜거나 `ANTHROPIC_API_KEY`가 있을 때 | 다른 회사 모델로 교차 검토 |
| 게시·운영 | 승인본만 패키지·기록 (1단계), 승인 후 API 게시 (2단계) | default 프로필 + `publish_log.csv` / 2단계: 인스타그램 공식 API 스크립트 + 승인 게이트 | ③ | ChatGPT Pro (기록·요약만) | 없음 (인스타그램 API 자체 요금 [확인 필요]) | 게시 권한을 주지 않는 것이 가장 강한 잠금 |

### 4-1. "LLM이 만드는 단계"와 "미디어를 실제 생성하는 단계"는 다릅니다

| 단계 | 누가 | 비용 |
|---|---|---|
| 기획·대본·제작 지시서(프롬프트) 작성 | LLM(ChatGPT Pro) | 구독 사용량 |
| 이미지·영상 실제 렌더링 | Kling·Seedance·FAL 등 제작 서비스 | **제작 서비스 비용**(웹 구독 크레딧 또는 API 선불) |
| 이미지 속 한글·수치 | 디자인 템플릿(Canva 등)에 사람이 넣음 | 템플릿 도구 요금 |

### 4-2. 제작 서비스: 웹 구독과 API는 다릅니다

| 서비스 | 웹 구독 | API | Hermes 연결 |
|---|---|---|---|
| Kling | 웹 멤버십 크레딧 | **별도 선불 패키지**. 웹 멤버십으로 API를 쓸 수 없고 크레딧도 옮겨지지 않음 [보도] | FAL 경유 Kling 3.0·O3 (`FAL_KEY`) 또는 OpenRouter 경유 [공식: Hermes 도구 문서]. Kling 공식 API 직접 연결은 기본 목록에 없음(플러그인 필요) [공식: 목록 기준] |
| Seedance | 드리미나·CapCut 등 웹·앱 [보도] | BytePlus ModelArk(해외)·Volcengine(중국) 종량제 [보도] | OpenRouter 경유 Seedance 2 [공식: Hermes 도구 문서]. FAL 기본 목록에는 없음 |
| FAL 이미지 | – | 종량제 | `image_gen` 도구, FLUX 2 등 11개 모델 [공식: Hermes 문서, 단가는 FAL 공식 가격표 확인] |

- **1단계 권장**: 웹에서 사람이 생성 → 추가 API 비용 0, 제작 구독료만. 저작권·상업 이용 조건은 각 서비스 약관 확인 [확인 필요].
- **2단계(선택)**: FAL 선불 크레딧 + 승인 게이트(부록 D). OpenRouter는 키 하나로 **LLM도 호출할 수 있어** 실수로 LLM 비용이 생길 여지가 있으므로, 영상 전용이라도 1단계에서는 권장하지 않습니다. [설계]
- 웹 화면을 자동 조작해 Kling·Seedance 웹을 대신 쓰게 하는 방식은 약관 위반·계정 제재 위험이 있어 권장하지 않습니다. [설계, 약관 확인 필요]

---

## 5. 실제 설치·연결 순서 (Windows 11 기준 초안 — 0-2 답변 후 확정)

> 표시 규칙: `<<바꾸기: ...>>` 는 직접 고칠 부분입니다. **API 키·비밀번호는 이 대화창에 절대 붙여넣지 마세요.** 로그인은 모두 브라우저 창에서 합니다.
> 명령어는 **PowerShell**(Windows 시작 메뉴에서 "PowerShell" 검색 → 실행)에 붙여넣습니다. 프롬프트 앞에 `PS C:\`가 보이면 PowerShell입니다.

### 1단계. PC 환경과 필수 조건 확인 (20분)

1. **조제·청구 PC와 분리**
   - 권장: 자동화 전용 PC(작은 미니 PC도 충분 [추정]). 최소: 같은 PC라면 **새 Windows 사용자 계정**을 만들어 그 계정에서만 Hermes를 설치.
   - 이유: Hermes는 터미널·파일 도구로 **그 계정이 열 수 있는 파일을 읽을 수 있습니다** [공식: 도구 목록]. 조제 프로그램·처방 스캔 파일이 보이면 환자정보가 AI로 나갈 수 있습니다.
2. **사양 확인**: Settings(설정) → System(시스템) → About(정보) → "설치된 RAM", "Windows 사양"을 적어 두세요.
   - 공식 최소 사양 문서는 찾지 못했습니다 [확인 필요]. Claude Code는 RAM 4GB 이상 [공식]. 여러 작업을 동시에 돌리지 않으면 8GB 이상이면 무난할 것으로 봅니다 [추정].
3. **Git for Windows 설치**: 브라우저에서 `git-scm.com/downloads/win` → 64-bit 설치 파일 → 기본값으로 계속 Next(다음) → Finish(마침).
   - 이유: Hermes의 터미널 도구가 Windows에서 **Git Bash**로 명령을 실행합니다 [공식]. Claude Code도 권장 [공식].
   - 성공 확인: PowerShell에서 `git --version` → `git version 2.x` 가 보이면 성공.
4. **API 키 환경변수가 없는지 확인** (값은 표시되지 않고 이름만 나옵니다):
   ```powershell
   Get-ChildItem Env: | Where-Object { $_.Name -match 'API_KEY|ANTHROPIC|OPENAI|OPENROUTER' } | Select-Object Name
   ```
   - 성공: 아무것도 출력되지 않음. 무언가 나오면 멈추고 알려주세요(직접 만든 게 아니면 지워야 함).

### 2단계. Hermes 설치 (15분)

1. 브라우저에서 **`hermes-agent.nousresearch.com`** 접속 → Desktop(데스크톱) → Windows 다운로드 (`.appinstaller` 파일).
2. 받은 파일 더블클릭 → Windows App Installer 창 → **Install(설치)**.
3. 시작 메뉴 → **Hermes** 실행 → 첫 안내 화면에서 **Choose provider later(나중에 선택)** 을 눌러도 됩니다 [공식]. (3단계에서 연결)
4. 성공 확인: PowerShell을 새로 열고
   ```powershell
   hermes --version
   hermes doctor
   ```
   - 버전 번호가 나오고 `doctor`에 치명적 오류가 없으면 성공.
   - `hermes`를 찾을 수 없다고 나오면 PowerShell을 닫았다 다시 여세요. 그래도 안 되면 알려주세요.
5. 참고: 백신이 `%LOCALAPPDATA%\hermes\bin\uv.exe`를 격리하면 **오탐**입니다(Hermes가 쓰는 Python 관리 도구) [공식 README]. 폴더 단위로 예외 처리하세요.
6. 대안(명령줄 설치): `iex (irm https://hermes-agent.nousresearch.com/install.ps1)` → 설치 후 `hermes desktop` 으로 앱 실행 [공식]. 관리자 권한 불필요.

### 3단계. 기존 구독을 쓰는 공식 연결 경로 설정 (20분)

**3-1. ChatGPT Pro 연결 (default 프로필)**
1. Hermes 앱 → Settings(설정) → **Providers(공급자)** → Accounts(계정) → **ChatGPT or Codex Subscription** → Sign in(로그인) [공식: 공급자 설정 화면 존재, 버튼 위치는 화면에서 확인]
   - 또는 PowerShell에서 `hermes model` → 목록에서 **ChatGPT or Codex Subscription** 선택.
2. 브라우저가 열리면 표시된 **코드**를 입력하고 ChatGPT(Pro) 계정으로 승인.
3. 모델 선택 화면에서 **중간 등급 모델**(예: GPT-6 Sol 계열)을 기본값으로 선택.
4. 성공 확인: 앱 채팅창에 "안녕"을 보내 답이 오면 성공. PowerShell `hermes status` 에 openai-codex 로그인이 보이면 성공.

**3-2. 비용 안전 설정 (default 프로필)** — PowerShell에 그대로 붙여넣기:
```powershell
hermes config set auth.adopt_external_logins false
hermes config set approvals.mode manual
hermes config set agent.max_turns 60
hermes config set HERMES_TIMEZONE Asia/Seoul
hermes fallback list
```
- 뜻: ① Claude Code 로그인을 Hermes가 빌려 쓰지 않음 ② 위험 명령은 AI 판단이 아니라 항상 사람에게 물음 ③ 한 번 요청에 최대 60번까지만 반복(무한 반복으로 사용량 소모 방지) ④ 한국 시간 기준 ⑤ 대체 공급자 목록 확인 → **비어 있어야 성공**.
- 모두 [공식] 문서에 있는 설정 키입니다. `agent.max_turns`의 적정값은 7단계에서 조정하세요 [추정].

**3-3. Claude Code 설치·로그인 (선택: 검수 2차 의견용)**
1. PowerShell:
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```
2. PowerShell을 새로 열고 `claude --version` → 버전이 나오면 설치 성공 [공식].
3. `claude` 입력 → 브라우저에서 **Claude Pro 계정**으로 로그인 → 로그인 완료 후 `/exit` 입력.
4. 확인: `claude auth status --text` → 구독 계정 로그인이 표시되면 성공.
5. 주의: `claude --bare` 모드는 구독 로그인을 쓰지 않고 API 키만 씁니다 [공식] → **쓰지 않습니다.**

**3-4. 구독 쪽 유료 전환 차단 (브라우저, 5분)**
1. claude.ai → Settings(설정) → Usage(사용량) → **usage credits(사용량 크레딧) / 자동 충전(auto-reload)이 꺼져 있는지** 확인 [공식: 기능 존재, 메뉴 이름은 화면에서 확인 필요].
2. ChatGPT → Settings(설정) → 사용량·크레딧 관련 메뉴에서 **크레딧 구매·자동 충전·앱의 크레딧 사용 허용이 꺼져 있는지** 확인 [보도: 기능 존재, 메뉴 이름 확인 필요].
3. ChatGPT에 "연결된 앱" 목록이 있다면 Hermes에 **주간 사용 상한(%)**을 걸어 두면 본인 몫이 보호됩니다 [보도: 앱별 주간 상한 기능, Hermes가 그 목록에 나타나는지 확인 필요].

### 4단계. 역할·프로필·모델 설정 (30분)

1. 프로필 3개 만들기 (3-2의 안전 설정이 복사되도록 `--clone` 사용) — PowerShell:
   ```powershell
   hermes profile create researcher --clone --description "공식 출처에서 근거를 수집하고 evidence.md를 작성"
   hermes profile create writer --clone --description "근거 기반으로 채널별 원고와 이미지·영상 제작 지시서를 작성"
   hermes profile create reviewer --clone --description "원고를 근거와 대조하고 규정 위험 표현을 점검"
   ```
   - 성공: `hermes profile list` 에 default, researcher, writer, reviewer 4개가 보임.
   - `--clone`은 설정·기억 파일을 복사하지만 **로그인(auth.json)은 복사하지 않습니다** [공식 설명 기준] → 다음 단계에서 각각 로그인.
2. 프로필마다 ChatGPT 로그인 (각각 브라우저 코드 입력):
   ```powershell
   hermes -p researcher auth add openai-codex
   hermes -p writer auth add openai-codex
   hermes -p reviewer auth add openai-codex
   ```
   - 같은 ChatGPT 계정으로 여러 번 로그인해도 되는지(기기 수 제한 등)는 [확인 필요]. 오류가 나면 알려주세요.
3. 프로필마다 모델 지정: Hermes 앱 → Settings(설정) → **Model(모델)** → 맨 위 **Applies to(적용 대상)** 에서 프로필 선택 → 모델 선택 [공식]. 추천:
   | 프로필 | 모델 등급 |
   |---|---|
   | default | 중간 등급 (대화·통합) |
   | researcher | 중간 등급 |
   | writer | 중간 등급 |
   | reviewer | 중간 등급 (+ Claude Code 2차) |
   - 형식 변환만 하는 역할을 나중에 추가하면 그 프로필은 가벼운 등급.
4. 작업자 프로필에서 유료 이미지·영상 도구 끄기 (API 키가 실수로 들어가도 작업자가 못 쓰게):
   ```powershell
   hermes -p researcher config set agent.disabled_toolsets '["image_gen","video_gen"]'
   hermes -p writer config set agent.disabled_toolsets '["image_gen","video_gen"]'
   hermes -p reviewer config set agent.disabled_toolsets '["image_gen","video_gen"]'
   ```
5. 직무 기술서(SOUL.md) 넣기: `hermes profile show researcher` → 표시된 폴더를 파일 탐색기로 열기 → `SOUL.md`를 메모장으로 열어 [`templates/hermes/SOUL-templates.md`](../templates/hermes/SOUL-templates.md)의 해당 부분을 붙여넣기 → 저장. 4개 프로필 모두 반복. (default 프로필 폴더는 `hermes config path` 로 확인)

### 5단계. 자료 조사 및 제작 도구 연결 (10분 / 2단계 미디어 API는 선택)

1. **웹 검색**: 아무 키도 넣지 않으면 Hermes가 무료 공개 등급(Exa·Parallel·Firecrawl·Keenable)을 돌아가며 씁니다 [공식]. 단 "최후 수단" 등급이라 **속도 제한**이 있습니다. DuckDuckGo(DDGS)도 키 없이 사용 가능 [공식].
   - 확인: `hermes -p researcher tools` → Web(웹) 항목에서 **Free(keyless)** 계열 또는 DDGS가 선택돼 있는지 확인. **Paid(API key) 항목은 고르지 않음.**
   - 개인정보 주의: 검색어는 외부 검색 회사로 전송됩니다. 환자 이름·증상 원문을 검색어로 쓰지 않도록 SOUL.md에 규칙을 넣었습니다.
2. **이미지·영상 (1단계)**: 아무것도 연결하지 않습니다. writer가 만든 `media_brief.md`를 보고 Kling·Seedance 웹에서 생성 → 결과 파일을 그 날짜 작업 폴더에 저장.
3. **이미지·영상 (2단계, 선택)**: 부록 D 참고. FAL 키는 `hermes tools` → Image Generation(이미지 생성) → FAL.ai 선택 후 **PowerShell 창에서 직접 입력**(대화창 금지). FAL 계정에서 선불·지출 한도 설정 가능 여부 [확인 필요].

### 6단계. 사람 승인 대기와 승인 후 게시 흐름 설정 (40분)

1. **텔레그램 연결 (default 프로필만)**: Hermes 앱 → **Messaging(메시징) → Telegram** → **Create with QR(QR로 만들기)** → 휴대폰 텔레그램으로 QR 스캔 → 봇이 자동 생성되고 **본인 텔레그램 ID만 허용**(`TELEGRAM_ALLOWED_USERS`)으로 저장됩니다 [공식].
   - 성공: 휴대폰 텔레그램에서 봇에게 "안녕" → 답이 오면 성공.
   - 봇 토큰은 대화창에 붙여넣지 마세요. QR 방식은 자동으로 저장합니다.
2. **작업 폴더 만들기**: 파일 탐색기에서 `C:\Users\<<바꾸기: 사용자이름>>\marketing\` 폴더 생성 → [`templates/hermes/content_calendar.csv`](../templates/hermes/content_calendar.csv)와 [`templates/hermes/publish_log.csv`](../templates/hermes/publish_log.csv)를 복사.
   - 캘린더는 엑셀로 편집 가능. 저장할 때 "CSV UTF-8"을 권장(일반 CSV도 읽도록 만들었음).
3. **스크립트 설치**: `hermes config path` 로 나온 파일이 있는 폴더 안에 `scripts` 폴더를 만들고, [`templates/hermes/scripts/`](../templates/hermes/scripts/)의 3개 파일(`mk_daily_cards.py`, `daily_report.py`, `health_check.py`)을 복사. (Hermes는 이 폴더 안의 스크립트만 예약 실행을 허용 [공식])
4. **칸반 설정** — PowerShell:
   ```powershell
   hermes kanban init
   hermes config set kanban.max_in_progress 1
   hermes config set kanban.failure_limit 2
   hermes config set kanban.review_dispatch false
   ```
   - 뜻: 동시에 1장만 실행(사용량 급소모 방지), 연속 실패 2번이면 자동 정지, 검토 단계는 사람만.
5. **예약 작업 3개 등록** — PowerShell:
   ```powershell
   hermes cron create "0 7 * * *" --no-agent --script mk_daily_cards.py --deliver telegram --name "daily-cards"
   hermes cron create "0 12 * * *" --no-agent --script daily_report.py --deliver telegram --name "daily-report"
   hermes cron create "0 21 * * *" --no-agent --script health_check.py --deliver telegram --name "health-check"
   hermes cron list
   ```
   - 성공: `cron list`에 3개가 보이고 다음 실행 시각이 한국 시간으로 맞음.
6. **승인 흐름 (텔레그램에서 약사가 하는 일)**

   | 순서 | 약사가 보내는 말 | Hermes(default)가 하는 일 |
   |---|---|---|
   | 1 | `승인 검토 2026-10-06-1` | review.md 결론, 근거 개수, 원고 첫 줄들, 제작 지시서 요약을 보여줌 |
   | 2 | `수정 2026-10-06-1: <고칠 내용>` | 해당 원고를 고쳐 다시 보여줌 |
   | 3 | `승인 2026-10-06-1` (**승인 A**) | publish_log.csv에 승인 기록, 제작 지시서 확정 |
   | 4 | (사람이 웹에서 이미지·영상 생성 → 폴더에 저장) | – |
   | 5 | `최종 확인 2026-10-06-1` (**승인 B**) | 채널별 붙여넣기용 `final_<채널>.md` 생성 |
   | 6 | (사람이 각 앱·Studio에서 게시·예약) | – |
   | 7 | `게시완료 2026-10-06-1 인스타그램 <URL>` | publish_log.csv에 게시 기록. 같은 번호·채널이 이미 있으면 경고 |

   - **승인 전 게시가 불가능한 이유**: 1단계에서는 PC에 인스타그램·유튜브·네이버 게시 권한(토큰·비밀번호)이 **없습니다.** 게시는 항상 사람 손으로 합니다. [설계]
   - 2단계에서 인스타그램 공식 API 자동 게시를 붙일 때는 부록 D의 승인 게이트를 함께 씁니다.

### 7단계. 소규모 작업으로 전체 흐름 검증 (1~2시간, 하루 1건 × 3일 권장)

1. 캘린더에 **오늘 날짜**로 위험 낮은 주제 1개(예: 폐의약품 배출법, R0)를 넣고 저장.
2. 즉시 실행: `hermes cron run daily-cards` → 텔레그램에 "카드 생성" 메시지 → `hermes kanban list` 에 카드 3장.
3. 진행 관찰: Hermes 앱의 **Kanban** 화면, 또는 `hermes kanban watch`.
4. 결과 확인: `marketing\content\<날짜>-1\` 폴더에 `evidence.md` → `draft_*.md`, `media_brief.md` → `review.md`가 차례로 생기는지.
5. **사용량 측정**: 시작 전·후로 ChatGPT의 사용량 화면과 claude.ai Settings(설정) → Usage(사용량)을 캡처 → 편당 사용률 계산(6-2 산식).
6. **모의 훈련 4가지**

   | 훈련 | 방법 | 통과 기준 |
   |---|---|---|
   | 가짜 인용 | draft 파일에 근거에 없는 수치 1개를 몰래 넣고 검수 카드만 다시 실행 | review.md가 그 문장을 잡아냄 |
   | 중복 실행 | `hermes cron run daily-cards`를 한 번 더 실행 | 새 카드가 생기지 않고 같은 카드 번호가 출력됨 |
   | 승인 없이 게시 요청 | 텔레그램에 "지금 바로 인스타에 올려" | 거절하고 승인 절차를 안내 |
   | 점검 알림 | `hermes cron run health-check` | 문제가 없으면 조용함, 일부러 로그아웃하면 알림 |
7. 문제가 생기면 확인할 곳: `hermes kanban show <카드번호>`, `hermes kanban log <카드번호>`, `hermes logs`.
8. **이 저장소의 스크립트는 실제 Hermes에서 아직 실행해 보지 않았습니다.** 모의 실행(dry-run)과 문법 검사만 통과했습니다. 7단계에서 오류가 나면 메시지를 그대로 알려주세요(개인정보·키가 없다면).

### 8단계. 24시간 운영 설정 (20분)

| 항목 | 설정 | 근거 |
|---|---|---|
| 절전 방지 | Hermes 앱 → Settings(설정) → Advanced(고급) → **Keep computer awake(컴퓨터 깨어 있기)** 켜기. 추가로 Windows 설정 → 시스템 → 전원 → 화면 및 절전 → "전원 연결 시 절전 모드" **안 함** | [공식: Hermes] |
| (명령으로 하려면) | `powercfg /change standby-timeout-ac 0` 과 `powercfg /change hibernate-timeout-ac 0` | Windows 기본 명령 |
| 재부팅 후 자동 시작 | `hermes gateway install` → Windows 로그인 시 게이트웨이 자동 실행(작업 스케줄러, 관리자 권한 불필요). 확인: `hermes gateway status` | [공식] |
| 재부팅 후 로그인 | 게이트웨이는 **Windows 로그인 후** 시작됨. 자동 로그인은 보안상 권장하지 않음 → 재부팅 시 사람이 로그인 | [공식: 로그인 시 시작] / [설계] |
| Windows 업데이트 재부팅 | 설정 → Windows 업데이트 → 고급 옵션 → **사용 시간(Active hours)** 을 예: 06:00~23:00 | [설계] |
| 정전 후 자동 켜짐 | PC BIOS의 "AC 전원 복구(Restore on AC power loss)" | [PC별 확인 필요] |
| 로그인·토큰 만료 | ChatGPT 로그인은 자동 갱신. 갱신이 영구 실패하면 Hermes가 반복 시도를 멈추고 재로그인 안내 [공식]. 매일 21:00 `health_check.py`가 알림 → PC에서 `hermes -p <프로필> auth add openai-codex` / Claude는 `claude` 실행 후 재로그인 | [공식] + [설계] |
| 사용량 한도 도달 | 이 설계의 예약 작업 3개는 LLM을 쓰지 않아 한도와 무관. LLM을 쓰는 칸반 작업자는 사용량 한도 오류가 나면 카드를 대기열로 돌리고 **쿨다운(기본 300초)** 후 다시 확인하며, 이 대기는 실패 횟수에 포함되지 않음. 인증 오류는 곧바로 재실행하지 않고 사람 확인을 기다림. 대체 공급자가 없으므로 **유료 전환 없이 대기**. 12:00 현황 보고에 "멈춤/대기"로 표시 | [공식 문서 기준, 실제 동작은 7단계에서 확인] |
| 실패 재시도 상한 | 카드별 `--max-retries 2`, `kanban.failure_limit 2`, 카드별 최대 40분, 요청당 최대 60회 반복. 예약 작업의 자동 재실행(5·15·30분)은 **모델 호출 전 네트워크 실패**일 때만 | [공식] |
| 중복 게시 방지 | 카드 생성은 날짜별 중복 방지 키 / 게시는 사람이 하고 `publish_log.csv`로 확인 / 2단계 자동 게시 스크립트는 기록이 있으면 거부 | [공식] + [설계] |
| 비상 정지 | `hermes pause` → 예약 작업·칸반·게이트웨이 새 작업 모두 중지(진행 중인 것은 끝까지), 재개는 `hermes resume` | [공식] |
| 로그 확인 | `hermes gateway status`, `hermes cron status`, `hermes cron list`, `hermes cron doctor`, `hermes kanban list`, `hermes kanban diagnostics`, `hermes logs -f` | [공식] |
| 비용 누적 방지 | 1-5의 구멍 7개 차단 + 동시 실행 1개 + 하루 1회 예약 + 작업자에서 유료 도구 끄기 + (2단계) 하루 유료 생성 승인 요청 3회 상한 | [설계] |

- 게이트웨이(gateway) = Hermes의 상시 실행 부분. 예약 작업과 칸반 배정기가 이 안에서 돌아갑니다 [공식]. 그래서 **앱 창을 닫아도 게이트웨이가 켜져 있으면 자동화는 계속**됩니다 [공식 문서 기반 판단, 7단계에서 확인].

---

## 6. 비용이 발생하는 지점과 운영상 제한

### 6-1. 월 비용표

| 항목 | 월 추가 비용 | 표시 |
|---|---|---|
| Hermes Desktop | ₩0 | [공식: MIT 무료] |
| ChatGPT Pro | 기존 구독료 외 ₩0 | 크레딧·리셋을 사지 않는 조건 |
| Claude Pro | 기존 구독료 외 ₩0 | 사용량 크레딧을 켜지 않는 조건 |
| Claude Code | ₩0 (Pro에 포함) | [공식] |
| 텔레그램 봇 | ₩0 | [추정] |
| 웹 검색 | ₩0 (무료 등급, 속도 제한) | [공식: Hermes] |
| PC 전기요금 | 산식 참고 | [추정] |
| 이미지·영상 | 산식 참고 (허용하신 비용) | 서비스별 공식 가격표 |

### 6-2. 비용·처리량 산식 (예상 제작량이 정해지지 않아 금액은 확정하지 않음)

**① 구독 사용량으로 가능한 처리량**
```
편당 주간 사용률(%) = (시험 운영 후 주간 사용률 − 시험 운영 전 주간 사용률) ÷ 시험 제작 편수
주당 가능 편수     = (100% − 본인이 직접 쓰는 몫% − 안전 여유 20%) ÷ 편당 주간 사용률
```
필요한 입력값: ChatGPT Pro 등급, 평소 본인 사용량(%), 7단계에서 측정한 편당 사용률. Claude Pro(검수 2차)도 같은 방식으로 따로 계산.

**② 이미지·영상 비용**
```
월 영상 비용 = Σ(월 편수 × 편당 생성 초 × 초당 단가 × (1 + 재생성률))
월 이미지 비용 = 월 이미지 장수 × 장당 단가 × (1 + 재생성률)
월 제작 비용 = 월 영상 비용 + 월 이미지 비용 + 웹 구독 월정액(쓰는 경우) + 템플릿 도구 월정액
원화 환산 = 달러 금액 × 결제일 환율 (+ 해외결제 수수료)
```
필요한 입력값: 월 편수, 영상 길이(초), 해상도·오디오 포함 여부, 모델, 재생성률(처음엔 50% 이상으로 잡는 것을 권장 [추정]), 결제 방식(웹 구독/API 선불), 환율.

**③ 전기요금**
```
월 전력량(kWh) = 평균 소비전력(W) × 24 × 30 ÷ 1000
월 전기요금    = 월 전력량 × 약국 전기요금 단가(원/kWh)
```
예: 평균 20W 미니 PC면 월 14.4kWh [추정]. 단가는 약국 전기요금 고지서에서 확인.

### 6-3. 운영상 제한 (솔직한 목록)

| 제한 | 영향 | 대응 |
|---|---|---|
| 구독 한도 도달 시 멈춤 | 그날 제작이 늦어짐 | 설계상 의도. 주제 수를 한도에 맞춤 |
| 정책 변경 위험 | OpenAI "다른 앱에서 요금제 사용" 정책은 2026-09-29 발표 직후, Anthropic은 `claude -p` 분리 계획을 보류 중 | 분기마다 공식 도움말 재확인. Claude 2차 검수는 빠져도 돌아가게 설계 |
| OpenAI의 Hermes 허용 여부 미확인 | 계정 제재 가능성이 0이라고 단정 불가 | 가장 보수적 대안: ⑤ Codex app-server 런타임(공식 Codex CLI 사용). 또는 OpenAI 고객지원에 문의 |
| 모델 이름·등급 변경 | 설정한 모델이 사라질 수 있음 | `hermes model` 목록 기준으로 재선택 |
| 재부팅 후 로그인 필요 | 정전·업데이트 후 멈춤 | 사용 시간 설정, 휴대폰으로 점검 알림 |
| 네이버 블로그·클립 자동 게시 불가 | 사람 손 필요 | 붙여넣기용 패키지로 3~10분 [이전 설계서 추정] |
| 무료 검색 속도 제한 | 조사가 느리거나 실패 | 공식 사이트 URL을 캘린더 메모에 미리 적어 줌 |
| Claude Pro 한도 작음 | 2차 검수 생략될 수 있음 | 실패 시 "2차 의견 생략"으로 기록하고 진행 |
| 저장소 스크립트 미검증 | 실제 PC에서 오류 가능 | 7단계에서 검증 후 수정 |

---

## 7. 내가 직접 결정할 일 vs 자동화에 맡길 일

| 약사가 직접 | 자동화에 맡김 |
|---|---|
| 0-2의 8가지 질문 답변 | 매일 카드 생성·순서 관리·현황 보고 |
| 콘텐츠 캘린더(주제·날짜·위험 등급) | 공식 출처 검색·근거 정리 |
| 승인 A(원고·제작 지시서), 승인 B(완성본) | 채널별 원고·대본·제작 지시서 초안 |
| 실제 게시(1단계), 게시 시각 | 근거 대조·위험 표현 1차 점검 |
| 유료 미디어 생성 여부·예산 상한 | 게시 패키지 정리·게시 기록 |
| 추가 LLM 비용 대안 선택 여부 | 로그인·비용 위험 설정 매일 점검 |
| 법적으로 애매한 표현의 최종 판단 | – |

---

## 8. 법규·개인정보 주의 (요약 — 상세는 이전 설계서 부록 A·B)

- 의약품 온라인 판매·구매 유도, 치료 효과 보장, 특정 병원 안내(담합 오해), 전문의약품 광고, 체험담형 표현은 원고 단계에서 금지로 넣었습니다. 애매한 표현은 **대한약사회·관할 보건소·식약처**에 확인하세요. [이전 설계서: 약사법 제50조·제68조 등]
- 건강기능식품을 다루면 기능성 표시·광고 사전심의 대상 여부를 확인하세요 [확인 필요].
- **환자 개인정보는 자동화 PC·AI·검색어에 넣지 않습니다.** 자동화 PC를 조제·청구 PC와 분리하는 이유입니다.
- AI 생성 이미지·영상에는 플랫폼 정책(유튜브 합성 콘텐츠 표시, Meta AI 정보 라벨)에 따라 표시하세요 [이전 설계서, 확인 필요].

---

## 부록 D. 2단계(선택): 인스타그램 공식 API 게시·유료 미디어 API를 붙일 때의 승인 게이트

1단계가 2주 이상 안정적으로 돌고, 승인 기록이 쌓인 뒤에만 검토하세요. [설계]

**구조**
1. 칸반 작업자(사람 없는 실행)는 게시·유료 생성을 **할 수 없음**: Hermes는 사람이 없는 실행에서 승인 요청을 **자동 거절**합니다(`approvals.cron_mode`, `single_query_mode` 기본값 `deny`) [공식]. 추가로 4단계에서 작업자 프로필의 유료 도구를 꺼 둠.
2. 게시·유료 생성은 **약사가 텔레그램에서 직접 요청한 대화**에서만 실행.
3. 그 직전에 [`templates/hermes/hooks/approval_gate.py`](../templates/hermes/hooks/approval_gate.py) 훅이 **예상 비용·게시 명령을 보여주고 사람 승인**을 받음. 하루 유료 생성 승인 요청 3회 초과 시 차단. [공식: `pre_tool_call` 훅의 approve/block 기능]
4. 게시 스크립트(`publish_*.py`, 2단계에서 작성)는 `publish_log.csv`에 같은 번호·채널 기록이 있으면 실행을 거부.

**default 프로필 `config.yaml`에 추가** (`hermes config edit` 으로 열기):
```yaml
hooks:
  pre_tool_call:
    - matcher: "terminal|video_generate|image_generate|xai_video_edit|xai_video_extend"
      command: "C:/Users/<<바꾸기: 사용자이름>>/hermes-scripts/approval_gate.py"
      timeout: 20
      fail_closed: true
```
- 경로는 **슬래시(/)** 로 적으세요(명령 해석 방식 때문) [확인 필요: `hermes hooks test`로 확인].
- 같은 폴더에 [`media_prices.json`](../templates/hermes/hooks/media_prices.json)을 두고, **공식 가격표에서 확인한 단가**를 직접 입력.

**반드시 확인할 것** [공식]
- 새 훅은 처음 한 번 **사람 동의**가 필요합니다. 게이트웨이·예약 작업에서는 동의 창이 뜨지 않아 **동의 안 된 훅이 조용히 빠집니다.** → PowerShell에서 `hermes chat` 을 한 번 실행해 동의 → `hermes hooks list` 에서 동의 상태 확인 → `hermes hooks doctor`.
- `fail_closed: true` = 훅이 고장 나면 통과가 아니라 **차단**.
- **YOLO 모드**(`/yolo`, `hermes --yolo`)는 모든 승인 창을 건너뜁니다. 절대 켜지 마세요.
- 인스타그램 Graph API 앱 설정·권한 심사·게시 한도는 별도 확인이 필요합니다 [확인 필요, 이전 설계서 참고].

---

## 출처 (확인일 2026-09-30)

**Hermes (공식 저장소 문서 원본으로 확인)**
- 공식 저장소·라이선스·버전 태그: https://github.com/NousResearch/hermes-agent (README, LICENSE, 태그 v2026.9.24)
- 공급자·구독 요금제 표·Anthropic/Codex 인증: https://hermes-agent.nousresearch.com/docs/integrations/providers (저장소 `website/docs/integrations/providers.md`)
- Desktop 앱(설치, 모델 선택, Keep computer awake, 설정 화면): https://hermes-agent.nousresearch.com/docs/user-guide/desktop
- 설치: https://hermes-agent.nousresearch.com/docs/getting-started/installation
- Windows 네이티브(게이트웨이 자동 시작, Git Bash): https://hermes-agent.nousresearch.com/docs/user-guide/windows-native
- Codex app-server 런타임: https://hermes-agent.nousresearch.com/docs/user-guide/features/codex-app-server-runtime
- 프로필: https://hermes-agent.nousresearch.com/docs/user-guide/profiles
- 칸반: https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban
- 하위 에이전트(delegation): https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation
- 예약 작업(cron, no-agent, 사용량 창 보류): https://hermes-agent.nousresearch.com/docs/user-guide/features/cron
- 훅(pre_tool_call, 동의 모델): https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks
- 보안(승인 모드, 빌린 CLI 로그인, YOLO): https://hermes-agent.nousresearch.com/docs/user-guide/security
- 웹 검색 무료 등급: https://hermes-agent.nousresearch.com/docs/user-guide/features/web-search
- 이미지 생성(FAL): https://hermes-agent.nousresearch.com/docs/user-guide/features/image-generation
- 도구 목록(video_generate: FAL Kling, OpenRouter Seedance): https://hermes-agent.nousresearch.com/docs/reference/tools-reference
- 텔레그램: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram
- Claude Code 번들 스킬: https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code
- 커뮤니티 프로젝트 고지: https://github.com/fathah/hermes-desktop

**Anthropic (공식)**
- Claude Code 법적 고지(OAuth 사용 범위, 개인 사용 전제): https://code.claude.com/docs/en/legal-and-compliance
- Agent SDK·`claude -p` 사용량 공지(2026-06-15 보류): https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
- 사용량 크레딧(표준 API 요금): https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans
- Pro 요금제 한도(5시간·주간): https://support.claude.com/en/articles/8325606-what-is-the-pro-plan
- Claude Code와 Pro 사용량 공유, API 키 주의: https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan
- Claude Code 설치: https://code.claude.com/docs/en/setup
- `claude -p`·`--bare`: https://code.claude.com/docs/en/headless
- (보도) 타사 에이전트 추가 사용량 전환: https://techcrunch.com/2026/04/04/anthropic-says-claude-code-subscribers-will-need-to-pay-extra-for-openclaw-support/

**OpenAI (공식 페이지 접속 불가 → 검색 요약·보도로 확인)**
- 다른 앱에서 ChatGPT 요금제 사용: https://help.openai.com/en/articles/20001542-using-your-chatgpt-plan-in-other-apps-and-sites
- ChatGPT 요금제로 Codex 사용: https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- Pro 등급: https://help.openai.com/en/articles/9793128-about-chatgpt-pro-tiers
- Codex 가격: https://developers.openai.com/codex/pricing
- DevDay 2026 요약: https://openai.com/index/devday-2026-recap/
- (보도) https://thenewstack.io/sign-in-with-chatgpt/
- (보도) https://thenextweb.com/news/openai-devday-pro-200-usage-cut-pro-500-plan
- (보도) https://www.engadget.com/2272106/openai-adds-dollar500-pro-subscription-nerfs-its-existing-dollar200-tier/

**제작 도구 (보도 — 공식 가격표 확인 필요)**
- Kling API와 웹 멤버십 분리: https://wavespeed.ai/blog/ai-api-pricing/kling-ai-api-pricing/
- Seedance API(BytePlus ModelArk): https://www.nxcode.io/resources/news/seedance-2-0-api-guide-pricing-setup-2026
