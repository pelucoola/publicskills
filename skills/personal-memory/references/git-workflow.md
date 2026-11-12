# Git 工作流程

示例使用常见 shell 语法。`memory_dir` 是本机记忆目录，`remote_url` 是用户提供的私有仓库地址，`branch` 是用户选定或远程默认分支。按参数安全传递真实值。使用 Git 已有的 SSH 或凭据管理器完成身份验证。

## 首次绑定与换电脑

1. 取得用户指定的私有远程仓库地址和可选的分支、本机目录。用户未提供地址时可以继续整理本地草稿，等取得地址再绑定。普通 HTTPS 或 SSH 地址可以写入 Git 配置，凭据由 Git 管理。用 Git 服务界面或用户确认核实仓库可见性。
2. 目录不存在或为空时，克隆用户指定的仓库。默认执行 `git clone -- "$remote_url" "$memory_dir"`。指定已有分支时用 `git clone --branch "$branch" -- "$remote_url" "$memory_dir"`。目录已有仓库时，先验证其根目录、`origin` 的拉取及推送地址、当前分支与用户指定值相符，再复用。目标已有其它资料时保留原目录并另选位置。
3. 远程已有提交时，沿用选定分支的跟踪关系。远程默认分支无法检出时，列出已有分支并让用户选择。若远程没有任何引用，先克隆空仓库，再给尚未创建的本地分支选择名称，未指定时用 `main`。用 `git check-ref-format --branch "$branch"` 检查分支名，仅在确认本地 `HEAD` 尚无提交时使用 `git -C "$memory_dir" symbolic-ref HEAD "refs/heads/$branch"`。第一次写入时创建记忆索引 `README.md`，第一次推送由用户的同步请求触发。
4. 将验证后的仓库绑定到本机工作目录。`verified_url` 为用户已确认的有效 `origin` 地址，拉取和推送地址均需指向该私有仓库。Git 会把绑定和 `origin` 保存在该目录的 `.git/config`。

   ```bash
   git -C "$memory_dir" config --local personal-memory.remote "$verified_url"
   git -C "$memory_dir" config --local personal-memory.branch "$branch"
   ```

   自定义本机路径时，在 Agent 运行环境中设置 `PERSONAL_MEMORY_DIR`，或在调用时提供路径。新电脑安装 Skill 后，用同一私有远程仓库和分支执行上述绑定流程。

## 日常拉取与提交

1. 每次更新前检查工作区、当前分支、已有提交和 `origin`。用 `git remote get-url --all origin`、`git remote get-url --push --all origin` 核对有效地址；出现多个推送地址、绑定不符或分支不符时，先解决配置差异。以下命令均以记忆仓库为工作目录。已有合并冲突、暂存或工作区改动时先查看其范围，保留用户的改动。
2. 对已有远程分支执行 `git fetch --prune origin`，再 `git merge --ff-only "refs/remotes/origin/$branch"`。本地和远程均有独立提交时转到下一节。若分支消失，核对绑定和远程状态。首次推送仅用于已确认的初始化场景。网络或认证失败时报告当前副本状态。
3. 修改实际需要维护的 Markdown。用 `git diff` 检查改动，并阅读本次新增的未跟踪文件。已有同文件的未提交内容时先确认提交范围；已有其它暂存项时，保留其状态并使用仅提交指定文件的方式，或暂存本次更新供用户核对。使用具体路径，检查提交内容后再完成本地提交。
4. 用户已授权同步时，核对远程分支与 `HEAD` 之间的所有待推送提交，检查其中的文件和内容，包括后来撤销的内容。项目提交仅在当次明确授权的范围内推送。自动同步个人记忆时，如果待推送历史包含未经当次授权的项目或其它改动，保留本地提交，说明待同步的范围。已有分支使用 `git push origin "HEAD:refs/heads/$branch"`。首次推送使用 `git push --set-upstream origin "HEAD:refs/heads/$branch"`。同步完成后报告目标分支和提交哈希。仅授权本地记录时，说明已有本地版本可供之后同步。

## 并发更新与恢复

- 若推送被远端的新提交拒绝，先重新获取远端并查看双方差异。可在本次授权范围内用普通合并保留双方历史。若同一条记忆有互相冲突的事实，保留现有改动并向用户核对正确版本，再继续合并和同步。使用普通快进推送；强推、丢弃本地改动和重写历史需由用户另行明确授权。
- 回看旧记录可用 `git log -- <路径>` 和 `git show <提交>:<路径>`。需要恢复某项内容时，把旧内容作为新的 Markdown 修改提交，保留后续记录。确认回滚范围后再同步。
