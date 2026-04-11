#!/usr/bin/env python3
"""
数据库初始化脚本
任务码: TASK-002

用法:
    python init_database.py          # 初始化数据库（创建所有表）
    python init_database.py --drop   # 删除所有表后重新创建
    python init_database.py --check  # 检查数据库连接
"""

import argparse
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, drop_db, check_db, engine
from sqlalchemy import inspect


def show_tables():
    """显示所有数据库表"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("\n📊 数据库表列表:")
    print("-" * 40)
    if not tables:
        print("  (暂无表)")
    else:
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"\n  📋 {table}")
            for col in columns:
                col_type = str(col['type']).replace('()', '')
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"     - {col['name']}: {col_type} ({nullable})")
    print("-" * 40)
    return tables


def main():
    parser = argparse.ArgumentParser(description='数据库初始化工具')
    parser.add_argument('--drop', action='store_true', help='删除所有表后重新创建')
    parser.add_argument('--check', action='store_true', help='检查数据库连接')
    args = parser.parse_args()

    print("=" * 50)
    print("🗄️  数据库管理工具")
    print("=" * 50)

    if args.check:
        print("\n🔍 检查数据库连接...")
        if check_db():
            print("✅ 数据库连接正常")
            show_tables()
        else:
            print("❌ 数据库连接失败")
            sys.exit(1)
        return

    if args.drop:
        print("\n⚠️  警告: 即将删除所有数据表!")
        confirm = input("确认删除? (输入 'yes' 确认): ")
        if confirm.lower() == 'yes':
            drop_db()
        else:
            print("已取消")
            return

    print("\n🚀 初始化数据库...")
    init_db()
    show_tables()
    print("\n✅ 完成!")


if __name__ == "__main__":
    main()
