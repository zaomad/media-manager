#!/usr/bin/env python3
"""
JSON到SQLite数据迁移工具

此脚本将媒体管理系统的JSON数据迁移到SQLite数据库中。
"""

import os
import sys
import logging
import argparse
from app.migrate_json_to_sqlite import run_migration

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='将JSON数据迁移到SQLite数据库')
    parser.add_argument('--force', action='store_true', help='强制执行迁移，即使数据库已存在')
    args = parser.parse_args()
    
    logger.info("=== 媒体管理系统数据迁移工具 ===")
    logger.info("从JSON到SQLite的数据迁移")
    
    # 检查数据目录
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        logger.error(f"数据目录不存在: {data_dir}")
        return 1
    
    # 检查JSON文件
    json_files = ['books.json', 'movies.json', 'music.json']
    missing_files = []
    for file in json_files:
        file_path = os.path.join(data_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        logger.warning(f"以下JSON文件不存在: {', '.join(missing_files)}")
        confirm = input("是否继续迁移? (y/n): ")
        if confirm.lower() != 'y':
            logger.info("迁移已取消")
            return 0
    
    # 检查数据库文件
    db_file = os.path.join(data_dir, 'media_manager.db')
    if os.path.exists(db_file) and not args.force:
        logger.warning(f"数据库文件已存在: {db_file}")
        confirm = input("数据库文件已存在，是否覆盖? (y/n): ")
        if confirm.lower() != 'y':
            logger.info("迁移已取消")
            return 0
    
    # 执行迁移
    logger.info("开始执行数据迁移...")
    success = run_migration()
    
    if success:
        logger.info("数据迁移成功完成!")
        logger.info(f"数据库文件位置: {db_file}")
        return 0
    else:
        logger.error("数据迁移失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 