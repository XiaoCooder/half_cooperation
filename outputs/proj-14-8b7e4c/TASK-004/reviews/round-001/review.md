# TASK-004 Review B - Round 001

- Round: 1
- Round ID: round-001
- Work branch: issue-1-personal-homepage-20260518
- Head commit: d6cc78cbad7167376e4d54d3a35ca88818380ae3
- Conclusion: 需要小修改后再合并
- approve_merge: false

## Summary

本轮实现以纯静态页面完成了个人信息、近期动态、精选项目、页脚、响应式布局和悬停微交互，整体方向符合 issue。现有 `unittest` 和 `git diff --check` 均通过。

但 issue 明确要求社交链接图标，目前页面只提供纯文字链接，因此当前不建议直接合并。

## Findings

### Medium - 社交链接没有按需求实现为图标链接

位置：`index.html:35`

Issue 要求“社交链接图标（GitHub、知乎、邮箱等）”。当前 `nav.social-links` 内的三个入口只渲染纯文字 `GitHub`、`知乎`、`邮箱`，没有 SVG、图标字体、内联图形或其他图标元素；这与视觉/交互需求不完全匹配。

建议为每个社交入口补充可访问的图标标识，并保留清晰的 `aria-label` 或可见文本。

### Low - 测试没有覆盖社交图标这一明确需求

位置：`tests/test_static_homepage.py:37`

现有测试只校验链接 `href` 中包含 `github`、`zhihu` 和 `mailto`，不能区分文字链接与图标链接。建议在补充图标后增加结构断言，例如检查每个社交链接包含 SVG、图标类名或明确的图标元素。

## Checks

- `git pull` in `/home/usr/blog-test`: passed, already up to date.
- `git pull` in `/home/usr/half_cooperation`: passed, already up to date.
- `python3 -m unittest discover -s tests` in `/home/usr/blog-test`: passed, 4 tests OK.
- `git diff --check main...d6cc78cbad7167376e4d54d3a35ca88818380ae3` in `/home/usr/blog-test`: passed, no whitespace errors.

## Recommendation

补齐 GitHub、知乎、邮箱的图标化社交入口，并为该结构增加测试断言后进入下一轮评审。
