# Public Skills

可供支持 Agent Skills 的 agent 安装使用的技能。每个项目提供完整技能目录、使用说明和 ZIP 安装包。

## 错题讲评册 / exam-review-booklet

把试卷、作业照片整理为可打印的 A4 讲评册，包含原作答、错因、逐步思路、完整参考答案和关键指导。每份新卷先互动确认标题及考试/作业日期。

- 版本：1.0.0
- 源任务与分享包制作日期：2026-10-25；GitHub 发布日期：2026-10-26。
- [完整说明与运行方法](projects/2026-10-26-exam-review-booklet/README.md)
- [技能目录](projects/2026-10-26-exam-review-booklet/skills/exam-review-booklet)
- [ZIP 安装包](projects/2026-10-26-exam-review-booklet/dist/exam-review-booklet-1.0.0.zip)

在支持技能安装器的 Codex 中发送：

```text
用 $skill-installer 从以下 GitHub 目录安装 exam-review-booklet：
https://github.com/pelucoola/publicskills/tree/main/projects/2026-10-26-exam-review-booklet/skills/exam-review-booklet
保留整个技能目录，并检查 Python 和中文字体依赖。
```

其他支持 Agent Skills 的 agent 也可以安装完整技能文件夹，或使用 ZIP 包安装。完整流程需要识图、文件访问和 Python 执行能力。

安装后上传试卷照片，并发送：

```text
用 $exam-review-booklet 生成错题讲评册，先让我确认标题和考试/作业日期。
```

技能运行依赖 Python 3.10 或更高版本、ReportLab、Pillow，以及可嵌入的中文字体；详见项目说明。生成后打开 PDF 或 HTML 预览，打印使用 A4、横向、实际大小。

本仓库提供技能与通用说明，不包含学生试卷、照片、姓名、成绩或实际作答。授权范围以各项目附带的许可证为准；没有附带许可证的项目尚未授予额外开源许可。
