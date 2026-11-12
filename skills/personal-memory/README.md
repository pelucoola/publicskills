# 个人长期记忆

`personal-memory` 1.0.0 用 Git 管理你亲自选择保存的长期偏好、项目记录和重要决定。资料使用普通 Markdown。新电脑克隆同一个私有仓库后，就能继续读取和更新。

## 安装

把 [技能目录](https://github.com/pelucoola/publicskills/tree/main/skills/personal-memory) 或 [ZIP 安装包](https://github.com/pelucoola/publicskills/blob/main/dist/personal-memory/personal-memory-1.0.0.zip) 交给支持 Agent Skills 的客户端。安装包提供 [SHA-256 校验文件](https://github.com/pelucoola/publicskills/blob/main/dist/personal-memory/personal-memory-1.0.0.zip.sha256)。Codex 可以用以下指令安装：

```text
用 $skill-installer 从 https://github.com/pelucoola/publicskills/tree/main/skills/personal-memory 安装 personal-memory。
```

使用环境需要 Git、记忆目录的读写权限，以及私有 Git 仓库的访问权限。远程服务可以用 GitHub 私有仓库或你自己的 Git 服务。

## 配置你的记忆仓库

先准备一个独立的私有 Git 仓库。安装 Skill 后，把**这个私有仓库的 Git 地址**交给 Agent。例如：

```text
用 $personal-memory 配置长期记忆。远程仓库是 git@example.com:your-account/personal-memory.git。
```

分支默认沿用远程默认分支，新建空仓库默认使用 `main`。默认本地目录为 `~/.local/share/personal-memory`。也可以指定其它分支和本地目录。Git 在本机记忆目录保存绑定，换设备时再次绑定同一个私有仓库。

## 日常使用

| 你可以说 | Skill 会做什么 |
| --- | --- |
| 拉取我的最新长期记忆 | 获取远程分支的更新，保留本地已有改动 |
| 把这条偏好加入长期记忆 | 更新相关 Markdown，并在本机记录一次 Git 提交 |
| 更新这个项目的进度并同步到记忆仓库 | 先拉取，更新记录，核对改动后提交并推送 |
| 在长期记忆里找出上次为什么做这个决定 | 查阅项目记录，必要时查看 Git 历史 |

在新的 Agent 里，先让它读取记忆仓库的 `README.md`，再继续任务。公开的 Skill 目录提供通用工作流程，实际记忆保存在你自己配置的仓库中。
