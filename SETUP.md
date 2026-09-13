# Setup

这个目录可以直接作为 `changluya/changluya` GitHub Profile 仓库。

## 使用

将本目录内容覆盖到现有 `changluya` 仓库后：

```bash
git add .
git commit -m "feat: update profile projects"
git push
```

## 自动更新

`.github/workflows/update-profile.yml` 每 12 小时刷新一次精选项目的 Star 数，并保持 Open Source 区域的分类与排序。

也可以在 GitHub：

`Actions -> Update profile -> Run workflow`

手动触发。

## 首页结构

当前首页保持简洁，主要包含：

1. 一句话定位
2. 核心技术栈
3. 分类后的精选开源项目
4. 当前技术关注方向

Open Source 当前分为三类：

- **Agent Framework & Infrastructure**：AgentForge、OpenReach
- **AI Engineering & Skills**：ai-practice-guide、open-office-skill
- **Applications & Platforms**：Studio-Vue、BlogLoom

其中 AgentForge 作为核心 Agent Framework 项目优先展示；BlogLoom 作为博客内容管理与发布平台放在应用类项目中。
