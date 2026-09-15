"""文件分类规则：把文件扩展名映射到类别。

把「规则」单独放一个文件，好处是：
以后想新增类别、调整规则，只改这里，主程序不用动。
"""
from __future__ import annotations

from pathlib import Path

# 类别 -> 该类别对应的扩展名列表
CATEGORIES: dict[str, list[str]] = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "文档": [".pdf", ".doc", ".docx", ".txt", ".md", ".xls", ".xlsx",
             ".ppt", ".pptx", ".csv"],
    "视频": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "代码": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".html",
             ".css", ".json", ".xml", ".sh", ".go", ".rs"],
    "安装包": [".exe", ".msi", ".apk"],
}

# 无法识别的扩展名统一归入这个类别
UNKNOWN_CATEGORY = "其他"


def get_category(filename: str) -> str:
    """根据文件名返回它所属的类别，未知类型归为「其他」。

    .lower() 是为了把 .JPG 和 .jpg 当成同一个扩展名处理。
    """
    ext = Path(filename).suffix.lower()
    for category, exts in CATEGORIES.items():
        if ext in exts:
            return category
    return UNKNOWN_CATEGORY
