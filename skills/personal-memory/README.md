# 个人长期记忆

`personal-memory` 1.3.0 用 Git 管理长期偏好、项目记录和重要决定。资料使用普通 Markdown。绑定同一个私有仓库后，可在不同电脑或 Agent 上继续读取和更新。

## 安装

把 [技能目录](https://github.com/pelucoola/publicskills/tree/main/skills/personal-memory) 或 [ZIP 安装包](https://github.com/pelucoola/publicskills/blob/main/dist/personal-memory/personal-memory-1.3.0.zip) 交给支持 Agent Skills 的客户端。安装包提供 [SHA-256 校验文件](https://github.com/pelucoola/publicskills/blob/main/dist/personal-memory/personal-memory-1.3.0.zip.sha256)。想在同一次对话里安装并配置，可以使用这条请求。

```text
用 $skill-installer 从 https://github.com/pelucoola/publicskills/tree/main/skills/personal-memory 安装 personal-memory。安装后读取刚安装的 SKILL.md，带我完成首次交互配置。
```

使用环境需要 Git、记忆目录的读写权限，以及私有 Git 仓库的访问权限。使用状态功能还需要 Python 3.8 或更新版本。远程服务可以用 GitHub 私有仓库或你自己的 Git 服务。

## 首次交互配置

安装完成后，首次调用 `$personal-memory` 时，Agent 会检查本机绑定。首次绑定会引导你输入私有 Git 仓库地址，再选择自动管理范围和推送方式。有交互提问工具的客户端可以弹框收集输入，其余客户端可以在聊天中逐项询问。已有绑定和设置可直接使用。

分支默认沿用远程默认分支，新建空仓库默认使用 `main`。默认本地目录为 `~/.local/share/personal-memory`。也可以指定其它分支和本地目录。启用自动管理时，可以选择在本机全局生效、仅在指定项目生效，以及是否自动推送。 [常驻指令配置](references/standing-instructions.md)

## 日常使用

| 你可以说 | Skill 会做什么 |
| --- | --- |
| 拉取我的最新长期记忆 | 获取远程分支的更新，保留本地已有改动 |
| 把这条偏好加入长期记忆 | 更新相关 Markdown，并在本机记录一次 Git 提交 |
| 更新这个项目的进度并同步到记忆仓库 | 先拉取，更新记录，核对改动后提交并推送 |
| 在长期记忆里找出上次为什么做这个决定 | 查阅项目记录，必要时查看 Git 历史 |
| 查看最近有哪些终端或 Agent 在用记忆 | 统计活跃和累计登记数量，并查看最后成功拉取和更新时间 |

想加入统计，可在每份记忆仓库克隆上说「开启终端和 Agent 使用记录」。多台电脑绑定同一个私有仓库后，可以在任意一台查询。活跃默认指最近 24 小时有记录的操作，终端按本地 Git 克隆区分。 [统计口径和用法](references/activity.md)

## 自动管理规则

- **何时读**。接续已有项目、需要长期偏好或引用先前决定时，拉取并查阅相关记录。
- **何时写**。任务结束时，只有出现有后续用途的已确认偏好、决定、进展或下一步才更新。纠正旧信息时修订原条目，Git 保存历史。
- **何时同步**。默认自动更新只形成一个本地提交。用户可按次要求推送，也可以在常驻指令里一次开启自动同步。

换电脑或换 Agent 时，绑定同一个私有仓库，并在需要的宿主重新启用常驻指令。
