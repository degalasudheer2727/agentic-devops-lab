"""Choose an allowlisted action for the synthetic shipping regression."""

import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

FIX = "restore_inclusive_threshold"
ESCALATE = "escalate"


def decide(observation):
    key = os.getenv("AI_GATEWAY_API_KEY")
    if not key:
        return FIX, "offline"
    # Send only a fixed synthetic observation, never local logs or source.
    body = {
        "model": "openai/gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": (
                'Return JSON {"action":"restore_inclusive_threshold"} or '
                '{"action":"escalate"}. Only restore the threshold when '
                'shipping should be free at 5000 cents and the code uses >.'
            )},
            {"role": "user", "content": observation},
        ],
        "response_format": {"type": "json_object"},
    }
    request = Request(
        "https://ai-gateway.vercel.sh/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read(65536))
        action = json.loads(payload["choices"][0]["message"]["content"])["action"]
    except (ValueError, KeyError, IndexError, TypeError, URLError, TimeoutError):
        return ESCALATE, "model_error"
    return (action if action in (FIX, ESCALATE) else ESCALATE), "model"
