# 个人长期记忆

`personal-memory` 1.5.0 用私有 Git 仓库保存 Markdown。个人记忆可选择自动管理，项目记忆按明确请求查阅、更新和同步。

## 安装

下载 [v1.5.0 安装包](https://github.com/pelucoola/publicskills/blob/main/dist/personal-memory/personal-memory-1.5.0.zip)，或从 [GitHub 技能目录](https://github.com/pelucoola/publicskills/tree/main/skills/personal-memory) 安装。发布包提供 [SHA-256 校验文件](https://github.com/pelucoola/publicskills/blob/main/dist/personal-memory/personal-memory-1.5.0.zip.sha256)。

**Codex 用户级安装**使用 `~/.agents/skills/personal-memory`。将完整的 Skill 目录放到这里。若从 `~/.codex/skills/personal-memory` 迁移，核对新位置的版本后将旧副本移出技能扫描目录，使 Codex 发现一份同名 Skill。 [Codex 技能目录说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

使用 Codex 的安装器时，可在同一个请求里指定安装目录并继续首次配置。

```text
用 $skill-installer 从 https://github.com/pelucoola/publicskills/tree/main/skills/personal-memory 安装 personal-memory，目标父目录为 ~/.agents/skills。安装完成后读取 SKILL.md，带我配置当前 Codex。
```

其他 Agent 可按自己的技能目录手动安装。通过共享目录发现 Skill 的 Agent，也会在首次调用时检查自己的配置。安装完成后可以说：

```text
用 $personal-memory 检查当前 Agent 的配置，带我完成缺少的设置。
```

使用环境需要 Git、记忆目录的读写权限，以及私有 Git 仓库的访问权限。使用状态功能还需要 Python 3.8 或更新版本。远程服务可以用 GitHub 私有仓库或你自己的 Git 服务。

## 首次交互配置

**场景 A：新电脑。** 先绑定私有 Git 仓库，再设置当前 Agent 的个人自动管理范围、推送方式和统计选择。

**场景 B：电脑已绑定仓库，新装了一个 Agent。** 复用本机仓库，从当前 Agent 自己的配置开始。首次可选择自动管理范围、推送方式，并登记自己的常驻指令和活动统计。已选择按需调用时，后续沿用该选择。

支持弹框的客户端可用交互提问，其余客户端逐项在聊天中询问。默认本地目录为 `~/.local/share/personal-memory`，分支沿用远程默认分支。个人自动管理可以仅在当前 Agent 的指定项目生效。 [当前 Agent 配置](references/standing-instructions.md)

## 日常使用

| 你可以说 | Skill 会做什么 |
| --- | --- |
| 拉取我的最新长期记忆 | 获取远程分支的更新，保留本地已有改动 |
| 把这条偏好加入长期记忆 | 更新相关 Markdown，并在本机记录一次 Git 提交 |
| 把这条决定记到「项目名」的项目记忆，并同步 | 更新该项目的记录，核对改动后提交并推送 |
| 在长期记忆里找出上次为什么做这个决定 | 查阅项目记录，必要时查看 Git 历史 |
| 查看最近有哪些终端或 Agent 在用记忆 | 统计活跃和累计登记数量，并查看最后成功拉取和更新时间 |

想加入统计，可说「为当前 Agent 开启使用记录」。多台电脑绑定同一个私有仓库后，可以在任意一台查询。活跃默认指最近 24 小时有记录的操作，终端按本地 Git 克隆区分。 [统计口径和用法](references/activity.md)

## 记忆怎么放

- `personal/` 存个人资料和你明确指定的长期偏好，可以选择自动管理。
- `projects/<project-id>/` 存指定项目的决定、进展和规范。查阅、更新和推送均由你明确发起。
- 根目录 `README.md` 是索引。临时要求和草稿留在当前任务。旧版条目在对应记录需要更新或整理时按归属处理。 [目录与旧记录规则](references/memory-layout.md)

换电脑时可绑定同一个私有仓库，各 Agent 的使用设置单独完成。
