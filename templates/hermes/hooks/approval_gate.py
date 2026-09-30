"""[2단계 전용] 게시 스크립트·유료 이미지/영상 생성 직전에 사람 승인을 강제하는 Hermes pre_tool_call 훅.

동작
- video_generate / image_generate / xai_video_*  → 예상 비용을 계산해 '사람 승인'으로 넘긴다.
  하루 승인 요청 횟수가 상한을 넘으면 아예 막는다(block).
- terminal 에서 publish_ 로 시작하는 게시 스크립트 실행 → '사람 승인'으로 넘긴다.
- terminal 에서 종량제 API 키를 설정하려는 명령 → 막는다(block).
- 그 외 → 통과({}).

중요
- cron·칸반 작업자처럼 사람이 없는 실행에서는 Hermes가 승인 요청을 자동 거절한다(approvals.cron_mode /
  single_query_mode 기본값 deny). 그래서 게시·유료 생성은 사람이 텔레그램/데스크톱 대화창에서 시작한 경우에만 된다.
- 이 훅은 'fail_closed: true' 로 등록해야 한다. 훅이 고장 나면 통과가 아니라 차단된다.
- 처음 등록 후 반드시 hermes hooks list 로 동의(consent) 상태를 확인한다. 동의되지 않은 훅은 게이트웨이에서 조용히 빠진다.

설치 위치(예): C:/Users/<사용자이름>/hermes-scripts/approval_gate.py  (가격표 media_prices.json 을 같은 폴더에)
테스트:       hermes hooks test pre_tool_call --for-tool video_generate
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRICES_FILE = HERE / "media_prices.json"
COUNTER_FILE = HERE / "approval_counter.json"

MEDIA_TOOLS = {"video_generate", "image_generate", "xai_video_edit", "xai_video_extend"}
PAID_KEY_NAMES = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "ANTHROPIC_TOKEN")


def reply(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def load_json(path: Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def bump_daily_counter(limit: int) -> int | None:
    """오늘 승인 요청 횟수를 1 올린다. 상한을 넘으면 None."""
    today = dt.date.today().isoformat()
    data = load_json(COUNTER_FILE, {})
    count = int(data.get(today, 0))
    if count >= limit:
        return None
    COUNTER_FILE.write_text(json.dumps({today: count + 1}), encoding="utf-8")
    return count + 1


def estimate(tool: str, args: dict, prices: dict) -> str:
    cur = prices.get("currency", "USD")
    if tool == "image_generate":
        unit = prices.get("image_per_image")
        n = int(args.get("num_images") or 1)
        return f"이미지 {n}장 × {unit} {cur} = {n * unit:.3f} {cur}" if unit else "단가 미입력(media_prices.json)"
    duration = args.get("duration")
    unit = prices.get("video_per_second")
    if not duration:
        return "길이 미지정(제작 도구 기본 길이 적용) — 단가표로 계산 불가, 승인 전 확인 필요"
    if not unit:
        return f"{duration}초 — 단가 미입력(media_prices.json)"
    return f"{duration}초 × {unit} {cur} = {float(duration) * unit:.3f} {cur}"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        reply({"action": "block", "message": "승인 게이트: 입력을 읽지 못해 차단했습니다."})
        return
    tool = payload.get("tool_name") or ""
    args = payload.get("tool_input") or {}

    if tool in MEDIA_TOOLS:
        prices = load_json(PRICES_FILE, {})
        limit = int(prices.get("daily_approval_request_limit", 3))
        count = bump_daily_counter(limit)
        if count is None:
            reply({"action": "block",
                   "message": f"오늘 유료 생성 승인 요청이 상한({limit}회)에 도달해 차단했습니다. 내일 다시 시도하세요."})
            return
        reply({"action": "approve", "rule_key": "media:paid",
               "message": (f"[유료 생성 승인 {count}/{limit}] 도구={tool}, 해상도={args.get('resolution', '기본')}, "
                           f"화면비={args.get('aspect_ratio', '기본')}, 예상 비용: {estimate(tool, args, prices)} "
                           "(직접 입력한 단가표 기준 추정치이며 실제 청구와 다를 수 있음)")})
        return

    if tool == "terminal":
        command = str(args.get("command", ""))
        if any(name in command for name in PAID_KEY_NAMES):
            reply({"action": "block", "message": "종량제 API 키 설정 명령은 자동화에서 실행할 수 없습니다."})
            return
        if "publish_" in command:
            reply({"action": "approve", "rule_key": "publish",
                   "message": f"[게시 승인] 다음 게시 명령을 실행할까요? {command[:300]}"})
            return

    reply({})


if __name__ == "__main__":
    main()
