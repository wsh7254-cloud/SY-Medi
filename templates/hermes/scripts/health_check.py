"""로그인 만료·추가 비용 위험 설정을 매일 점검한다(LLM 사용 안 함).

문제가 없으면 아무것도 출력하지 않는다 → 텔레그램에 알림이 가지 않는다(조용한 점검).
문제가 있으면 무엇을 해야 하는지 한국어로 출력한다 → 텔레그램 알림.

설치 위치: <HERMES_HOME>/scripts/health_check.py
테스트:     python health_check.py --verbose   (문제가 없어도 점검 결과를 모두 출력)
주의: 이 스크립트는 API 키 '값'을 절대 출력하지 않는다. 키 이름이 설정돼 있는지만 본다.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# ▼▼▼ 직접 바꿀 수 있는 부분 ▼▼▼
PROFILES = ["default", "researcher", "writer", "reviewer"]
CHECK_CLAUDE_CODE = True   # 검수 담당이 Claude Code(Claude Pro)를 쓰지 않으면 False
# ▲▲▲ 여기까지 ▲▲▲

# 이 이름이 .env 에 값과 함께 있으면, 구독 대신 종량제 API로 청구될 위험이 있다.
PAID_KEY_NAMES = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_TOKEN", "OPENROUTER_API_KEY",
                  "AI_GATEWAY_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY", "XAI_API_KEY")
AUTH_TROUBLE_WORDS = ("dead", "expired", "exhausted", "re-auth", "reauth", "invalid_grant", "not logged in")
VERBOSE = "--verbose" in sys.argv


def hermes(profile: str, *args: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "hermes_cli.main"]
    if profile != "default":
        cmd += ["-p", profile]
    return subprocess.run(cmd + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)


def main() -> int:
    problems: list[str] = []
    notes: list[str] = []

    for profile in PROFILES:
        # 1) 로그인 상태
        res = hermes(profile, "auth", "list")
        text = (res.stdout + res.stderr).lower()
        if res.returncode != 0 or any(w in text for w in AUTH_TROUBLE_WORDS):
            problems.append(f"🔑 [{profile}] ChatGPT 로그인 확인 필요 → PC에서: hermes -p {profile} auth add openai-codex"
                            if profile != "default" else
                            "🔑 [default] ChatGPT 로그인 확인 필요 → PC에서: hermes auth add openai-codex")
        else:
            notes.append(f"[{profile}] 로그인 정상")

        # 2) 종량제 API 키가 들어가 있는지(값은 읽지 않고 이름만 확인)
        env_res = hermes(profile, "config", "env-path")
        env_path = Path(env_res.stdout.strip().splitlines()[-1]) if env_res.stdout.strip() else None
        if env_path and env_path.exists():
            for raw in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                name, _, value = raw.strip().partition("=")
                if name.strip() in PAID_KEY_NAMES and value.strip().strip('"').strip("'"):
                    problems.append(f"💸 [{profile}] {name.strip()} 가 설정돼 있습니다. 추가 LLM 비용 위험 → "
                                    f"직접 선택한 것이 아니면 삭제: hermes -p {profile} config unset {name.strip()}")

    # 3) Claude Code(Claude Pro) 로그인 상태
    if CHECK_CLAUDE_CODE:
        claude = shutil.which("claude")
        if not claude:
            problems.append("🧩 Claude Code 를 찾을 수 없습니다(검수 2차 의견이 생략됩니다). 설치 여부를 확인하세요.")
        else:
            res = subprocess.run([claude, "auth", "status", "--text"], capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=60)
            out = (res.stdout + res.stderr).strip()
            if res.returncode != 0 or "not logged in" in out.lower():
                problems.append("🧩 Claude Code 로그인 필요 → PC의 PowerShell에서 claude 실행 후 브라우저 로그인")
            elif "api key" in out.lower():  # 표시 문구는 버전마다 다를 수 있음(7단계 테스트에서 확인)
                problems.append("💸 Claude Code 가 API 키(종량제)로 로그인된 것으로 보입니다. Claude Pro 계정으로 다시 로그인하세요.")
            else:
                notes.append("Claude Code 로그인 정상")

    if problems:
        print("🩺 자동화 PC 점검 결과 — 조치 필요\n" + "\n".join(problems))
    elif VERBOSE:
        print("🩺 점검 결과 이상 없음\n" + "\n".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
