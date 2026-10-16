<div align="center">

# tx-38sev-cheaper-robber

[![Python](https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3776AB&style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Login](https://img.shields.io/static/v1?label=Login&message=Playwright%20QR&color=2EAD33&style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Platform](https://img.shields.io/static/v1?label=Platform&message=Windows&color=0078D6&style=flat-square&logo=windows11&logoColor=white)](#quick-start)
[![License](https://img.shields.io/static/v1?label=License&message=GPL-3.0&color=2563EB&style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Cec1c/tx-38sev-cheaper-robber?style=flat-square&label=stars)](https://github.com/Cec1c/tx-38sev-cheaper-robber/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/Cec1c/tx-38sev-cheaper-robber?style=flat-square)](https://github.com/Cec1c/tx-38sev-cheaper-robber/commits)
[![HTTP](https://img.shields.io/static/v1?label=HTTP&message=requests&color=2CA5E0&style=flat-square)](#how-it-works)

Prepare your Tencent Cloud login, check eligibility, and schedule order attempts for the Lighthouse ¥38/year flash sale. The tool resolves the day's session ID and submits requests at the configured time.

[简体中文](README.zh-CN.md) ｜ [Quick Start](#quick-start) ｜ [Docs](#docs) ｜ [Credits](#credits)

</div>

> [!IMPORTANT]
> The activity is **new-user only** (one purchase per real-name identity) and may require **face verification**. Run `morning_check.py` before each session — it validates login, face check, purchase eligibility and the day's session ID. An unpaid order blocks all further attempts until it is paid or cancelled.

## What It Does

- **QR login capture** — `get_cookies.py` opens a browser, saves the login state to `cookies.json`, and checks face-verification status, guiding you through verification if needed.
- **HTTP ordering** — after browser login, order requests use `requests` and derive `x-csrf-token` from the `skey` cookie with g_tk (djb2).
- **Auto-resolved session ID** — the `business.id` in the order payload equals the day's session ID; it is fetched automatically from `query-seckill-by-date` by matching the target start time.
- **Preflight checks** — login state, face check, purchase eligibility and stock quota are verified before the sale.
- **Round-based firing** — starts 1.5 s early, then one round (3 regions concurrently) every 350–600 ms with jitter; backs off 1.5 s on `408`; 30 s retry window; 3 s per-request timeout.
- **Unpaid-order detection** — on `1101411`, it stops retrying and opens the payment page so you can pay or cancel the existing order.
- **Two sessions a day** — `launch_today.py` starts background listeners for both the 10:00 and 15:00 windows, logging to `run_1000.log` / `run_1500.log`.

## Quick Start

Prerequisites: Windows, Python 3.10+, and dependencies:

```bat
pip install requests playwright
python -m playwright install chromium
```

1. Capture your login. Repeat this step when `morning_check.py` reports `NOT-LOGINED`:

```bat
python get_cookies.py
```

Scan the QR code with WeChat; the script saves `cookies.json` and verifies face check.

2. Self-check before the sale:

```bat
python morning_check.py
```

Continue when all four checks pass: login, face verification, purchase eligibility, and today's session ID.

3. Schedule today's 10:00 and 15:00 sessions, or replace the example date below to run one session:

```bat
python launch_today.py
:: single session at an explicit time
python snap_up_server.py "2026-01-01 10:00:00"
```

Windows users can also double-click `早上抢购.bat` (self-check + launch in one step).

## How It Works

1. `get_cookies.py` captures the login cookies; the CSRF token is computed from `skey` — the firing stage is pure `requests`.
2. Clock skew is calibrated once, 60 s before the sale (median of 5 samples, `Date` header centered at `+500 ms` with half-RTT compensation).
3. 1.5 s before the target time, rounds begin: each round fires one order request per region concurrently.
4. Responses are classified — retry on `1100205` / `1100136` / `1100110`, back off on `408`, stop on qualification errors or `1101411`.
5. On success the order ID and payment link are printed and opened; **pay within 1 hour**.

Key parameters (editable in `CONFIG` / `config.json`):

| Parameter | Default | Purpose |
| --- | --- | --- |
| `LEAD_MS` | 1500 | Start firing this early |
| `RETRY_WINDOW_S` | 30 | Stop re-firing this long after open |
| `BACKOFF_408_S` | 1.5 | Cool-down after rate limiting |
| `ROUND_GAP_S` + `ROUND_JITTER_S` | 0.35 + 0~0.25 | Pacing between rounds |
| `BUY_TIMEOUT_S` | 3 | Per-request timeout (fail fast) |
| `SYNC_AHEAD_S` | 60 | Clock re-sync lead time |

## Docs

| Task | Guide |
| --- | --- |
| Look up an error code | [API error-code manual (zh)](docs/腾讯云活动接口错误码全景速查手册.md) |
| Prepare a new eligible account | [New account guide (zh)](docs/腾讯云新账号准备指南.md) |
| Daily operation & mechanics | [Operating notes (zh)](docs/运维笔记.md) |

## Credits

- [Allenalonel/tencentyun-seckill](https://github.com/Allenalonel/tencentyun-seckill) — base script, real-fight notes and the error-code manual.
- [genhao3/TencentCloud](https://github.com/genhao3/TencentCloud) — success-verified timing parameters and the `skey` → CSRF derivation.
- [zhouyifan007/tencentyun-snake-up](https://github.com/zhouyifan007/tencentyun-snake-up) — stock-quota polling approach.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE) — Copyright (C) 2026 Cec1c.

The base script is derived from [Allenalonel/tencentyun-seckill](https://github.com/Allenalonel/tencentyun-seckill), which declares no license; copyright of that portion remains with its original author and is included here with credit.
