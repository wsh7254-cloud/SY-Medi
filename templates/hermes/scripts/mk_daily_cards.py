"""오늘 날짜의 콘텐츠 주제마다 칸반 카드 3장(자료조사 -> 기획·원고 -> 검수)을 만든다.

- LLM을 쓰지 않는다. 구독 사용량이 0이다(Hermes cron의 no-agent 모드로 실행).
- 같은 날 두 번 실행돼도 카드가 중복 생성되지 않는다(idempotency key).
- 게시·유료 미디어 생성 카드는 만들지 않는다. 그 단계는 사람이 승인한 뒤에만 진행한다.

설치 위치: <HERMES_HOME>/scripts/mk_daily_cards.py
  HERMES_HOME 확인: PowerShell에서  hermes config path  (출력된 config.yaml이 있는 폴더)
테스트:     python mk_daily_cards.py --dry-run   (실제 카드를 만들지 않고 명령만 출력)
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

# ▼▼▼ 직접 바꿀 수 있는 부분 ▼▼▼
MARKETING_HOME = Path.home() / "marketing"   # 작업 폴더(캘린더·결과물 저장 위치)
PROFILES = {"research": "researcher", "write": "writer", "review": "reviewer"}
MAX_RETRIES = "2"      # 카드 1장당 총 시도 횟수 상한(실패 반복으로 사용량이 새지 않게)
MAX_RUNTIME = "40m"    # 카드 1장당 최대 실행 시간
# ▲▲▲ 여기까지 ▲▲▲

CALENDAR = MARKETING_HOME / "content_calendar.csv"
DRY_RUN = "--dry-run" in sys.argv


def read_calendar(path: Path) -> list[dict]:
    """엑셀에서 저장한 CSV(UTF-8 또는 CP949)를 모두 읽는다."""
    for encoding in ("utf-8-sig", "cp949"):
        try:
            with path.open(encoding=encoding, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"{path.name} 인코딩을 읽을 수 없습니다. 'CSV UTF-8'로 다시 저장하세요.")


def kanban(*args: str) -> dict:
    """Hermes에 포함된 Python으로 Hermes CLI를 직접 호출한다(WindowsApps 실행 별칭 문제 회피)."""
    cmd = [sys.executable, "-m", "hermes_cli.main", "kanban", *args, "--json"]
    if DRY_RUN:
        print("[dry-run]", " ".join(cmd))
        return {"id": "t_dry"}
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    if res.returncode != 0:
        raise RuntimeError((res.stderr or res.stdout)[-600:])
    return json.loads(res.stdout)


def write_brief(folder: Path, name: str, text: str) -> Path:
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def briefs(topic: str, channels: str, risk: str, memo: str) -> dict[str, str]:
    common = (
        f"- 주제: {topic}\n- 대상 채널: {channels or '인스타그램, 유튜브 쇼츠, 네이버 블로그·클립(확인 필요)'}\n"
        f"- 위험 등급: {risk or '미지정'}\n- 메모: {memo or '없음'}\n"
        "- 작업 폴더: 이 카드의 작업 폴더(현재 폴더). 모든 결과 파일은 여기에 저장한다.\n"
        "- 환자 개인정보·실제 상담 사례·처방 내용은 절대 다루지 않는다.\n"
    )
    return {
        "research": (
            "# 1. 자료조사 지시\n" + common +
            "\n## 할 일\n"
            "1. 허용 출처에서만 근거를 찾는다: mfds.go.kr(식약처·의약품안전나라), kdca.go.kr(질병관리청·국가건강정보포털),\n"
            "   mohw.go.kr, me.go.kr, busan.go.kr, law.go.kr, hira.or.kr, nhis.or.kr, who.int, pubmed.ncbi.nlm.nih.gov\n"
            "2. evidence.md 에 주장별로 기록한다: 주장ID | 출처 기관 | 문서 제목 | URL | 확인일 | 원문 인용(그대로 복사) | 요약\n"
            "3. 근거를 찾지 못한 주장은 '근거 없음'으로 표시하고 원고에 쓰지 말라고 적는다.\n"
            "4. 끝나면 kanban_complete 로 완료한다(요약: 근거 개수, 빠진 부분). artifacts 에 evidence.md 를 넣는다.\n"
            "5. 공식 출처를 전혀 찾지 못하면 kanban_block(kind=needs_input) 으로 멈추고 이유를 적는다.\n"
        ),
        "write": (
            "# 2. 기획·원고 지시\n" + common +
            "\n## 할 일\n"
            "1. evidence.md 에 있는 주장만 사용한다. 새로운 의학적 주장을 추가하지 않는다.\n"
            "2. 채널별 원고를 만든다: draft_instagram.md(캡션+카드뉴스 문안), draft_shorts.md(60초 이하 대본+자막),\n"
            "   draft_naver_blog.md(블로그 본문), draft_naver_clip.md(클립 대본·설명).\n"
            "3. media_brief.md(이미지·영상 제작 지시서)를 만든다: 장면별 설명, 길이(초), 화면비 9:16,\n"
            "   '이미지 속 한글·숫자는 AI가 그리지 않고 템플릿에 넣음', '실제 약 포장·알약·실존 인물·약국 내부 AI 생성 금지'.\n"
            "4. 금지: 치료 효과 보장, 의약품 구매·온라인 판매 유도, 특정 병원 안내, 전문의약품 광고, 체험담형 표현.\n"
            "5. 끝나면 kanban_complete 로 완료한다. artifacts 에 위 파일들을 넣는다.\n"
        ),
        "review": (
            "# 3. 검수 지시\n" + common +
            "\n## 할 일\n"
            "1. 모든 draft_*.md 문장을 evidence.md 원문 인용과 대조한다. 근거 없는 문장은 모두 목록으로 적는다.\n"
            "2. 숫자·단위·성분명이 근거와 한 글자라도 다르면 '불일치'로 적는다.\n"
            "3. 약사법·의약품 광고·건강기능식품 광고 규정상 위험 표현, 브랜드 말투, 채널 규격을 점검한다.\n"
            "4. (선택) 2차 의견: Claude Code 가 설치돼 있으면 아래처럼 Claude Pro 사용량으로 교차 검토를 받는다.\n"
            "   cat evidence.md draft_*.md | claude -p \"약사 콘텐츠 검수자로서 근거와 원고의 불일치, 과장·위험 표현만 목록으로 답하라\" --model sonnet --max-turns 2 > claude_review.md\n"
            "   (--bare 는 쓰지 않는다. 실패하거나 사용량 한도 메시지가 나오면 건너뛰고 review.md 에 '2차 의견 생략'이라고 적는다.)\n"
            "5. review.md 에 결론을 쓴다: '승인 요청 가능' 또는 '수정 필요(항목)'.\n"
            "6. 끝나면 kanban_complete 로 완료한다. 게시·유료 이미지/영상 생성은 절대 하지 않는다.\n"
        ),
    }


def main() -> int:
    if not CALENDAR.exists():
        print(f"⚠️ 콘텐츠 캘린더가 없습니다: {CALENDAR}")
        return 0
    today = dt.date.today().isoformat()
    rows = [r for r in read_calendar(CALENDAR)
            if (r.get("날짜") or "").strip() == today and (r.get("상태") or "예정").strip() in ("예정", "")]
    if not rows:
        print(f"📭 {today} 예정된 주제가 캘린더에 없습니다. content_calendar.csv 를 확인하세요.")
        return 0

    lines = [f"🗂 {today} 제작 카드 생성"]
    for n, row in enumerate(rows, start=1):
        topic = (row.get("주제") or "").strip()
        folder = MARKETING_HOME / "content" / f"{today}-{n}"
        folder.mkdir(parents=True, exist_ok=True)
        texts = briefs(topic, row.get("채널", ""), row.get("위험등급", ""), row.get("메모", ""))
        parent = None
        ids = []
        for step, label in (("research", "1.자료조사"), ("write", "2.기획·원고"), ("review", "3.검수")):
            brief = write_brief(folder, f"brief_{step}.md", texts[step])
            args = ["create", f"[{today}-{n}] {label}: {topic}",
                    "--assignee", PROFILES[step],
                    "--body-file", str(brief),
                    "--workspace", f"dir:{folder.as_posix()}",
                    "--idempotency-key", f"{today}-{n}-{step}",
                    "--max-retries", MAX_RETRIES,
                    "--max-runtime", MAX_RUNTIME]
            if parent:
                args += ["--parent", parent]
            parent = str(kanban(*args)["id"])
            ids.append(parent)
        lines.append(f"- {n}. {topic} → 카드 {' → '.join(ids)}")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
