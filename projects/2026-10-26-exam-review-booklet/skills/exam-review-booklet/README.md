# 错题讲评册 / exam-review-booklet

分享包版本：1.0.0
打包日期：2026年10月25日

把卷子照片整理成带原作答截图、错因、逐步思路与标准答案的可打印讲评册。每批新卷先确认或自填标题、考试/作业日期；每页显示身份信息，生成时间另列。输出 A4 横向 PDF 与自包含 HTML。

## 安装给其他 agent

将这个 ZIP 提供给支持 Agent Skills 的 agent，并发送：

> 请检查并安装 ZIP 中的 exam-review-booklet 技能到你的个人技能目录。保留整个目录结构，检查 Python、ReportLab、Pillow 和中文字体依赖。不要覆盖已有的同名技能。

支持识图、读取附件和执行 Python 的 agent 才能完成整套流程。仅聊天但不能执行代码的环境可以阅读讲评步骤，需要额外执行环境来生成 PDF。

手动安装时，把解压后的 exam-review-booklet 整个文件夹放到目标客户端识别的 skills 目录。Codex 当前官方文档列出的个人目录为 ~/.agents/skills/；其他客户端按其实际技能目录安装。不同版本或已有配置可能使用其他位置，由安装 agent 核对。

安装后在 Codex 中使用：

> 用 $exam-review-booklet 处理我上传的卷子，先确认标题和考试日期，再生成可打印讲评册。

其他 agent 按其技能调用方式使用。具备互动提问工具时先显示确认卡；不具备时在聊天中询问。未确认的日期不会默认为拍照日期或今天。

## 运行环境

- Python 3.10 或更高版本。
- ReportLab、Pillow。requirements.txt 固定为本包已验证的版本；可在适合的虚拟环境安装。
- 可嵌入的中文 TrueType 字体。脚本会发现部分常见字体；也可用 --font 指定已有的 .ttf/.ttc。
- 字体文件不包含在分享包中。
- FontTools 为可选项，可缩小 HTML 嵌入字体的体积；没有它仍可生成自包含网页。
- PDF 目视验收可使用 Poppler；依照所在环境已有工具执行。

本包中的渲染器只负责排版。识题、判断错题、证明核验及教学讲解由使用技能的 agent 完成。

在合适的 Python 环境安装依赖：

    python -m pip install -r requirements.txt

按 references/schema.md 准备已经确认标题和日期的 booklet.json，然后运行：

    python scripts/render_booklet.py /task/booklet.json --output-dir /task/output

原图路径相对 JSON 所在目录解析。标题与日期的确认字段均须为 true。运行依赖与文件权限由目标环境处理。

## 分享到 GitHub

把整个技能目录放到仓库中的独立目录，保留相对路径。将该目录的 GitHub 链接交给另一 agent，让它使用技能安装器安装该目录即可。

仓库公开前，由发布者确定版权/许可证以及公开范围。本包不包含本次家庭照片、姓名、成绩、生成的学生讲评册、密钥、字体、缓存或 node_modules。

## 官方市场

本 ZIP 是直接安装的技能分享包。OpenAI 官方目录以插件包分发技能；上架时按插件包规范封装，再完成发布者身份、检查、审核和发布步骤。不要把本 ZIP 的存在视为已经通过市场审核。

- 技能分发：https://learn.chatgpt.com/docs/build-skills
- 插件打包：https://developers.openai.com/plugins/build/plugins
- 提交与发布：https://developers.openai.com/plugins/deploy/submission

若采用需要桌面本地执行的发布方式，按官方 desktop-only 指引声明执行要求。其他市场按各自的打包与审核规则适配。
