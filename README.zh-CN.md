<div align="center">

# tx-38sev-cheaper-robber

[![Python](https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3776AB&style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![登录方式](https://img.shields.io/static/v1?label=%E7%99%BB%E5%BD%95%E6%96%B9%E5%BC%8F&message=Playwright%20%E6%89%AB%E7%A0%81&color=2EAD33&style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev/)
[![平台](https://img.shields.io/static/v1?label=%E5%B9%B3%E5%8F%B0&message=Windows&color=0078D6&style=flat-square&logo=windows11&logoColor=white)](#快速开始)
[![许可证](https://img.shields.io/static/v1?label=%E8%AE%B8%E5%8F%AF%E8%AF%81&message=GPL-3.0&color=2563EB&style=flat-square)](LICENSE)
[![星标](https://img.shields.io/github/stars/Cec1c/tx-38sev-cheaper-robber?style=flat-square&label=%E6%98%9F%E6%A0%87)](https://github.com/Cec1c/tx-38sev-cheaper-robber/stargazers)
[![最新提交](https://img.shields.io/github/last-commit/Cec1c/tx-38sev-cheaper-robber?style=flat-square&label=%E6%9C%80%E6%96%B0%E6%8F%90%E4%BA%A4)](https://github.com/Cec1c/tx-38sev-cheaper-robber/commits)
[![HTTP](https://img.shields.io/static/v1?label=HTTP&message=requests&color=2CA5E0&style=flat-square)](#工作原理)

腾讯云轻量应用服务器（38 元/年）秒杀活动自动抢购 —— 实战验证：免浏览器下单（g_tk 计算 CSRF）、场次 ID 自动获取、人脸/资格预检、带抖动的轮次开抢策略。

[English](README.md) ｜ [快速开始](#快速开始) ｜ [文档](#文档) ｜ [致谢](#致谢)

</div>

> [!IMPORTANT]
> 活动限**新用户**参与（同一实名限购 1 台），且可能要求**人脸核身**。每场开抢前先运行 `morning_check.py`：检查登录态、人脸核身、购买资格与当日场次 ID。若存在未支付订单（1101411），在付款或取消之前重试全部无效。

> [!NOTE]
> 仅供个人学习研究。自动化抢购可能违反活动规则，风险自担。基础脚本、错误码手册与实战笔记来自 [Allenalonel/tencentyun-seckill](https://github.com/Allenalonel/tencentyun-seckill)。

## 能做什么

- **扫码登录**：`get_cookies.py` 弹出浏览器扫码，保存登录态到 `cookies.json`，并自动检查人脸核身状态（未通过会引导完成）
- **免浏览器下单**：`x-csrf-token` 由 `skey` cookie 经 g_tk（djb2）算法计算，开抢阶段纯 `requests`，不依赖页面与浏览器
- **场次 ID 自动获取**：下单负载里的 `business.id` 就是当日场次 ID，启动时自动从 `query-seckill-by-date` 按开售时间精确匹配
- **开抢前预检**：登录态、人脸核身、购买资格、库存配额全部提前核对
- **轮次开抢**：提前 1.5 秒起打；每轮 3 地域并发；轮间 350~600ms 抖动；遇 408 退避 1.5s；重试窗口 30 秒；单请求超时 3 秒
- **未支付订单识别**：收到 `1101411` 立即停止重试并自动打开付款页（未付单占着限购配额，重试无意义）
- **一天两场**：`launch_today.py` 自动挂起 10:00 与 15:00 两场后台监听，日志分别写入 `run_1000.log` / `run_1500.log`

## 工作原理

1. `get_cookies.py` 获取登录 cookies；CSRF 由 `skey` 现算，开抢阶段零浏览器依赖
2. 开抢前 60 秒做一次钟差校准（5 次采样取中位数，`Date` 头按 +500ms 对中并补偿半 RTT）
3. 到点前 1.5 秒开始轮次：每轮对每个地域并发发一次下单请求
4. 响应分类处理 —— `1100205` / `1100136` / `1100110` 继续重试，`408` 退避，资格类错误或 `1101411` 立即停止
5. 成功时打印订单号与付款链接并自动打开；**务必 1 小时内付款**

核心参数（`CONFIG` 或 `config.json` 可调）：

| 参数 | 默认值 | 作用 |
| --- | --- | --- |
| `LEAD_MS` | 1500 | 提前起打毫秒数 |
| `RETRY_WINDOW_S` | 30 | 开闸后重试窗口 |
| `BACKOFF_408_S` | 1.5 | 触发限流后的退避秒数 |
| `ROUND_GAP_S` + `ROUND_JITTER_S` | 0.35 + 0~0.25 | 轮间间隔与抖动 |
| `BUY_TIMEOUT_S` | 3 | 单请求超时（快速失败） |
| `SYNC_AHEAD_S` | 60 | 钟差校准提前量 |

## 快速开始

前提：Windows、Python 3.10+，安装依赖：

```bat
pip install requests playwright
python -m playwright install chromium
```

1. 登录（有效期数天；`morning_check.py` 报 `NOT-LOGINED` 时重跑）：

```bat
python get_cookies.py
```

用微信扫码，脚本会保存 `cookies.json` 并检查人脸核身。

2. 开抢前自检：

```bat
python morning_check.py
```

预期：四行 ✅（登录态、人脸核身、购买资格、今日场次 ID）。

3. 拉起今日两场监听（或单场运行）：

```bat
python launch_today.py
:: 单场指定时间
python snap_up_server.py "2026-01-01 10:00:00"
```

Windows 下也可直接双击 `早上抢购.bat`（自检 + 启动一步完成）。

## 文档

| 任务 | 指南 |
| --- | --- |
| 查询返回码含义 | [腾讯云活动接口错误码全景速查手册](docs/腾讯云活动接口错误码全景速查手册.md) |
| 准备一个符合资格的新账号 | [腾讯云新账号准备指南](docs/腾讯云新账号准备指南.md) |
| 每日流程与机制细节 | [运维笔记](docs/运维笔记.md) |

## 致谢

- [Allenalonel/tencentyun-seckill](https://github.com/Allenalonel/tencentyun-seckill) —— 基础脚本、实战笔记与错误码手册
- [genhao3/TencentCloud](https://github.com/genhao3/TencentCloud) —— 验证过成功的时间参数与 `skey` → CSRF 推导
- [zhouyifan007/tencentyun-snake-up](https://github.com/zhouyifan007/tencentyun-snake-up) —— 库存配额轮询思路

## 许可

本项目基于 [GNU General Public License v3.0](LICENSE) 发布 —— Copyright (C) 2026 Cec1c。

基础脚本派生自 [Allenalonel/tencentyun-seckill](https://github.com/Allenalonel/tencentyun-seckill)（原仓库未声明许可证），该部分版权归原作者所有，此处署名收录。
