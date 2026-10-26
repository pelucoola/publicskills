# 错题讲评册 / exam-review-booklet

把已作答的试卷、作业照片整理成可直接打印的讲评册：保留学生原作答截图，并排呈现具体错因、逐步思路、完整参考答案和关键指导。每份新试卷先互动确认标题与考试/作业日期，每页打印标题、日期与题号，另列生成时间。

- 版本：1.0.0
- 源任务及分享包制作日期：2026-10-25
- GitHub 发布日期：2026-10-26
- 输出：A4 横向 PDF、自包含打印 HTML，以及便于后续订正的排版数据。

## 让其他 agent 安装

技能目录：[skills/exam-review-booklet](skills/exam-review-booklet)

在支持技能安装器的 Codex 中发送：

```text
用 $skill-installer 从以下 GitHub 目录安装 exam-review-booklet：
https://github.com/pelucoola/publicskills/tree/main/projects/2026-10-26-exam-review-booklet/skills/exam-review-booklet
保留整个技能目录，并检查 Python 和中文字体依赖；如已有同名技能，先说明差异。
```

本仓库为公开仓库，可以直接分享上述技能目录链接。

也可下载 [ZIP 安装包](dist/exam-review-booklet-1.0.0.zip)，把它交给支持 Agent Skills 的 agent，要求安装其中完整的 `exam-review-booklet` 文件夹。Codex 个人技能目录通常为 `~/.agents/skills/`；由安装 agent 核对当前客户端实际使用的位置。其他客户端使用各自支持的技能目录。

## 使用与预览

安装后上传试卷照片，并发送：

```text
用 $exam-review-booklet 生成错题讲评册，先让我确认标题和考试/作业日期。
保留原作答，详细分析错因，给出不断步的思路和完整参考答案。
```

agent 有互动提问工具时显示确认选项，没有时通过普通对话确认。生成后直接打开 PDF 检查，或在浏览器中打开 HTML 预览。打印设置为 A4、横向、实际大小。

## 运行依赖

- agent 能识图、读取本地文件并运行 Python。
- Python 3.10 或更高版本，ReportLab 和 Pillow，版本见技能目录的 `requirements.txt`。
- 一款允许嵌入的中文 TrueType 字体；字体文件需由使用者自行提供，也可通过 `--font` 指定。
- FontTools 可选，用于缩小自包含 HTML 的字体体积。PDF 目视检查可使用 Poppler。

渲染脚本只负责排版；题目识别、独立求解、错因分析和答案核验由 agent 完成。没有教师答案时，讲评册会注明“标准答案（按题面整理）”。

需要手动运行排版时，在技能目录下执行：

```bash
python -m pip install -r requirements.txt
python scripts/render_booklet.py /path/to/booklet.json --output-dir /path/to/output
```

`booklet.json` 的格式见 [排版数据协议](skills/exam-review-booklet/references/schema.md)。图片路径相对数据文件所在目录解析。先确认标题和日期，再生成讲评册；生成后逐页目视检查公式、截图和分页。

## 包内容与边界

源码与 ZIP 安装包内容一致。包内仅有技能说明、交互与讲评规则、排版脚本和样式，未包含学生照片、姓名、成绩、实际作答、生成的学生讲评册、字体或凭据。

完整安装说明见 [技能包 README](skills/exam-review-booklet/README.md)，下载完整性可用 [SHA-256 校验文件](dist/exam-review-booklet-1.0.0.zip.sha256)核对。此版本通过技能结构、脚本语法、示例输入校验和 ZIP 完整性检查。

本目录没有附加开源许可证；公开再分发或用于其他市场前，由权利人确定授权范围。本次上传为 GitHub 分发，不代表市场上架或审核通过。
