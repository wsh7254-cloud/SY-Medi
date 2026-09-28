---
name: symedi-evidence-ledger
description: 주제 하나에 대해 공식 자료를 찾아 원문을 저장하고, 주장별 근거 장부(CSV)를 만든다. 인용문·숫자·도메인은 코드로 대조한다. 권장 모델은 Claude Opus 5.5.
version: 0.1.0
metadata:
  hermes:
    tags: [symedi, evidence, verification]
    category: symedi
---

# 공식 자료 조사와 근거 장부 작성

권장 모델: **Claude Opus 5.5** (OPUS급 L3). 현재 모델이 다를 수 있으면, 시작 전에 약사에게 `/model`로 `claude-opus-5-5`로 바꾸고 다시 요청해 달라고 한 번 안내합니다.

## When to Use

- 약사가 확정한 주제의 근거를 모을 때
- 보류된 주장에 약사가 새 출처(PDF 등)를 넣어 다시 확인할 때

## Procedure

### 1. 주제와 위험 등급 확인

- 주제ID를 `YYMMDD-주제요약` 형식으로 정합니다.
- 위험 등급을 정합니다.
  - R0: 생활 정보
  - R1: 일반 건강 정보
  - R2: 용량·상호작용·금기·임신수유·소아·고령자·질환별 치료·성분 비교
  - R3: 발행 금지 → 여기서 멈추고 약사에게 알립니다.

### 2. 공식 출처 찾기

- `references/allowed-domains.md`의 도메인에 있는 문서만 근거로 씁니다.
- 검색어에 기관명이나 도메인을 넣어 찾습니다. 검색 결과에 허용 도메인 밖의 URL이 나오면 근거로 쓰지 않고 "참고만"으로 적습니다.
- 검색 결과의 요약문(스니펫)은 원문이 아닙니다. 반드시 페이지를 추출해서 읽습니다.
- 출처는 1~4개로 충분합니다. 필요 이상으로 검색하지 않습니다(검색 8회 이내).

### 3. 원문 저장

- `web_extract`로 페이지를 추출합니다.
- 추출한 텍스트를 **고치지 않고 그대로** `sources/<YYMMDD>/<번호>_<기관>.md`에 저장합니다. 파일 맨 위에는 다음 4줄만 덧붙입니다.
  ```
  URL: <주소>
  문서명: <페이지 제목>
  확인일: <오늘 날짜 YYYY-MM-DD>
  추출: web_extract (원문 그대로)
  ```
- 결과 끝에 `[TRUNCATED]` 표시가 있으면, 안내된 저장 파일을 `read_file`로 끝까지 읽어서 전체를 저장합니다.
- 본문이 거의 비어 있으면(동적 페이지, 로그인 필요 등) 그 출처는 "원문 미확보"로 기록합니다. 약사에게 해당 페이지를 PDF로 저장해 `sources/<YYMMDD>/`에 넣어 달라고 요청합니다.
- 발표일·개정일은 **원문에 적혀 있을 때만** 씁니다. 없으면 "미확인"입니다.

### 4. 주장 추출

주장 5~10개를 뽑고, 주장마다 다음을 정리합니다.

- 주장ID: `YYMMDD-C01`부터 순서대로
- 콘텐츠 표현: 일반인이 읽을 문장 (원문보다 강하게 말하지 않기)
- 근거 원문: 저장본에서 **글자 그대로 복사한** 1~3문장. 요약·의역 금지
- 원문 위치: 문단·표·페이지
- 적용 대상과 예외: 원문에 있는 범위만

### 5. 코드 검사 (execute_code로 반드시 실행)

아래 코드를 `execute_code`로 실행합니다. `claims` 목록만 이번 주장으로 바꿉니다. 검사 결과는 코드 출력값을 그대로 장부에 옮깁니다.

```python
import json, re, unicodedata
from urllib.parse import urlparse

ALLOWED = ["mfds.go.kr", "kdca.go.kr", "mohw.go.kr", "me.go.kr", "busan.go.kr", "law.go.kr",
           "hira.or.kr", "nhis.or.kr", "who.int", "cochranelibrary.com", "ncbi.nlm.nih.gov", "data.go.kr"]
EXTRA_DOMAINS = []  # 부산 구청 도메인 등 약사가 허용한 도메인을 여기에 추가
UNITS = r"(mg|g|kg|mL|ml|L|㎎|㎖|mcg|μg|IU|%|정|캡슐|포|회|일|주|개월|년|세|시간|분|℃)"
NUM_UNIT = re.compile(r"(\d+(?:[.,]\d+)*)\s*" + UNITS + r"?")

def norm(s):
    s = unicodedata.normalize("NFKC", s).replace("​", "")
    return re.sub(r"\s+", " ", s).strip()

def domain_ok(url):
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in ALLOWED + EXTRA_DOMAINS)

def check(claims):
    out = []
    for c in claims:
        with open(c["source_file"], encoding="utf-8") as f:
            src = norm(f.read())
        quote = norm(c["quote"])
        quote_ok = bool(quote) and quote in src
        pairs = NUM_UNIT.findall(norm(c["expression"]))
        missing = []
        for num, unit in pairs:
            pat = re.escape(num) + (r"\s*" + re.escape(unit) if unit else r"(?!\d)")
            if not re.search(pat, quote):
                missing.append(num + unit)
        out.append({
            "주장ID": c["id"],
            "허용 도메인": "예" if domain_ok(c["url"]) else "아니오",
            "인용 일치(코드)": "일치" if quote_ok else "불일치",
            "숫자·단위 일치(코드)": "해당 없음" if not pairs else ("일치" if not missing else "불일치: " + ", ".join(missing)),
        })
    print(json.dumps(out, ensure_ascii=False, indent=1))

claims = [
    # {"id": "260929-C01", "expression": "콘텐츠 표현", "quote": "근거 원문 그대로",
    #  "source_file": "sources/260929/01_busan.md", "url": "https://www.busan.go.kr/..."},
]
check(claims)
```

- `execute_code`를 쓸 수 없는 환경이면 두 코드 검사 칸을 "미검사"로 적습니다. 직접 눈으로 비교했더라도 "일치"로 적지 않습니다.
- "불일치"가 나오면 인용문을 다시 복사하거나 표현을 원문 범위로 줄인 뒤 **한 번만** 다시 검사합니다. 그래도 불일치면 보류합니다.

### 6. 뒷받침 판정 (모델 판단)

- 근거 원문이 콘텐츠 표현을 **직접** 말하면 "지지"로 판정합니다.
- 일부만 말하거나 추론이 한 단계라도 필요하면 "부분"으로 판정합니다.
- 관련이 약하면 "불충분"으로 판정합니다.
- 판정 뒤에 모델명을 붙입니다. 예: `지지 (claude-opus-5-5)`
- 출처가 둘 이상이면 서로 충돌하는지 확인해 "없음" 또는 "있음(내용)"으로 적습니다.

### 7. 검증 상태 결정

| 조건 | 검증 상태 | 약사 검토 필요 |
|---|---|---|
| 허용 도메인 아님, 원문 미확보, 인용 불일치, 숫자 불일치, 판정 부분·불충분, 충돌 있음 중 하나라도 해당 | 보류 | 예 |
| 위 문제가 없고 R2 | 출처확인 (약사 원문 대조 대기) | 예 |
| 위 문제가 없고 R0·R1 | 검증완료 | 아니오 |

R2 주장은 약사가 "약사 확인" 칸에 날짜와 메모를 적은 뒤에만 "검증완료"로 바꿉니다.

### 8. 장부 저장 (execute_code)

`references/ledger-columns.md`의 25개 열 그대로 `ledger/근거장부_<YYMMDD>.csv`에 저장합니다. Excel에서 한글이 깨지지 않도록 `utf-8-sig`로 씁니다.

```python
import csv, os

HEADER = ["주장ID","주제ID","콘텐츠 표현","위험등급","출처 문서명","출처 URL","출처 기관 유형","근거 원문","원문 위치",
          "원문 저장 파일","발표일","개정일","확인일","적용 대상","예외·주의","인용 일치(코드)","숫자·단위 일치(코드)",
          "뒷받침 판정(모델)","출처 충돌","검증 상태","약사 검토 필요","약사 확인","사용 채널","승인 버전 해시","재확인 예정일"]

def append_rows(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, extrasaction="raise")
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in HEADER})
    print(f"{len(rows)}행 저장: {path}")

rows = [
    # {"주장ID": "260929-C01", "주제ID": "260929-폐의약품", ...},
]
append_rows("ledger/근거장부_260929.csv", rows)
```

"약사 확인", "사용 채널", "승인 버전 해시"는 비워 둡니다. "재확인 예정일"은 R2만 확인일 + 6개월로 적습니다.

### 9. 약사에게 보고

아래 항목만 짧게 보고합니다.

- 주장별 상태 표 (주장ID, 표현, 상태, 사유)
- 보류 항목마다 약사가 할 일 (예: "부산시 공지 PDF 저장", "R2 원문 대조")
- 핵심 메시지를 뒷받침하는 주장이 보류되면 "주제 연기 권장"이라고 적습니다.

## Pitfalls

- 인용문을 다듬거나 요약한 뒤 "원문"이라고 적지 않습니다.
- 원문에 없는 숫자, 단위, 대상, 기간을 표현에 넣지 않습니다.
- 언론 기사·블로그·SNS·쇼핑몰은 근거가 아닙니다.
- 게시일을 모르면 "미확인"이라고 씁니다. 확인일(오늘)과 섞지 않습니다.
- 다른 AI의 답, 이전 대화의 기억, 일반 상식은 근거가 아닙니다.
- 검색어에 환자 정보를 넣지 않습니다.

## Verification

- CSV 열이 25개이고, 머리행이 `references/ledger-columns.md`와 같습니다.
- "검증완료" 행은 모두 허용 도메인·인용 일치·숫자 일치(또는 해당 없음)·지지·충돌 없음이며, R2라면 약사 확인이 적혀 있습니다.
- 저장본 파일이 모든 출처 URL에 대해 존재합니다.
