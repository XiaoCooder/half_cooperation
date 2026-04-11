"""
Markdown 文件存储配置
任务码: TASK-007
"""

import os

# 存储根目录
STORAGE_ROOT = os.path.join(os.path.dirname(__file__), "posts")

# Markdown 文件目录
POSTS_DIR = os.path.join(STORAGE_ROOT, "content")

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {".md", ".markdown"}

# 文件名最大长度
MAX_FILENAME_LENGTH = 200

# 单个文件最大大小（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024


def ensure_storage_dirs():
    """确保存储目录存在"""
    os.makedirs(POSTS_DIR, exist_ok=True)


def get_post_file_path(slug: str) -> str:
    """
    根据 slug 获取文章文件路径

    Args:
        slug: 文章 slug 标识符

    Returns:
        完整的文件路径
    """
    # 确保使用 .md 扩展名
    if not slug.endswith('.md'):
        slug = slug + '.md'
    return os.path.join(POSTS_DIR, slug)


def get_post_content_path(slug: str) -> str:
    """
    获取文章内容路径（不含扩展名）

    Args:
        slug: 文章 slug 标识符

    Returns:
        不含扩展名的文件路径
    """
    return os.path.join(POSTS_DIR, slug)