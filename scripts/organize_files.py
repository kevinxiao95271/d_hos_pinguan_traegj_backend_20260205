# -*- coding: utf-8 -*-
"""
整理项目文件结构
- 将根目录下的所有 .py 脚本移动到 scripts 目录
- 将根目录下的所有 .md 和 .txt 文档移动到 docs 目录
"""
import os
import shutil
from pathlib import Path

# 项目根目录
root_dir = Path(r"d:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205")
scripts_dir = root_dir / "scripts"
docs_dir = root_dir / "docs"

# 确保目标目录存在
scripts_dir.mkdir(exist_ok=True)
docs_dir.mkdir(exist_ok=True)

print("=" * 120)
print("File Organization")
print("=" * 120)

# 需要排除的文件
exclude_files = {
    'organize_files.py',  # 当前脚本自己
    'pom.xml',
    'mvnw',
    'mvnw.cmd',
    '.gitignore'
}

# 需要排除的目录
exclude_dirs = {
    'src',
    'target',
    'scripts',
    'docs',
    '.git',
    '.mvn',
    '.idea',
    'terminals'
}

moved_scripts = []
moved_docs = []
skipped_files = []

print(f"\n[Step 1] Moving Python scripts to {scripts_dir}")
print("-" * 120)

# 移动根目录下的 .py 文件到 scripts
for file_path in root_dir.glob("*.py"):
    if file_path.name in exclude_files:
        print(f"  [SKIP] {file_path.name} (excluded)")
        skipped_files.append(file_path.name)
        continue
    
    target_path = scripts_dir / file_path.name
    
    # 如果目标文件已存在，添加后缀
    if target_path.exists():
        base_name = file_path.stem
        suffix = file_path.suffix
        counter = 1
        while target_path.exists():
            target_path = scripts_dir / f"{base_name}_backup{counter}{suffix}"
            counter += 1
        print(f"  [MOVE] {file_path.name} -> {target_path.name} (renamed to avoid conflict)")
    else:
        print(f"  [MOVE] {file_path.name} -> scripts/")
    
    shutil.move(str(file_path), str(target_path))
    moved_scripts.append(file_path.name)

print(f"\n[Step 2] Moving documentation files to {docs_dir}")
print("-" * 120)

# 移动根目录下的 .md 和 .txt 文件到 docs
doc_extensions = ['.md', '.txt']

for ext in doc_extensions:
    for file_path in root_dir.glob(f"*{ext}"):
        if file_path.name in exclude_files:
            print(f"  [SKIP] {file_path.name} (excluded)")
            skipped_files.append(file_path.name)
            continue
        
        target_path = docs_dir / file_path.name
        
        # 如果目标文件已存在，检查是否相同
        if target_path.exists():
            # 如果文件内容相同，删除根目录的
            if file_path.read_bytes() == target_path.read_bytes():
                print(f"  [DELETE] {file_path.name} (duplicate, already in docs/)")
                file_path.unlink()
            else:
                # 内容不同，重命名
                base_name = file_path.stem
                suffix = file_path.suffix
                counter = 1
                while target_path.exists():
                    target_path = docs_dir / f"{base_name}_backup{counter}{suffix}"
                    counter += 1
                print(f"  [MOVE] {file_path.name} -> {target_path.name} (renamed to avoid conflict)")
                shutil.move(str(file_path), str(target_path))
            moved_docs.append(file_path.name)
        else:
            print(f"  [MOVE] {file_path.name} -> docs/")
            shutil.move(str(file_path), str(target_path))
            moved_docs.append(file_path.name)

print(f"\n{'=' * 120}")
print("[Summary]")
print("=" * 120)

print(f"\nMoved to scripts/: {len(moved_scripts)} files")
if moved_scripts:
    for name in sorted(moved_scripts):
        print(f"  - {name}")

print(f"\nMoved to docs/: {len(moved_docs)} files")
if moved_docs:
    for name in sorted(moved_docs):
        print(f"  - {name}")

if skipped_files:
    print(f"\nSkipped: {len(skipped_files)} files")
    for name in sorted(set(skipped_files)):
        print(f"  - {name}")

print(f"\n{'=' * 120}")
print("[Complete]")
print("=" * 120)
print(f"\nAll files have been organized!")
print(f"  - Python scripts: scripts/")
print(f"  - Documentation: docs/")

print(f"\n{'=' * 120}")
