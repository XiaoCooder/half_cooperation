# TASK-004 Review B - round-001

结论：需要小修改后再合并，当前不批准合并。

锚点信息：

- round: 1
- round_id: round-001
- work_branch: issue-1-personal-homepage-20260518
- head_commit: 4aa572157323e2beb0288fcd3ff82b1b5f3ab852
- approve_merge: false

## Findings

### Medium: 社交链接没有按需求实现为图标

位置：`index.html:31-40`

需求明确要求“社交链接图标（GitHub、知乎、邮箱等）”。当前实现只是文字胶囊按钮，没有使用图标字体、SVG 或其他图标元素。视觉表达和任务要求都不一致，属于需要修改的问题。

### Low: 文章和项目卡片使用 `#` 占位链接

位置：`index.html:54,61,68,75,87,92`

近期动态标题和精选项目卡片都用了 `href="#"`。这会让内容看起来可点击，但实际只会回到页首；对这个单页主页来说，要么提供真实外链，要么改成非链接展示，避免误导用户。

## Checks

- `node --check /home/usr/blog-test/script.js`
- `python3 -c "from pathlib import Path; s=Path('/home/usr/blog-test/index.html').read_text(); print({'articles': s.count('<article class=\"article-item\">'), 'projects': s.count('<a class=\"project-card\"'), 'social_links': s.count('<nav class=\"social-links\"')})"`

## Recommendation

先把社交区改成真正的图标链接，再处理掉 `#` 占位入口，然后重新评审。
