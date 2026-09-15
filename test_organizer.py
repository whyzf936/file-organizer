"""单元测试：验证分类规则和移动逻辑。

运行方式：
    python -m unittest test_organizer -v
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rules import get_category
from organizer import collect_files, plan_move, unique_target, execute_move


class TestRules(unittest.TestCase):
    """测试分类规则。"""

    def test_known_extensions(self):
        self.assertEqual(get_category("photo.jpg"), "图片")
        self.assertEqual(get_category("简历.pdf"), "文档")
        self.assertEqual(get_category("movie.mp4"), "视频")
        self.assertEqual(get_category("song.mp3"), "音频")
        self.assertEqual(get_category("archive.zip"), "压缩包")
        self.assertEqual(get_category("main.py"), "代码")
        self.assertEqual(get_category("setup.exe"), "安装包")

    def test_unknown_extension(self):
        self.assertEqual(get_category("data.xyz"), "其他")

    def test_case_insensitive(self):
        # 大写扩展名也应该识别
        self.assertEqual(get_category("PHOTO.JPG"), "图片")

    def test_no_extension(self):
        self.assertEqual(get_category("README"), "其他")


class TestOrganizer(unittest.TestCase):
    """测试整理逻辑。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _make_file(self, name: str) -> Path:
        p = self.dir / name
        p.write_text("test", encoding="utf-8")
        return p

    def test_collect_files(self):
        self._make_file("a.txt")
        self._make_file("b.jpg")
        (self.dir / "subdir").mkdir()
        files = collect_files(self.dir)
        self.assertEqual(len(files), 2)  # 子文件夹不计入

    def test_plan_move(self):
        self._make_file("a.txt")
        self._make_file("b.jpg")
        plans = plan_move(collect_files(self.dir), self.dir)
        categories = {dst.parent.name for _, dst in plans}
        self.assertIn("文档", categories)
        self.assertIn("图片", categories)

    def test_unique_target_no_conflict(self):
        target = self.dir / "图片" / "a.jpg"
        self.assertEqual(unique_target(target), target)

    def test_unique_target_with_conflict(self):
        # 目标已存在同名文件时，应加序号避免覆盖
        existing = self.dir / "图片" / "a.jpg"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("old", encoding="utf-8")
        resolved = unique_target(existing)
        self.assertEqual(resolved.name, "a_1.jpg")
        self.assertNotEqual(resolved, existing)

    def test_execute_move_dry_run(self):
        """dry-run 模式不应真的移动文件。"""
        f = self._make_file("a.jpg")
        plans = plan_move(collect_files(self.dir), self.dir)
        moved = execute_move(plans, dry_run=True)
        self.assertEqual(moved, 1)
        self.assertTrue(f.exists())  # 文件还在原地

    def test_execute_move_real(self):
        """真实模式应把文件移动到对应类别目录。"""
        self._make_file("a.jpg")
        plans = plan_move(collect_files(self.dir), self.dir)
        moved = execute_move(plans, dry_run=False)
        self.assertEqual(moved, 1)
        self.assertTrue((self.dir / "图片" / "a.jpg").exists())


if __name__ == "__main__":
    unittest.main()
