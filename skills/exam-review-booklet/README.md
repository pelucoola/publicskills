# 错题讲评册

把孩子已经写过的试卷、作业照片，整理成可以直接打印的讲评册。孩子能在同一份讲义里对照自己的原作答，弄清错在哪里、每一步应该怎样想，并看到完整的参考答案和下一次做题的关键提醒。

适用于作业订正、考试复盘和阶段复习，也适合家长或老师准备一份能让孩子自行阅读的讲解材料。

| 项目 | 内容 |
| --- | --- |
| 技能名称 | `exam-review-booklet` |
| 当前版本 | 1.0.2 |
| 主要输出 | A4 横向 PDF、自包含打印网页 |
| 源任务日期 | 2026-10-25 |
| 本次更新 | 2026-10-26，清理与原任务相同的示例日期，更新脱敏安装包 |

## 讲评册里有什么

| 内容 | 如何呈现 |
| --- | --- |
| 原题与原作答 | 保留照片中的笔迹、批改和关键图形，方便回看孩子当时怎样写 |
| 错因分析 | 针对实际作答指出错误发生的位置，说明条件、概念或推理在哪一步没有对应好 |
| 逐步思路 | 解释先想什么、为什么添辅助线、条件如何转化、下一步依据是什么，补齐中间推理 |
| 完整参考答案 | 单独成块，便于学习规范书写；长题可以使用紧邻的答案页 |
| 关键指导 | 提炼下一次遇到同类问题时可执行的检查或思考动作 |
| 标题与日期 | 每页显示已确认的试卷标题、考试或作业日期、题号；页脚另列生成时间和页码 |

默认使用 A4 横向两栏：左侧是原题、原作答与辅助图，右侧是错因和思路。内容较长时自动续页，优先保证文字和截图清楚可读。

## 需要提供什么

- 清晰的试卷、作业照片、截图或扫描图，能看清题目、学生笔迹和图形。多张材料可以一起提供。
- 试卷标题及考试或作业日期。agent 会先提出候选值，让你确认或自行填写；没有年份时可只确认月日，不清楚日期时可以选择“日期未提供”。
- 如果有教师答案或批改说明，可以一并提供，用于核对。

每批新卷都会重新确认标题与日期。照片的拍摄时间、讲评册生成时间与考试日期分别记录。多份卷子默认分别出册；需要合并时，可以在调用时说明。

## 安装

### 从 GitHub 安装

在支持技能安装器的 Codex 中发送：

```text
用 $skill-installer 从以下目录安装 exam-review-booklet：
https://github.com/pelucoola/publicskills/tree/main/skills/exam-review-booklet
保留完整技能目录，并检查 Python 和中文字体依赖。
```

其他支持 Agent Skills 的 agent 可以使用同一目录链接，按其客户端支持的方法安装。手动安装时，复制整个 `exam-review-booklet` 文件夹到目标客户端识别的技能目录，不要只复制 `SKILL.md`。

### 从 ZIP 安装

[下载 1.0.2 安装包](https://github.com/pelucoola/publicskills/blob/main/dist/exam-review-booklet/exam-review-booklet-1.0.2.zip)，把它交给 agent，并发送：

```text
请安装 ZIP 中完整的 exam-review-booklet 技能文件夹，并检查它的运行依赖。
```

安装包的 [SHA-256 校验文件](https://github.com/pelucoola/publicskills/blob/main/dist/exam-review-booklet/exam-review-booklet-1.0.2.zip.sha256)可用于核对下载完整性。

## 怎么使用

安装后上传试卷或作业照片，再发送：

```text
用 $exam-review-booklet 生成错题讲评册。
先让我确认标题和考试或作业日期。
保留孩子的原作答，详细分析错因，补齐每一步思路，
给出完整参考答案和关键指导，生成可以直接打印的文件。
```

接下来会按以下顺序处理：

1. 阅读材料，区分不同卷子，提出标题和日期的候选值。
2. 等待你确认这些信息；同时可以继续识题、核对作答。
3. 独立求解，逐题整理原作答、错因、思路、参考答案与关键指导。
4. 排版成册，检查公式、截图、图形标签和分页，再交付文件。

客户端有互动提问工具时，会通过确认选项收集标题和日期；没有时，在普通对话中确认。标题和日期未确认前不会完成最终排版。

## 输出与打印

| 文件 | 用途 |
| --- | --- |
| `.pdf` | 直接阅读和打印 |
| `.html` | 在浏览器预览和打印；生成文件已内嵌所需图片、样式与字体 |
| `booklet.json` | 保存整理后的题目和排版内容，方便后续修改 |
| `.layout.json` | 记录页数、边界和排版诊断，供 agent 检查 |

打开 PDF 或网页即可预览。打印设置使用 **A4、横向、实际大小**。参考答案没有教师原版依据时，会标注“标准答案（按题面整理）”。

## 运行条件

| 条件 | 说明 |
| --- | --- |
| agent 能力 | 能识图、读取本地文件并执行 Python |
| Python | 3.10 或更高版本 |
| 必需库 | ReportLab、Pillow，已验证版本见 [requirements.txt](requirements.txt) |
| 中文字体 | 需要允许嵌入的 TrueType 字体；可由脚本发现已有字体，或通过 `--font` 指定 |
| 可选工具 | FontTools 可缩小网页内嵌字体体积；PDF 目视检查可使用 Poppler |

字体文件不包含在安装包中。只有聊天能力、没有文件与代码执行能力的环境，需要额外执行环境才能完成文件生成。

### 手动调用排版脚本

在技能目录下安装依赖：

```bash
python -m pip install -r requirements.txt
```

按 [排版数据协议](references/schema.md)准备已核验的 `booklet.json`，然后运行：

```bash
python scripts/render_booklet.py /path/to/booklet.json --output-dir /path/to/output
```

可加 `--font /path/to/ChineseFont.ttf` 指定字体。图片路径相对 `booklet.json` 所在目录解析，标题和日期的确认字段须为 `true`。

脚本负责排版，识题、判断错因、独立求解及教学讲解由使用技能的 agent 完成。具体工作方法见 [讲评与核验规则](references/review-method.md)，标题与日期的互动方法见 [确认指引](references/intake.md)。

## 技能文件

```text
exam-review-booklet/
├── README.md
├── SKILL.md
├── requirements.txt
├── agents/openai.yaml
├── assets/layout.css
├── references/
│   ├── intake.md
│   ├── review-method.md
│   └── schema.md
└── scripts/render_booklet.py
```

原始照片保留原样，裁图用于讲义；看不清或不能判定的内容会明确标记。生成结果需核验题目、推导与排版，不能用单个模糊或空白作答直接推断孩子整体不会。

文档中的题名、日期和作答示例均为虚构演示。学生照片、姓名、成绩、实际作答和生成的讲评册保存在当次任务目录，不放进公开技能目录或安装包。

排版脚本没有网络上传功能。识图和分析是否经过在线服务，取决于所使用的 agent 与运行环境；公开技能不等于对整个处理环境作出离线承诺。

[返回 Public Skills 技能目录](https://github.com/pelucoola/publicskills)
