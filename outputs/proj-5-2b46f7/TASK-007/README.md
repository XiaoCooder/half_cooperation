# Markdown 文件存储模块

任务码: TASK-007

## 功能概述

本模块实现文章内容的本地文件系统存储功能，支持 Markdown 格式文件的读写操作，并提供完善的路径安全验证，防止路径遍历攻击。

## 文件结构

```
TASK-007/
├── storage_config.py      # 存储配置
├── file_utils.py           # 文件工具函数（安全验证）
├── markdown_storage.py     # 核心存储功能
├── README.md               # 本文档
└── posts/                  # Markdown 文件存储目录
    └── content/            # 实际存放 .md 文件的目录
```

## 主要功能

### 1. 文章保存 - `save_post(slug, content, overwrite=False)`

```python
from markdown_storage import save_post

# 保存新文章
file_path = save_post("hello-world", "# Hello World\n这是我的第一篇博客")

# 覆盖已存在的文章
file_path = save_post("hello-world", "# Updated\n内容已更新", overwrite=True)
```

### 2. 文章读取 - `read_post(slug)`

```python
from markdown_storage import read_post

content = read_post("hello-world")
print(content)  # 输出 Markdown 内容
```

### 3. 文章删除 - `delete_post(slug)`

```python
from markdown_storage import delete_post

delete_post("hello-world")  # 删除文章
```

### 4. 检查文章存在 - `exists_post(slug)`

```python
from markdown_storage import exists_post

if exists_post("hello-world"):
    print("文章存在")
```

### 5. 列出所有文章 - `list_posts()`

```python
from markdown_storage import list_posts

posts = list_posts()
for post in posts:
    print(f"{post['slug']} - {post['size']} bytes")
```

### 6. 获取文章元数据 - `get_post_metadata(slug)`

```python
from markdown_storage import get_post_metadata

meta = get_post_metadata("hello-world")
print(meta)
# {'slug': 'hello-world', 'filename': 'hello-world.md', 'size': 1024, ...}
```

### 7. 存储统计 - `get_storage_stats()`

```python
from markdown_storage import get_storage_stats

stats = get_storage_stats()
print(f"文章数: {stats['posts_count']}")
print(f"总大小: {stats['total_size_readable']}")
```

## 安全特性

### 路径遍历防护

系统会拦截以下攻击：

- ❌ `../etc/passwd` - 父目录引用
- ❌ `/etc/passwd` - 绝对路径
- ❌ `hello/../world` - 路径分隔符绕过
- ❌ `hello\x00world` - null 字节注入

验证示例：

```python
from file_utils import validate_slug, FileSecurityError

try:
    validate_slug("normal-slug")  # ✅ 通过
    validate_slug("../etc/passwd")  # ❌ 抛出异常
except FileSecurityError as e:
    print(f"安全验证失败: {e}")
```

### Slug 规范化

- 转换为小写
- 空格替换为连字符
- 移除非安全字符
- 移除首尾连字符

```python
from file_utils import normalize_slug

normalize_slug("Hello World!")  # -> "hello-world"
normalize_slug("My__Post_Name")  # -> "my-post-name"
```

## 错误处理

| 异常类 | 说明 |
|--------|------|
| `FileSecurityError` | 文件安全验证失败 |
| `PostNotFoundError` | 文章不存在 |
| `PostExistsError` | 文章已存在 |
| `StorageFullError` | 存储空间不足 |
| `MarkdownStorageError` | 其他存储错误 |

```python
from markdown_storage import (
    save_post, read_post, delete_post,
    PostNotFoundError, PostExistsError,
    FileSecurityError, StorageFullError
)

try:
    content = read_post("my-post")
except PostNotFoundError:
    print("文章不存在")
except FileSecurityError:
    print("不安全的 slug")
```

## 配置项

在 `storage_config.py` 中可配置：

```python
STORAGE_ROOT = "posts"           # 存储根目录
POSTS_DIR = "posts/content"       # Markdown 文件目录
ALLOWED_EXTENSIONS = {".md"}      # 允许的扩展名
MAX_FILENAME_LENGTH = 200         # 文件名最大长度
MAX_FILE_SIZE = 10 * 1024 * 1024  # 单个文件最大 10MB
```

## 与数据库集成

数据库中 Post 表只存储元数据：

| 字段 | 说明 |
|------|------|
| id | 主键 |
| title | 标题 |
| slug | 唯一标识符 |
| summary | 摘要 |
| content | 存储在文件系统中 |

读取流程：
1. 根据 slug 从数据库获取文章元数据
2. 调用 `read_post(slug)` 读取文件内容
3. 合并返回完整文章数据

## 测试

```bash
# 测试基本功能
python -c "
from markdown_storage import (
    save_post, read_post, delete_post,
    exists_post, list_posts
)

# 保存
save_post('test-post', '# Test\nHello World!')
print('Saved:', exists_post('test-post'))

# 读取
content = read_post('test-post')
print('Content:', content)

# 列出
print('Posts:', list_posts())

# 删除
delete_post('test-post')
print('Deleted:', not exists_post('test-post'))
"
```

## 路径遍历防护测试

```bash
# 测试恶意 slug
python -c "
from file_utils import validate_slug, FileSecurityError

test_cases = [
    'normal-slug',      # ✅ 正常
    '../etc/passwd',    # ❌ 父目录
    '/etc/passwd',      # ❌ 绝对路径
    'hello/../world',   # ❌ 路径绕过
    'hello\\\\world',   # ❌ 反斜杠
]

for slug in test_cases:
    try:
        validate_slug(slug)
        print(f'✅ {slug}')
    except FileSecurityError as e:
        print(f'❌ {slug}: {e}')
"
```