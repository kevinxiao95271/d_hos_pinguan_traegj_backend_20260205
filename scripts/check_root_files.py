# -*- coding: utf-8 -*-
"""
检查根目录下的文件
"""
from pathlib import Path

root_dir = Path(r"d:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205")

# 排除的目录
exclude_dirs = {'src', 'target', 'scripts', 'docs', '.git', '.mvn', '.idea', 'terminals', 'data'}

# 排除的文件（应该保留的）
keep_files = {'pom.xml', 'mvnw', 'mvnw.cmd', '.gitignore', 'README.md'}

print("=" * 120)
print("Root Directory Files Check")
print("=" * 120)

print(f"\nScanning: {root_dir}")
print("-" * 120)

root_files = []
for item in root_dir.iterdir():
    if item.is_file():
        root_files.append(item)

print(f"\nTotal files in root directory: {len(root_files)}")
print("\nFiles that should be moved:")
print("-" * 120)

should_move = []
should_keep = []

for file_path in sorted(root_files):
    if file_path.name in keep_files:
        should_keep.append(file_path.name)
    else:
        should_move.append(file_path.name)
        print(f"  - {file_path.name}")

print(f"\n{'-' * 120}")
print(f"Summary:")
print(f"  Should keep: {len(should_keep)} files")
for name in sorted(should_keep):
    print(f"    ✓ {name}")

print(f"\n  Should move: {len(should_move)} files")

print(f"\n{'=' * 120}")
