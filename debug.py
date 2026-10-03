import json
import os

import requests

tok = os.environ.get("METACULUS_TOKEN", "")
print("token present:", bool(tok), "length:", len(tok))
H = {"Authorization": f"Token {tok}"}
BASE = "https://www.metaculus.com/api"


def show(label, url, params):
    r = requests.get(BASE + url, params=params, headers=H, timeout=60)
    print("==", label, "| HTTP", r.status_code, "|", r.headers.get("content-type"))
    try:
        j = r.json()
    except Exception:
        print(r.text[:300])
        return
    if label == "me":
        print("username:", j.get("username"), "| is_bot:", j.get("is_bot"))
        return
    if isinstance(j, dict) and "results" in j:
        print("count:", j.get("count"), "| returned:", len(j["results"]))
        for p in j["results"][:12]:
            q = p.get("question") or {}
            print(
                " ",
                p.get("id"),
                p.get("status"),
                (p.get("title") or "")[:70],
                "| open:",
                (p.get("open_time") or "")[:10],
                "| qstatus:",
                q.get("status"),
            )
    else:
        print(json.dumps(j)[:400])


show("me", "/users/me/", {})
show("open t=33121", "/posts/", {"tournaments": 33121, "statuses": "open", "limit": 20})
show("any t=33121", "/posts/", {"tournaments": 33121, "limit": 20})
show("slug open", "/posts/", {"tournaments": "fall-futureeval-2026", "statuses": "open", "limit": 20})
show("minibench open", "/posts/", {"tournaments": "minibench", "statuses": "open", "limit": 20})
show(
    "bot-style params",
    "/posts/",
    {"tournaments": 33121, "statuses": "open", "limit": 20, "with_cp": "true", "order_by": "-hotness"},
)
