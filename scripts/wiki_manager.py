#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiki管理工具
用于管理.qoder/repowiki目录下的wiki内容
"""

import os
import sys
import shutil
from pathlib import Path

class WikiManager:
    def __init__(self):
        # 由于脚本现在在scripts目录下，需要指向上级目录
        self.base_dir = Path(__file__).parent.parent
        self.wiki_dir = self.base_dir / ".qoder" / "repowiki" / "zh" / "content"
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
    
    def list_wiki_files(self):
        """列出所有wiki文件"""
        print(f"📁 Wiki目录: {self.wiki_dir}")
        print("📄 Wiki文件列表 (Qoder IDE管理):")
        
        if not self.wiki_dir.exists():
            print("  (目录不存在)")
            return
            
        md_files = list(self.wiki_dir.glob("*.md"))
        if not md_files:
            print("  (暂无wiki文件)")
            return
            
        for file in sorted(md_files):
            size = file.stat().st_size
            print(f"  - {file.name} ({size} bytes)")
    
    def create_template(self, filename):
        """提示用户在Qoder IDE中创建wiki文件"""
        print(f"💡 建议在Qoder IDE中直接创建wiki文件: {filename}")
        print("   1. 在Qoder IDE中打开项目")
        print("   2. 导航到 .qoder/repowiki/zh/content/ 目录")
        print("   3. 创建新的.md文件")
        print("   4. 使用Qoder IDE的wiki编辑功能")
    
    def sync_to_github(self):
        """提示如何同步到GitHub Wiki"""
        print("🔄 同步到GitHub Wiki:")
        print("1. 提交更改到git仓库:")
        print("   git add .qoder/repowiki/zh/content/")
        print("   git commit -m '更新wiki内容'")
        print("   git push")
        print("")
        print("2. GitHub Actions会自动检测到更改并同步到GitHub Wiki")
        print("3. 或者在GitHub仓库的Actions页面手动触发'Manual Wiki Sync'")
        print("")
        print("💡 提示: 您可以直接在Qoder IDE中编辑wiki内容！")
    
    def backup_wiki(self):
        """备份wiki内容"""
        backup_dir = self.base_dir / "wiki_backup"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = self._get_timestamp().replace(":", "-").replace(" ", "_")
        backup_path = backup_dir / f"wiki_backup_{timestamp}"
        
        if self.wiki_dir.exists():
            shutil.copytree(self.wiki_dir, backup_path)
            print(f"✅ Wiki内容已备份到: {backup_path}")
        else:
            print("❌ Wiki目录不存在，无法备份")
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    manager = WikiManager()
    
    if len(sys.argv) < 2:
        print("📚 CloudResourceOptimizer Wiki管理工具 (Qoder IDE)")
        print("使用方法:")
        print("  python scripts/wiki_manager.py list          # 列出wiki文件")
        print("  python scripts/wiki_manager.py sync          # 查看同步方法")
        print("  python scripts/wiki_manager.py backup        # 备份wiki内容")
        print("")
        print("💡 提示: 请在Qoder IDE中直接编辑wiki内容")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        manager.list_wiki_files()
    elif command == "create":
        if len(sys.argv) < 3:
            print("💡 建议直接在Qoder IDE中创建wiki文件")
            print("   导航到 .qoder/repowiki/zh/content/ 目录")
            return
        filename = sys.argv[2]
        manager.create_template(filename)
    elif command == "sync":
        manager.sync_to_github()
    elif command == "backup":
        manager.backup_wiki()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()