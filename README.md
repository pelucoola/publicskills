# Public Skills

可以交给 agent 安装使用的公开技能集合。这里按技能名称组织目录，每个技能都有独立的用途介绍、安装方法、使用说明和所需资源。

从下方选择技能，进入它的 README 了解详情，再把技能目录链接或 ZIP 安装包交给你的 agent。

## 技能一览

| 技能 | 技能名称 | 可以帮你做什么 | 使用条件 | 版本 |
| --- | --- | --- | --- | --- |
| [错题讲评册](skills/exam-review-booklet/README.md) | `exam-review-booklet` | 把已作答的试卷、作业照片整理成可打印讲评册，保留原作答，分析错因，补齐思路与参考答案 | 识图、文件访问、Python、中文字体 | 1.0.2 |

## 快速安装

### 通过技能目录安装

把对应技能的 GitHub 目录链接交给支持 Agent Skills 的 agent。以错题讲评册为例，在支持技能安装器的 Codex 中发送：

```text
用 $skill-installer 从以下目录安装 exam-review-booklet：
https://github.com/pelucoola/publicskills/tree/main/skills/exam-review-booklet
保留完整技能目录，并检查它的运行依赖。
```

### 通过 ZIP 安装

下载 [错题讲评册 1.0.2 安装包](dist/exam-review-booklet/exam-review-booklet-1.0.2.zip)，交给你的 agent，并让它安装其中完整的 `exam-review-booklet` 文件夹。其他技能的下载入口会列在各自 README 中。

技能的实际安装位置、调用方式和依赖安装方式，由目标客户端确定。不同 agent 的能力有差异，安装前请查看对应技能的运行条件。

## 仓库结构

```text
publicskills/
├── README.md                         # 所有公开技能的展示与安装入口
├── skills/                           # 技能源码：一个技能一个目录
│   └── exam-review-booklet/
│       ├── README.md                 # 给使用者看的用途、安装与使用说明
│       ├── SKILL.md                  # 给 agent 读取的技能入口
│       ├── requirements.txt          # Python 依赖
│       ├── agents/                   # 客户端展示信息
│       ├── scripts/                  # 排版脚本
│       ├── references/               # 工作流程与数据协议
│       └── assets/                   # 排版样式
└── dist/                             # 可下载的安装包，按技能名称归档
    └── exam-review-booklet/
        ├── exam-review-booklet-1.0.2.zip
        └── exam-review-booklet-1.0.2.zip.sha256
```

## 后续技能如何放置

1. 技能源码统一放在 `skills/<skill-name>/`，使用简短的小写英文名称，单词用连字符连接；目录名与 `SKILL.md` 中的 `name` 一致，不在目录名中加入日期。
2. 每个技能的 `README.md` 说明用途、适用场景、输入与输出、安装、调用方法及运行条件；`SKILL.md` 保存 agent 执行任务所需的指引。
3. 脚本、参考资料和样式等资源放在技能目录内部，保留相对路径。按需添加资源，避免依赖作者电脑上的固定路径。
4. ZIP 安装包放在 `dist/<skill-name>/`，文件名使用 `<skill-name>-<version>.zip`，同时提供 SHA-256 校验文件。解压后应得到一个完整的技能文件夹。
5. 新增或更新技能时，同步修改本页的技能表、对应 README、版本和安装包。当前发布目录只保留经过脱敏检查的安装包；发现带有原任务信息的旧包时撤下，源码历史通过 Git 提交回看。

## 数据与授权

仓库只保存可复用技能和通用说明，不放入使用者的试卷、照片、姓名、成绩、实际作答或凭据。使用技能生成的个人材料保存在各自任务目录。

授权范围以项目明确提供的许可证为准；未附带许可证的内容尚未授予额外开源许可。
