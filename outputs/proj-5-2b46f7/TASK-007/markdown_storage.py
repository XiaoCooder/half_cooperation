"""
Markdown 文件存储核心模块
任务码: TASK-007
实现文章内容读写本地文件系统功能
"""

import os
from typing import Optional, List
from datetime import datetime

from storage_config import (
    POSTS_DIR,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    get_post_file_path,
    ensure_storage_dirs,
)
from file_utils import (
    validate_slug,
    get_safe_path,
    check_file_size,
    is_safe_extension,
    normalize_slug,
    FileSecurityError,
)


class MarkdownStorageError(Exception):
    """Markdown 存储错误"""
    pass


class PostNotFoundError(MarkdownStorageError):
    """文章不存在错误"""
    pass


class PostExistsError(MarkdownStorageError):
    """文章已存在错误"""
    pass


class StorageFullError(MarkdownStorageError):
    """存储空间不足错误"""
    pass


# 初始化存储目录
ensure_storage_dirs()


def save_post(slug: str, content: str, overwrite: bool = False) -> str:
    """
    保存文章内容到文件

    Args:
        slug: 文章 slug 标识符
        content: Markdown 内容
        overwrite: 是否覆盖已存在的文件

    Returns:
        保存的文件路径

    Raises:
        FileSecurityError: slug 不安全
        PostExistsError: 文章已存在且不允许覆盖
        StorageFullError: 存储空间不足
    """
    # 规范化 slug
    slug = normalize_slug(slug)

    # 验证 slug 安全性
    validate_slug(slug)

    # 获取安全路径
    file_path = get_safe_path(POSTS_DIR, slug, ".md")

    # 检查文件是否已存在
    if os.path.exists(file_path) and not overwrite:
        raise PostExistsError(f"文章 '{slug}' 已存在")

    # 检查内容大小
    content_size = len(content.encode('utf-8'))
    if content_size > MAX_FILE_SIZE:
        raise StorageFullError(
            f"内容大小 {content_size} bytes 超过限制 {MAX_FILE_SIZE} bytes"
        )

    # 写入文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        raise MarkdownStorageError(f"写入文件失败: {e}")

    return file_path


def read_post(slug: str) -> str:
    """
    读取文章内容

    Args:
        slug: 文章 slug 标识符

    Returns:
        文章 Markdown 内容

    Raises:
        FileSecurityError: slug 不安全
        PostNotFoundError: 文章不存在
    """
    # 规范化 slug
    slug = normalize_slug(slug)

    # 验证 slug 安全性
    validate_slug(slug)

    # 获取安全路径
    file_path = get_safe_path(POSTS_DIR, slug, ".md")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise PostNotFoundError(f"文章 '{slug}' 不存在")

    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        raise MarkdownStorageError(f"读取文件失败: {e}")


def delete_post(slug: str) -> bool:
    """
    删除文章

    Args:
        slug: 文章 slug 标识符

    Returns:
        是否成功删除

    Raises:
        FileSecurityError: slug 不安全
        PostNotFoundError: 文章不存在
    """
    # 规范化 slug
    slug = normalize_slug(slug)

    # 验证 slug 安全性
    validate_slug(slug)

    # 获取安全路径
    file_path = get_safe_path(POSTS_DIR, slug, ".md")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise PostNotFoundError(f"文章 '{slug}' 不存在")

    # 删除文件
    try:
        os.remove(file_path)
        return True
    except IOError as e:
        raise MarkdownStorageError(f"删除文件失败: {e}")


def exists_post(slug: str) -> bool:
    """
    检查文章是否存在

    Args:
        slug: 文章 slug 标识符

    Returns:
        文章是否存在
    """
    try:
        slug = normalize_slug(slug)
        validate_slug(slug)
        file_path = get_safe_path(POSTS_DIR, slug, ".md")
        return os.path.exists(file_path)
    except FileSecurityError:
        return False


def list_posts(extension: str = ".md") -> List[dict]:
    """
    列出所有文章

    Args:
        extension: 文件扩展名过滤

    Returns:
        文章信息列表
    """
    posts = []

    if not os.path.exists(POSTS_DIR):
        return posts

    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(extension):
            continue

        file_path = os.path.join(POSTS_DIR, filename)

        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            slug = filename[:-len(extension)]  # 移除扩展名

            posts.append({
                "slug": slug,
                "filename": filename,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

    # 按修改时间排序，最新的在前
    posts.sort(key=lambda x: x["modified_at"], reverse=True)

    return posts


def get_post_metadata(slug: str) -> dict:
    """
    获取文章元数据

    Args:
        slug: 文章 slug 标识符

    Returns:
        文章元数据字典

    Raises:
        FileSecurityError: slug 不安全
        PostNotFoundError: 文章不存在
    """
    # 规范化 slug
    slug = normalize_slug(slug)

    # 验证 slug 安全性
    validate_slug(slug)

    # 获取安全路径
    file_path = get_safe_path(POSTS_DIR, slug, ".md")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise PostNotFoundError(f"文章 '{slug}' 不存在")

    # 获取文件信息
    stat = os.stat(file_path)

    return {
        "slug": slug,
        "filename": os.path.basename(file_path),
        "path": file_path,
        "size": stat.st_size,
        "size_readable": _format_size(stat.st_size),
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def _format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def get_storage_stats() -> dict:
    """
    获取存储统计信息

    Returns:
        存储统计信息
    """
    posts = list_posts()

    total_size = sum(p["size"] for p in posts)

    return {
        "posts_count": len(posts),
        "total_size": total_size,
        "total_size_readable": _format_size(total_size),
        "storage_dir": POSTS_DIR,
    }


def init_storage() -> None:
    """初始化存储目录"""
    ensure_storage_dirs()
    print(f"✅ Markdown 存储初始化完成: {POSTS_DIR}")


# 模块加载时自动初始化
init_storage()