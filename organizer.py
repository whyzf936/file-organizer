"""文件整理器：按类型自动把散乱文件归类到子文件夹。

用法示例：
    python organizer.py --dir D:/下载                 # 整理指定目录
    python organizer.py --dir D:/下载 --dry-run       # 只预览，不真的移动
    python organizer.py --dir D:/下载 --include-dirs  # 同时处理子文件夹
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from rules import get_category

# Windows 控制台默认 GBK 编码，输出中文/emoji 会报错，这里切到 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def collect_files(directory: Path) -> list[Path]:
    """收集目录下所有文件（默认不进入子文件夹）。"""
    return [p for p in directory.iterdir() if p.is_file()]


def unique_target(target: Path) -> Path:
    """如果目标位置已有同名文件，自动加序号，避免覆盖。

    例如 a.txt 已存在，则返回 a_1.txt；再存在则 a_2.txt，以此类推。
    """
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 1
    while True:
        candidate = target.with_name(f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def plan_move(files: list[Path], directory: Path) -> list[tuple[Path, Path]]:
    """计算每个文件要移动到哪里，返回 (源路径, 目标路径) 列表。"""
    plans = []
    for f in files:
        category = get_category(f.name)
        target = unique_target(directory / category / f.name)
        plans.append((f, target))
    return plans


def execute_move(plans: list[tuple[Path, Path]], dry_run: bool) -> int:
    """执行移动计划；dry_run=True 时只打印预览、不真动手。

    返回实际移动（或预览会移动）的文件数。
    """
    moved = 0
    for src, dst in plans:
        if src.resolve() == dst.resolve():
            # 文件本来就在正确的位置，跳过
            continue
        if dry_run:
            print(f"  [预览] {src.name}  ->  {dst.parent.name}/")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.replace(dst)
            print(f"  ✅ {src.name}  ->  {dst.parent.name}/")
        moved += 1
    return moved


def report(plans: list[tuple[Path, Path]]) -> None:
    """整理结束后，按类别统计移动了多少文件。"""
    counter = Counter()
    for _, dst in plans:
        counter[dst.parent.name] += 1
    print("\n📊 分类统计：")
    for category, count in sorted(counter.items(), key=lambda x: -x[1]):
        print(f"   {category:<6} {count} 个")


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="organizer",
        description="按文件类型自动归类目录下的文件",
    )
    parser.add_argument("--dir", default=".", help="要整理的目录（默认当前目录）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只预览会怎么移动，不实际执行")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    directory = Path(args.dir).expanduser()

    if not directory.is_dir():
        print(f"❌ 目录不存在：{directory}", file=sys.stderr)
        sys.exit(1)

    files = collect_files(directory)
    if not files:
        print("📭 该目录下没有文件")
        return

    plans = plan_move(files, directory)

    if args.dry_run:
        print(f"🔍 预览模式：共 {len(files)} 个文件，将这样归类：")
    else:
        print(f"📁 共 {len(files)} 个文件，开始整理：")

    moved = execute_move(plans, args.dry_run)

    if moved == 0:
        print("  所有文件都已经在正确位置，无需整理 ✨")
    elif args.dry_run:
        print(f"\n预览完成：共 {moved} 个文件会被移动（未实际执行）")
    else:
        print(f"\n✅ 整理完成：共移动 {moved} 个文件")
        report(plans)


if __name__ == "__main__":
    main()
