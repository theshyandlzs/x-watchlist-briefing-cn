# x-watchlist-briefing-cn

面向 OpenClaw 的中文 X 观察池简报 skill。  
它会围绕固定的 129 个账号观察池，按 9 个领域生成带原始推文链接的中文时效简报。

适合这类请求：

- “过去 24 小时这批账号都讨论了什么”
- “总结近 7 天 AI / 出海 / SaaS / 独立开发动态”
- “按 9 个领域输出周报，所有结论都带来源链接”

## What It Does

这份 skill 聚焦固定观察池，而不是全网关键词搜索。

它会：

- 读取 `references/watchlist.json` 中的 129 条账号记录
- 按 handle 去重后抓取 111 个唯一账号
- 按 9 个领域输出中文简报
- 强制区分 `事实` 与 `观点/判断`
- 为每条结论附上原始 X 链接
- 对 `400 no tweet` 和 `429` 做更稳的抓取策略处理

覆盖领域：

1. AI
2. 创业者
3. SaaS 和 APP 产品
4. 出海
5. 海外手机卡
6. 独立开发者
7. OpenClaw
8. 知识分享
9. 副业

## Why This Exists

常见的 X 总结有两个问题：

- 只做关键词搜索，结果不稳定，容易偏题
- 没有来源链接，或者把观点写成事实

这个 skill 的设计目标很明确：

- 只追固定观察池
- 只保留高信号内容
- 输出适合中文读者快速消费的时效简报
- 尽量减少 OpenTwitter 时间线端点不稳定带来的漏抓

## Install

### Option 1: Install From GitHub

适合公开仓库：

```bash
npx skills add <github-owner>/<github-repo> --agent openclaw
```

如果你的仓库名就叫 `x-watchlist-briefing-cn`，通常会是：

```bash
npx skills add <github-owner>/x-watchlist-briefing-cn --agent openclaw
```

### Option 2: Manual Install

适合想手动 clone 的用户：

```bash
git clone https://github.com/<github-owner>/<github-repo>.git x-watchlist-briefing-cn
export TWITTER_TOKEN="<your-token>"
cp -r ./x-watchlist-briefing-cn ~/.openclaw/skills/
```

复制完成后，目标目录应当是：

```bash
~/.openclaw/skills/x-watchlist-briefing-cn
```

## Configuration

### API Token

这份 OpenClaw 版 skill 不把 token 写进仓库文件。  
运行时通过环境变量读取：

```bash
export TWITTER_TOKEN="<your-token>"
```

获取 token：

- [https://6551.io/mcp](https://6551.io/mcp)

依赖：

- `curl`
- `python3`
- `TWITTER_TOKEN`

## Working Directory

这个 skill 里的辅助脚本使用的是 repo 内的 `scripts/` 目录。

所以在执行下面这些命令前，先确保你已经进入这个 skill 的根目录，或者直接使用该目录下脚本的绝对路径。

常见根目录有两个：

- `~/.openclaw/skills/x-watchlist-briefing-cn`
- 你本地 clone 下来的 `x-watchlist-briefing-cn` 仓库根目录

如果你在别的目录里直接运行：

```bash
python3 scripts/show_watchlist.py --summary
```

Python 会按当前目录去找 `scripts/show_watchlist.py`，然后报 `No such file or directory`。

## Quick Start

安装完成后，可以直接在 OpenClaw 里这样用：

- “使用 x-watchlist-briefing-cn，总结过去 24 小时这批账号讨论了什么”
- “使用 x-watchlist-briefing-cn，总结近 7 天 AI 和出海领域动态”
- “使用 x-watchlist-briefing-cn，按 9 个领域输出本周简报，并附来源链接”

推荐输入要素：

- 明确时间终点
- 明确时间窗口
- 明确是否要全量 9 个领域，还是只看部分领域

## Data Source And Fetch Strategy

数据源基于 6551 OpenTwitter API，运行方式沿用 OpenClaw 场景下的：

- `curl`
- `TWITTER_TOKEN`

为了降低漏抓率，这份 skill 明确使用稳定抓取梯子：

1. 先查账号资料，获取 canonical `screenName`
2. 再打 `twitter_user_tweets`
3. 如果返回 `400 no tweet`，立刻 fallback 到账号维度搜索
4. 如果返回 `429`，执行 bounded backoff，而不是直接判失败

这意味着：

- `400 no tweet` 不等于账号失效
- `429` 不等于没有内容
- 对时间线端点不稳定的账号，会继续尝试 search fallback

## Output Format

默认输出结构：

1. 标题与绝对时间窗口
2. 一句话速览
3. AI
4. 创业者
5. SaaS 和 APP 产品
6. 出海
7. 海外手机卡
8. 独立开发者
9. OpenClaw
10. 知识分享
11. 副业
12. 跨领域信号
13. 无公开更新 / 无高价值更新账号

每条信息使用统一格式：

- `结论`
- `事实`
- `观点/判断`
- `为什么重要`
- `来源`

## Project Structure

```text
x-watchlist-briefing-cn/
├── SKILL.md
├── package.json
├── README.md
├── references/
│   ├── watchlist.json
│   └── opentwitter-openclaw.md
└── scripts/
    ├── render_digest_template.py
    └── show_watchlist.py
```

关键文件：

- `SKILL.md`: OpenClaw skill 主说明
- `references/watchlist.json`: 129 账号观察池
- `references/opentwitter-openclaw.md`: OpenTwitter 端点说明和抓取策略
- `scripts/show_watchlist.py`: 观察池统计与检查
- `scripts/render_digest_template.py`: 简报模板生成

## Local Validation

可以先本地检查观察池和模板脚本：

```bash
cd ~/.openclaw/skills/x-watchlist-briefing-cn
python3 scripts/show_watchlist.py --summary
python3 scripts/show_watchlist.py --duplicates
python3 scripts/render_digest_template.py --end '2026-03-08T09:00:00+08:00' --hours 48
```

或者直接用绝对路径：

```bash
python3 ~/.openclaw/skills/x-watchlist-briefing-cn/scripts/show_watchlist.py --summary
```
