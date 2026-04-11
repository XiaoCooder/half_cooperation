"""
文件工具函数 - 包含安全验证
任务码: TASK-007
"""

import os
import re
from pathlib import Path
from typing import Optional


class FileSecurityError(Exception):
    """文件安全验证错误"""
    pass


def validate_slug(slug: str) -> bool:
    """
    验证 slug 是否安全

    安全规则：
    1. 不能包含路径分隔符
    2. 不能包含父目录引用 (..)
    3. 不能是绝对路径
    4. 不能包含 null 字节
    5. 只能包含安全的字符（字母、数字、连字符、下划线）

    Args:
        slug: 待验证的 slug

    Returns:
        验证是否通过

    Raises:
        FileSecurityError: 验证失败
    """
    if not slug:
        raise FileSecurityError("Slug 不能为空")

    # 检查 null 字节
    if '\x00' in slug:
        raise FileSecurityError("Slug 包含非法字符 (null bytes)")

    # 检查绝对路径
    if slug.startswith('/') or slug.startswith('\\'):
        raise FileSecurityError("Slug 不能是绝对路径")

    # 检查父目录引用
    if '..' in slug:
        raise FileSecurityError("Slug 不能包含父目录引用")

    # 检查路径分隔符
    if '/' in slug or '\\' in slug:
        raise FileSecurityError("Slug 不能包含路径分隔符")

    # 检查字符安全性 - 只允许字母、数字、连字符、下划线
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        raise FileSecurityError("Slug 只能包含字母、数字、连字符和下划线")

    return True


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除不安全字符
    filename = re.sub(r'[^\w\-.]', '_', filename)

    # 限制长度
    max_length = 200
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext

    return filename


def get_safe_path(base_dir: str, slug: str, extension: str = ".md") -> str:
    """
    获取安全的文件路径

    该函数确保最终路径不会超出 base_dir，防止路径遍历攻击。

    Args:
        base_dir: 基础目录
        slug: 文件 slug
        extension: 文件扩展名

    Returns:
        安全的文件路径

    Raises:
        FileSecurityError: 路径不安全
    """
    # 先验证 slug
    validate_slug(slug)

    # 清理 slug
    slug = sanitize_filename(slug)

    # 确保扩展名正确
    if extension and not slug.endswith(extension):
        slug = slug + extension

    # 构建路径
    requested_path = os.path.normpath(os.path.join(base_dir, slug))

    # 解析基础目录的绝对路径
    base_abs = os.path.abspath(base_dir)

    # 确保请求的路径在基础目录内
    requested_abs = os.path.abspath(requested_path)

    if not requested_abs.startswith(base_abs + os.sep) and requested_abs != base_abs:
        raise FileSecurityError("路径遍历攻击被阻止")

    return requested_path


def check_file_size(file_path: str, max_size: int) -> bool:
    """
    检查文件大小是否超过限制

    Args:
        file_path: 文件路径
        max_size: 最大字节数

    Returns:
        是否在限制内
    """
    if not os.path.exists(file_path):
        return True

    size = os.path.getsize(file_path)
    return size <= max_size


def is_safe_extension(filename: str, allowed_extensions: set) -> bool:
    """
    检查文件扩展名是否安全

    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名集合

    Returns:
        是否安全
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions


def normalize_slug(slug: str) -> str:
    """
    规范化 slug

    1. 转为小写
    2. 替换空格为连字符
    3. 移除不安全字符

    Args:
        slug: 原始 slug

    Returns:
        规范化后的 slug
    """
    # 转小写
    slug = slug.lower()

    # 替换空格和下划线为连字符
    slug = re.sub(r'[\s_]+', '-', slug)

    # 只保留安全字符
    slug = re.sub(r'[^a-z0-9\-]', '', slug)

    # 移除连续的连字符
    slug = re.sub(r'-+', '-', slug)

    # 移除首尾连字符
    slug = slug.strip('-')

    return slug


def ensure_file_exists(file_path: str, default_content: str = "") -> None:
    """
    确保文件存在，如果不存在则创建

    Args:
        file_path: 文件路径
        default_content: 默认内容
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(default_content)