#!/usr/bin/env python3
"""
迁移脚本：将音乐数据中的title字段迁移到album字段
"""

import json
import os
import sys

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
MUSIC_FILE = os.path.join(DATA_DIR, 'music.json')

def migrate_music_data():
    """将音乐数据中的title字段迁移到album字段"""
    print(f"开始迁移音乐数据...")
    
    # 确保数据目录和文件存在
    if not os.path.exists(MUSIC_FILE):
        print(f"错误：找不到音乐数据文件 {MUSIC_FILE}")
        return False
    
    try:
        # 读取现有数据
        with open(MUSIC_FILE, 'r', encoding='utf-8') as f:
            music_items = json.load(f)
        
        print(f"读取到 {len(music_items)} 条音乐记录")
        
        # 统计需要迁移的记录数
        need_migration_count = 0
        for item in music_items:
            if 'title' in item:
                need_migration_count += 1
        
        print(f"需要迁移的记录数: {need_migration_count}")
        
        # 执行迁移
        for item in music_items:
            # 如果有title但没有album，将title的值赋给album
            if 'title' in item and not item.get('album'):
                print(f"迁移: {item.get('title')} -> album")
                item['album'] = item.pop('title')
            # 如果同时有title和album，保留album并删除title
            elif 'title' in item:
                print(f"删除title字段: {item.get('title')}, 保留album: {item.get('album')}")
                item.pop('title')
        
        # 保存更新后的数据
        with open(MUSIC_FILE, 'w', encoding='utf-8') as f:
            json.dump(music_items, f, ensure_ascii=False, indent=4)
        
        print(f"迁移完成，已更新 {need_migration_count} 条记录")
        return True
    
    except Exception as e:
        print(f"迁移过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = migrate_music_data()
    sys.exit(0 if success else 1) 