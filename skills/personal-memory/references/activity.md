# 记忆使用状态

使用状态需要 Python 3.8 或更新版本，以及对已绑定私有 Git 仓库的访问权限。查询需要读取权限，登记与同步需要写入权限。统计放在同一仓库的 `personal-memory-activity` 分支。脚本用独立的 Git 暂存区写入活动分支，记忆正文和当前工作区由原有 Git 流程管理。

## 开启与查询

- 配置当前 Agent 时询问是否开启统计，复用用户已给出的选择。开启时运行 `enable --agent`，登记本机和该 Agent。选择关闭时用 `disable --agent` 保存该选择。两条命令只设置当前 Agent 的 `personal-memory.<agent>.activity`。
- `--agent` 填该客户端的稳定名称，例如 `codex` 或 `openclaw`。同一客户端的不同常驻配置可用不同名称，例如 `codex-work`。使用小写英文字母、数字和连字符。每个会话复用所属 Agent 名称。使用默认本地记忆目录时可省略 `--repo`。
- 用户问「现在多少终端在用」「最后什么时候拉取或更新」时运行 `status`。报告最近 24 小时的活跃终端和 Agent 数、累计登记数，以及每个终端和 Agent 的最后成功时间。按用户指定窗口查询时传入 `--hours`。

```bash
python3 scripts/activity.py --repo "$memory_dir" enable --agent codex
python3 scripts/activity.py --repo "$memory_dir" status --hours 24
```

## 计数和时间

- **终端**按独立的本地 Git 克隆计数。每份克隆有一个保存在本地 Git 元数据中的随机 ID，换会话复用它。共享一份克隆的多个 Agent 算一个终端，同一台电脑的不同克隆各算一个终端。
- **Agent**按终端和稳定 Agent 名称的组合计数。活跃表示在选定窗口内登记、成功拉取或提交了记忆更新。显示终端时可用随机 ID 的前八位。缺少的时间显示为「尚无记录」。
- **最后拉取**记成功拉取并快进到远端记忆分支的时间。远端检查成功且本机已是最新也计入。**最后更新**记 Markdown 有实际变化并成功产生本地提交的时间。时间以 UTC 保存，展示时按用户时区转换并标明。
- 远端活动记录只包含随机终端 ID、Agent 名称和活动时间。启用前的操作从当前开始登记，不补造历史时间。

## 记录与关闭

只有在对应操作成功后才调用 `record`。一次任务实际完成了拉取和更新时，各记一次。脚本检查该 Agent 的统计设置。旧版在此克隆开启统计且该 Agent 已有本机活动记录时，沿用其旧版选择。新 Agent 通过首次配置选择是否登记。失败的拉取、本地纯查阅、活动状态查询和没有产生新提交的记忆编辑均无需登记。

```bash
python3 scripts/activity.py --repo "$memory_dir" record --agent codex --event pull
python3 scripts/activity.py --repo "$memory_dir" record --agent codex --event update
python3 scripts/activity.py --repo "$memory_dir" disable --agent codex
```

活动同步失败时，脚本保留该 Agent 最新的本机时间，下一次记录该 Agent 的活动时会重试。记忆操作和活动记录分别报告结果。查询远端失败时说明暂时读不到统计。`disable` 停止所选 Agent 的后续登记，已同步的记录会随时间退出活跃窗口。
