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
        self.wiki_dir = self.base_dir / ".qoder" / "repowiki"
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
    
    def list_wiki_files(self):
        """列出所有wiki文件"""
        print(f"📁 Wiki目录: {self.wiki_dir}")
        print("📄 Wiki文件列表:")
        
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
        """创建wiki模板文件"""
        if not filename.endswith('.md'):
            filename += '.md'
            
        filepath = self.wiki_dir / filename
        
        if filepath.exists():
            print(f"❌ 文件 {filename} 已存在")
            return
            
        template_content = f"""# {filename[:-3]}

## 概述

请在这里添加内容描述...

## 主要内容

### 章节1
内容描述...

### 章节2
内容描述...

## 相关链接
- [首页](Home)
- [使用指南](Usage-Guide)

---
*创建时间: {self._get_timestamp()}*
"""
        
        filepath.write_text(template_content, encoding='utf-8')
        print(f"✅ 已创建模板文件: {filename}")
    
    def sync_to_github(self):
        """提示如何同步到GitHub Wiki"""
        print("🔄 同步到GitHub Wiki:")
        print("1. 提交更改到git仓库:")
        print("   git add .qoder/repowiki/")
        print("   git commit -m '更新wiki内容'")
        print("   git push")
        print("")
        print("2. GitHub Actions会自动检测到更改并同步到GitHub Wiki")
        print("3. 或者在GitHub仓库的Actions页面手动触发'Manual Wiki Sync'")
    
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
        print("📚 CloudResourceOptimizer Wiki管理工具")
        print("使用方法:")
        print("  python scripts/wiki_manager.py list          # 列出wiki文件")
        print("  python scripts/wiki_manager.py create <名称>  # 创建新的wiki文件")
        print("  python scripts/wiki_manager.py sync          # 查看同步方法")
        print("  python scripts/wiki_manager.py backup        # 备份wiki内容")
        print("")
        print("💡 提示: 请在项目根目录下运行此脚本")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        manager.list_wiki_files()
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ 请提供文件名")
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