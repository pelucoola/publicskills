# 当前 Agent 配置

## 检查当前 Agent 的状态

为当前 Agent 使用稳定的小写标识，例如 `codex` 或 `claude-code`。同一客户端的不同配置可分别使用 `codex-work` 等标识。共享仓库的本地配置以 `personal-memory.<agent>.` 为前缀；只读取和修改当前标识的设置。

1. 用 `git -C "$memory_dir" config --local --get "personal-memory.$agent.scope"` 检查已有选择。`manual` 表示用户已选择按需调用。`global` 或 `project` 时，检查保存的 `instruction-file` 和其中的记忆区块，确认它仍适用于当前 Agent。项目范围在其他任务中保持已配置状态，按实际作用范围使用。
2. 没有状态时，检查当前 Agent 自己正在使用的指令入口。已有可辨认的旧版 `personal-memory` 区块时沿用已明确的范围和同步方式。该区块约定按 Skill 规则管理，自动管理范围按本版的个人记忆规则解释。缺少当前 Agent 的有效配置时，执行 [场景 B](../SKILL.md#场景-b本机已绑定仓库当前-agent-初次使用)。
3. 完成设置后，在记忆仓库用 `git config --local` 保存当前 Agent 的 `scope`（`manual`、`global`、`project`）与 `push`（`local`、`auto`），自动模式再保存实际 `instruction-file` 和项目根目录 `project-root`（仅项目范围）。例如：

   ```bash
   git -C "$memory_dir" config --local "personal-memory.$agent.push" local
   git -C "$memory_dir" config --local "personal-memory.$agent.scope" manual
   ```

   `manual` 的推送由当次请求决定，状态记录可避免重复引导。统计选择按 [使用状态](activity.md) 单独处理。仅在用户要求更改或有效配置缺失时再次引导。

## 选择指令文件

- **Codex 全局**使用 `$CODEX_HOME/AGENTS.md`，未设置 `CODEX_HOME` 时使用 `~/.codex/AGENTS.md`。同级有正在生效的 `AGENTS.override.md` 时，更新该文件。
- **其它 Agent**使用当前客户端独有的指令入口。例如 Claude Code 使用其当前配置的 `CLAUDE.md`。宿主没有可编辑入口时，给出区块供用户加入设置，等生效后再将该模式登记为已配置。
- **指定项目范围**优先使用当前客户端独有的项目指令入口。项目指令文件同时被多个 Agent 读取时，在当前客户端自己的指令文件中添加适用条件，写明用户指定的项目根目录。普通项目工作仍遵循项目自身指令。

## 写入与维护

保留当前指令文件的其它内容。新启用时追加下方区块，重复配置时更新标记之间的内容。切换到按需调用时，只移除当前 Agent 的记忆区块，并保存按需状态。发现不完整或重复标记时，先核实要修改的范围。写完复核文件并告知路径。更改在宿主重新载入指令后生效。

```markdown
<!-- personal-memory:start -->
## 个人长期记忆

当前 Agent 标识为 `<agent>`。当任务确实需要个人资料或长期个人偏好时，按 personal-memory 的规则拉取并读取相关个人记录。任务结束时，仅按 Skill 的个人记忆规则维护已确认的个人条目。项目记忆由用户明确发起读取、记录或同步。

个人记忆自动更新后提交到本地。推送由当次同步请求授权。
<!-- personal-memory:end -->
```

替换 `<agent>` 为当前标识。指定项目范围时，在区块中注明「本规则仅在指定项目根目录生效」，并填入实际路径。用户开启自动同步时使用以下推送规则。

> 自动推送仅适用于按 Skill 核对过的个人记忆提交，目标为已绑定的私有分支。项目记忆的推送由当次请求授权。

仓库地址、分支和认证沿用本机绑定。使用自定义记忆目录时，在客户端启动环境里设置 `PERSONAL_MEMORY_DIR`。各 Agent 的常驻文件和配置状态独立。Codex 的指令文件发现规则见 [AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。
