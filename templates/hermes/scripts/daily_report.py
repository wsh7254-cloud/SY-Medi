"""오늘 만든 칸반 카드의 진행 상태를 요약해 텔레그램으로 보낸다(LLM 사용 안 함).

Hermes cron 의 no-agent 모드로 실행하면 이 스크립트가 출력한 글이 그대로 텔레그램에 전달된다.
설치 위치: <HERMES_HOME>/scripts/daily_report.py
테스트:     python daily_report.py --sample   (Hermes 없이 예시 데이터로 출력 모양만 확인)
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys

STATUS_LABEL = {
    "triage": "🟡 분류 대기", "todo": "⏳ 앞 단계 대기", "ready": "⏳ 실행 대기",
    "running": "🔄 진행 중", "blocked": "⛔ 멈춤(사람 확인 필요)", "review": "🔍 검토 중",
    "done": "✅ 완료", "archived": "📦 보관",
}

SAMPLE = [
    {"id": "t_a1", "title": "[2026-10-01-1] 1.자료조사: 폐의약품 버리는 법", "status": "done"},
    {"id": "t_a2", "title": "[2026-10-01-1] 2.기획·원고: 폐의약품 버리는 법", "status": "done"},
    {"id": "t_a3", "title": "[2026-10-01-1] 3.검수: 폐의약품 버리는 법", "status": "blocked",
     "last_failure_error": "usage limit reached"},
]


def list_tasks() -> list[dict]:
    if "--sample" in sys.argv:
        return SAMPLE
    cmd = [sys.executable, "-m", "hermes_cli.main", "kanban", "list", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if res.returncode != 0:
        raise RuntimeError((res.stderr or res.stdout)[-600:])
    return json.loads(res.stdout)


def main() -> int:
    today = "2026-10-01" if "--sample" in sys.argv else dt.date.today().isoformat()
    tasks = [t for t in list_tasks() if str(t.get("title", "")).startswith(f"[{today}")]
    if not tasks:
        print(f"📭 {today} 제작 카드가 없습니다. (아침 카드 생성 작업이 실행됐는지 확인하세요: hermes cron list)")
        return 0

    lines = [f"📋 {today} 제작 현황"]
    ready_for_approval = []
    for t in sorted(tasks, key=lambda x: x.get("title", "")):
        status = t.get("status", "")
        line = f"- {STATUS_LABEL.get(status, status)} {t.get('title')} ({t.get('id')})"
        err = t.get("last_failure_error")
        if status == "blocked" and err:
            line += f"\n    └ 이유: {str(err)[:120]}"
        lines.append(line)
        if status == "done" and "3.검수" in str(t.get("title", "")):
            ready_for_approval.append(str(t.get("title")).split("]")[0].strip("["))

    if ready_for_approval:
        lines.append("")
        lines.append("👉 승인 검토 가능: " + ", ".join(ready_for_approval))
        lines.append("   이 대화창에 '승인 검토 <번호>' 라고 보내면 패키지 요약과 review.md 결론을 보여줍니다.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
