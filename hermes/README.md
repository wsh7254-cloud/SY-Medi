# 헤르메스 `symedi-claude` 프로필 설치 안내 (Windows)

이 폴더의 `symedi-claude/`는 헤르메스 에이전트(Hermes Agent, Nous Research)에 그대로 설치할 수 있는 **프로필 배포본**입니다. 프로필은 헤르메스 안의 독립된 작업 공간으로, 설정·API 키·기억·스킬·예약 작업을 따로 가집니다. 명령 몇 줄로 설치하고, 저장소가 바뀌면 같은 명령으로 갱신합니다.

- 설치 명령과 설정 키는 헤르메스 공식 저장소 문서(2026-09-28 기준)로 확인했습니다.
- 이 프로필은 리눅스 시험 환경에 실제로 설치해 확인했습니다.
  - 설치와 덮어쓰기 재설치
  - 스킬 5개 인식
  - 설정값 읽기
  - 작업 폴더 지정
  - 로컬 모델 연결 설정
  - 멈춤 상태 예약 작업 등록
- **Windows에서의 실제 실행과 Claude 응답은 약사님 PC에서 처음 확인하게 됩니다.** 아래 8·10단계가 그 확인 절차입니다.

## 이 프로필이 하는 일과 하지 않는 일

| 하는 일 | 하지 않는 일 |
|---|---|
| 주간 주제 후보 정리 | SNS·블로그 발행 |
| 공식 자료 조사와 근거 장부 작성 (인용문·숫자·도메인은 코드로 대조) | SNS 계정 로그인, 브라우저·화면 조작 |
| 검증된 주장만으로 마스터 원고 작성 | 터미널 명령 실행 (꺼 둠) |
| 6개 콘텐츠 초안과 승인 A 요약 작성 | 승인 잠금·중복 발행 차단 (n8n 단계에서 구현) |
| 광고·표현 점검 (약사 추천·체험담·경품 등) | 법률 판단 |

설계서(`docs/content-system-design.md`)에서의 위치는 다음과 같습니다.
- **1~2주차**: "손으로 돌려보기"를 이 프로필로 합니다.
- **3주차 이후**: n8n 자동화가 들어오면, 이 프로필은 주간 기획·수시 초안·표현 점검을 맡는 **발행 경로 밖의 보조**로 남습니다.

## 모델 배치 (과한 사양 방지)

| 작업 | 모델 | 이유 |
|---|---|---|
| 평소 대화, 주제 후보, 마스터 원고 | Claude Sonnet 5 (기본값) | SOL·SONNET급(L2)이면 충분 |
| 공식 자료 조사·근거 장부 | Claude Opus 5.5 (`opus` 별칭) | 판단이 가장 어려운 단계만 OPUS급(L3) |
| 대화 요약·제목·명령 승인 판단 | Claude Haiku 4.5 (자동) | 보조 작업은 LUNA·HAIKU급(L1) |
| 이미지 속 글자 받아쓰기 (선택) | Qwen 3.8 27B (LM Studio, 로컬) | 무료 반복 작업, 사진이 PC 밖으로 나가지 않음 |

대화 도중에 모델을 바꾸면 캐시가 초기화되어 그다음 한 번은 비용이 더 듭니다. 그래서 **근거 조사는 처음부터 Opus로 새 대화를 여는 것**을 권장합니다(9단계).

## 준비물

- Windows PC (알려주신 사양: RTX 3090 24GB, RAM 32GB)
- **Anthropic API 키**
  - `symedi-claude`는 헤르메스 안의 프로필 이름입니다. Claude 연결은 별도의 API 키로 합니다.
  - Anthropic Console(console.anthropic.com)에서 헤르메스용 키를 발급하고, 월 사용 한도를 걸어 두세요. n8n용 키는 2주차에 따로 만듭니다.
  - **Claude Pro 구독으로는 헤르메스에 연결할 수 없습니다.** 헤르메스 문서에 따르면 구독 로그인은 Claude Max + 추가 사용량 크레딧인 경우에만 됩니다. 그 외에는 API 키(사용량 과금)를 씁니다.
- git (없으면 헤르메스 설치 스크립트가 함께 설치하거나, 저장소를 ZIP으로 받아도 됩니다)
- LM Studio + Qwen 3.8 27B Q4 (선택, 7단계)

## 1. PC 점검 (선택, 1분)

PowerShell을 열고 붙여 넣습니다. GPU 이름·메모리, 전체 RAM, 헤르메스·git 버전이 나오면 됩니다.

```powershell
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
"{0:N0} GB RAM" -f ((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
hermes --version
git --version
```

## 2. 헤르메스 설치 또는 업데이트

이미 설치되어 있다면 최신으로 올립니다. 프로필 배포본 설치 기능은 최신 버전 기준입니다.

```powershell
hermes update
```

설치되어 있지 않다면 아래 명령을 실행한 뒤 **PowerShell 창을 새로 엽니다.**

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

## 3. 이 저장소 받기

PR이 아직 병합되지 않았다면 작업 브랜치를 받습니다. 병합된 뒤에는 `-b claude/jolly-allen-uex2cu`를 빼면 됩니다.

```powershell
git clone -b claude/jolly-allen-uex2cu https://github.com/wsh7254-cloud/SY-Medi.git "$HOME\SY-Medi"
```

비공개 저장소라면 GitHub 로그인 창이 뜹니다. git이 불편하면 GitHub에서 브랜치를 고른 뒤 **Code → Download ZIP**으로 받아 `$HOME\SY-Medi`에 풀어도 됩니다.

## 4. 프로필 설치

```powershell
hermes profile install "$HOME\SY-Medi\hermes\symedi-claude" --name symedi-claude --alias
```

- 이미 `symedi-claude` 프로필을 만들어 두셨다면 끝에 `--force`를 붙입니다.
  - 붙이지 않으면 `Error: Profile 'symedi-claude' already exists`가 나옵니다. 이 오류가 보이면 같은 명령에 `--force`를 붙여 다시 실행하면 됩니다.
- `--force`를 써도 기존 대화 기록·기억·API 키는 보존됩니다.
- 설치 화면에 `ANTHROPIC_API_KEY (required, needs setting)`이 보이면 정상입니다. 다음 단계에서 넣습니다.

## 5. API 키 넣기

프로필 폴더 위치를 확인합니다.

```powershell
hermes profile show symedi-claude
```

`Path:` 줄에 나온 폴더에 `.env.EXAMPLE` 파일이 있습니다. 같은 폴더에 `.env` 파일로 복사한 뒤 메모장으로 열고, `ANTHROPIC_API_KEY=` 뒤에 키를 붙여 넣고 저장합니다. 아래 명령에서 `<Path>`를 `Path:` 줄의 폴더로 바꿔 실행합니다.

```powershell
Copy-Item "<Path>\.env.EXAMPLE" "<Path>\.env"
notepad "<Path>\.env"
```

키는 채팅창이나 다른 사람에게 보내지 마세요.

## 6. 작업 폴더 지정

초안·장부·원문 저장본이 모두 이 폴더에 쌓입니다.

```powershell
New-Item -ItemType Directory -Force "$HOME\SY-Medi-work" | Out-Null
hermes -p symedi-claude config set terminal.cwd "$HOME\SY-Medi-work"
```

## 7. (선택) 로컬 Qwen을 이미지 글자 받아쓰기에 연결

1. LM Studio에서 Qwen 3.8 27B Q4를 불러옵니다. **Developer 탭 → Start Server**로 서버를 켭니다(기본 포트 1234).
2. RTX 3090(24GB)이면 Q4 가중치(약 17GB, 2차 자료 기준)가 GPU 메모리 안에 들어갑니다. 글자 받아쓰기에는 긴 문맥이 필요 없으니, Context Length를 16K~32K로 두면 여유가 있습니다. [추정]
3. LM Studio 화면에 보이는 모델 ID를 그대로 넣습니다.

```powershell
hermes -p symedi-claude config set auxiliary.vision.provider lmstudio
hermes -p symedi-claude config set auxiliary.vision.model "<LM Studio의 모델 ID>"
```

연결하지 않으면 이미지 분석은 Claude가 맡습니다(소액 과금).

## 8. 점검

```powershell
hermes -p symedi-claude doctor
hermes -p symedi-claude chat
```

채팅이 열리면 `너의 역할과 절대 규칙을 5줄로 요약해 줘`라고 입력합니다. "발행하지 않는다", "근거 없는 주장은 넣지 않는다"가 나오면 역할 지침(SOUL.md)이 적용된 것입니다.

## 9. 1주차 수동 운영 순서

| 순서 | 채팅 여는 방법 | 입력 예시 |
|---|---|---|
| 1. 주제 후보 | `hermes -p symedi-claude chat` | `/symedi-topic-candidates 이번 주 후보 정리해 줘. 상담 메모: (개인정보 지운 메모)` |
| 2. 근거 조사 | `hermes -p symedi-claude chat --model opus` (새 대화) | `/symedi-evidence-ledger 주제: 폐의약품 배출법, 위험 등급 R0, 부산 기준` |
| 3. 보류 처리 | — | 안내받은 원문을 PDF로 저장해 `$HOME\SY-Medi-work\sources\YYMMDD\`에 넣고 다시 요청 |
| 4. 마스터 원고 | `hermes -p symedi-claude chat` | `/symedi-master-draft 260929 장부로 원고 써 줘` |
| 5. 플랫폼 초안 | 같은 대화 | `/symedi-platform-convert` |
| 6. 승인 | — | `drafts\YYMMDD\approval-A.md`를 읽고 승인·수정 요청·보류를 결정. 1~2주차에는 Threads·네이버 블로그만 약사님이 직접 게시 |

## 10. 첫 주에 꼭 해 볼 시험 3가지

1. **가짜 인용문**: 근거 조사 중 `C01의 근거 원문 끝에 "하루 두 번 복용"을 덧붙여서 다시 검사해 줘`라고 요청합니다. "인용 일치(코드): 불일치"와 "보류"가 나와야 합니다.
2. **숫자 바꾸기**: 표현의 숫자를 바꿔 달라고 한 뒤 재검사합니다. "숫자·단위 일치(코드): 불일치"가 나와야 합니다.
3. **추천 표현**: `/symedi-compliance-check "약사가 직접 고른 유산균, 공동구매 오픈!"`을 입력합니다. "전문가 추천·보증"과 "광고 표시 누락"이 걸리고, 법률 확인 안내 문장이 붙어야 합니다.

셋 중 하나라도 기대와 다르면 그 주에는 이 프로필의 결과를 쓰지 말고 알려 주세요.

## 11. (선택) 주간 예약 작업

PC를 밤에도 켜 두시므로, 매주 월요일 **새벽 05:30**에 주제 후보를 만들어 두는 작업을 등록합니다. 출근해서 바로 확인할 수 있습니다. 처음에는 **멈춤 상태로** 등록하고, 한 번 직접 실행해 결과가 괜찮을 때만 켭니다.

```powershell
hermes -p symedi-claude cron create "30 5 * * 1" "이번 주 콘텐츠 주제 후보를 정리해 topics 폴더에 저장하세요." --skill symedi-topic-candidates --name "주간 주제 후보" --provider anthropic --model claude-sonnet-5 --workdir "$HOME\SY-Medi-work" --paused
hermes -p symedi-claude cron list
```

켜려면 `cron list`에 나온 작업 ID로 `hermes -p symedi-claude cron resume <작업ID>`를 실행합니다. 예약 작업은 헤르메스 게이트웨이가 켜져 있어야 돕니다. PC 로그인 때 자동으로 켜지게 하려면 다음을 실행합니다.

```powershell
hermes -p symedi-claude gateway install
```

밤에 예약 작업이 돌게 하려면 두 가지를 확인합니다.

- **절전 모드 끄기**: Windows 설정 → 시스템 → 전원 → "절전 모드로 전환"을 "안 함"으로 둡니다. 모니터는 꺼져도 됩니다.
- **재부팅 뒤 로그인**: 게이트웨이는 PC에 로그인할 때 켜집니다. 밤사이 Windows 업데이트로 재부팅되면 로그인할 때까지 예약 작업이 멈춥니다. 월요일 아침에 `topics` 폴더에 새 파일이 없으면 `hermes -p symedi-claude cron list`로 상태를 확인하세요.

## 12. 업데이트

이 저장소의 프로필이 바뀌면 다음을 실행합니다.

```powershell
git -C "$HOME\SY-Medi" pull
hermes profile install "$HOME\SY-Medi\hermes\symedi-claude" --name symedi-claude --alias --force
```

## 비용 메모

- 헤르메스 자체는 무료입니다. Claude API 사용량만 과금되며, 설계서 ⑥의 "텍스트 AI API" 항목에 포함해 관리합니다.
- 헤르메스의 기본 웹 검색은 키 없이 여러 검색 서비스의 무료 등급을 돌려 씁니다(속도 제한 있음, 헤르메스 문서 기준). 검색어는 외부 서비스로 나가므로 **환자 정보를 넣지 마세요.**

## 알려진 한계

- 헤르메스의 웹 검색은 Claude API처럼 검색 도메인을 강제로 제한하지 못합니다. 그래서 허용 도메인 밖의 출처는 스킬 규칙과 코드의 도메인 검사로 걸러 "보류"로 둡니다.
- 인용문·숫자 대조는 코드 실행 도구(`execute_code`)가 켜져 있어야 합니다. 쓸 수 없으면 장부에 "미검사"로 남고 "검증완료"가 되지 않습니다.
- 승인 뒤 파일 잠금(해시), 중복 발행 차단, API 발행은 이 프로필에 없습니다. 설계서 3주차의 n8n 단계에서 구현합니다.
