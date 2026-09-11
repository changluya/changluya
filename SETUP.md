# Setup

这个目录可以直接作为 `changluya/changluya` GitHub Profile 仓库。

## 使用

将本目录内容覆盖到现有 `changluya` 仓库后：

```bash
git add .
git commit -m "refactor: simplify profile"
git push
```

## 自动更新

`.github/workflows/update-profile.yml` 每 12 小时刷新一次四个精选项目的 Star 数。

也可以在 GitHub：

`Actions -> Update profile -> Run workflow`

手动触发。

## 首页结构

只保留四层：

1. 一句话定位
2. 核心技术栈
3. 四个精选开源项目
4. 当前技术关注方向

完整技术栈默认折叠，避免首页过长。
