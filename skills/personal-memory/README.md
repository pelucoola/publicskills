# 个人长期记忆

`personal-memory` 1.1.0 用 Git 管理长期偏好、项目记录和重要决定。资料使用普通 Markdown。绑定同一个私有仓库后，可在不同电脑或 Agent 上继续读取和更新。

## 安装

把 [技能目录](https://github.com/pelucoola/publicskills/tree/main/skills/personal-memory) 或 [ZIP 安装包](https://github.com/pelucoola/publicskills/blob/main/dist/personal-memory/personal-memory-1.1.0.zip) 交给支持 Agent Skills 的客户端。安装包提供 [SHA-256 校验文件](https://github.com/pelucoola/publicskills/blob/main/dist/personal-memory/personal-memory-1.1.0.zip.sha256)。可以把安装、绑定和开启自动管理写在同一条请求中。

```text
用 $skill-installer 从 https://github.com/pelucoola/publicskills/tree/main/skills/personal-memory 安装 personal-memory。安装后读取刚安装的 SKILL.md，绑定我的私有 Git 仓库 <私有 Git 地址>，并在本机全局指令中开启自动记忆管理。默认只创建本地提交。
```

使用环境需要 Git、记忆目录的读写权限，以及私有 Git 仓库的访问权限。远程服务可以用 GitHub 私有仓库或你自己的 Git 服务。

也可以只在当前项目开启。要让 Agent 在自动更新后推送，把「默认只创建本地提交」改成「允许自动同步到这个私有仓库」。已安装旧版的用户可以更新 Skill 后用现有仓库绑定开启自动管理。 [常驻指令配置](references/standing-instructions.md)

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

## 自动管理规则

- **何时读**。接续已有项目、需要长期偏好或引用先前决定时，拉取并查阅相关记录。
- **何时写**。任务结束时，只有出现有后续用途的已确认偏好、决定、进展或下一步才更新。纠正旧信息时修订原条目，Git 保存历史。
- **何时同步**。默认自动更新只形成一个本地提交。用户可按次要求推送，也可以在常驻指令里一次开启自动同步。

换电脑或换 Agent 时，绑定同一个私有仓库，并在需要的宿主重新启用常驻指令。
