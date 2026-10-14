import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "bin/omarchy-github-graph"


def load_script():
    loader = importlib.machinery.SourceFileLoader("github_graph_test", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        with mock.patch.object(Path, "home", return_value=self.home):
            self.mod = load_script()
        self.state = self.home / ".local/state/omarchy/current"
        (self.state / "theme").mkdir(parents=True)
        (self.state / "theme.name").write_text("test-theme\n")
        (self.state / "theme/colors.toml").write_text(
            'background = "#000000"\nforeground = "#ffffff"\n')
        self.background = self.home / "github-contributions.png"
        self.background.write_text("wallpaper")
        self.link = self.state / "background"
        self.link.symlink_to(self.background)
        self.mod.STATE = self.state
        self.mod.PREVIOUS = self.home / ".local/state/omarchy-github-graph/previous"
        self.data = ("octocat", {"totalContributions": 1, "weeks": []})
        self.fetch = mock.patch.object(self.mod, "fetch", return_value=self.data)
        self.fetch_mock = self.fetch.start()
        self.addCleanup(self.fetch.stop)
        self.render = mock.patch.object(self.mod, "render")
        self.render_mock = self.render.start()
        self.addCleanup(self.render.stop)
        self.commands = []
        def run(args, **kwargs):
            self.commands.append(args)
            return subprocess.CompletedProcess(args, 0)
        self.run = mock.patch.object(self.mod.subprocess, "run", side_effect=run)
        self.run.start()
        self.addCleanup(self.run.stop)

    def invoke(self, *args):
        with mock.patch.object(Path, "home", return_value=self.home), \
                mock.patch.object(sys, "argv", [str(SCRIPT), *args]):
            self.mod.main()

    def output_path(self):
        return self.home / ".config/omarchy/backgrounds/test-theme/github-contributions.png"

    def test_inactive_automatic_skips_before_theme_read(self):
        self.link.unlink()
        (self.state / "theme.name").unlink()
        self.invoke("--if-active")
        self.fetch_mock.assert_not_called()

    def test_active_render_then_identical_refresh_skips(self):
        self.invoke("--if-active")
        self.render_mock.assert_called_once()
        self.assertEqual(len(self.commands), 1)
        self.output_path().touch()
        self.render_mock.reset_mock()
        self.commands.clear()
        self.invoke("--if-active")
        self.render_mock.assert_not_called()
        self.assertEqual(self.commands, [])

    def test_calendar_change_redraws(self):
        self.invoke("--if-active")
        self.output_path().touch()
        self.render_mock.reset_mock()
        self.data = ("octocat", {"totalContributions": 2, "weeks": []})
        self.fetch_mock.return_value = self.data
        self.invoke("--if-active")
        self.render_mock.assert_called_once()

    def test_colors_change_redraws(self):
        self.invoke("--if-active")
        self.output_path().touch()
        self.render_mock.reset_mock()
        (self.state / "theme/colors.toml").write_text('background = "#111111"\nforeground = "#ffffff"\n')
        self.invoke("--if-active")
        self.render_mock.assert_called_once()

    def test_missing_png_redraws(self):
        self.invoke("--if-active")
        self.render_mock.reset_mock()
        self.invoke("--if-active")
        self.render_mock.assert_called_once()

    def test_wallpaper_switched_during_fetch_is_not_rendered_or_applied(self):
        other = self.home / "other.jpg"
        other.write_text("other")
        self.fetch_mock.side_effect = lambda: (self.link.unlink(), self.link.symlink_to(other), self.data)[-1]
        self.invoke("--if-active")
        self.render_mock.assert_not_called()
        self.assertEqual(self.commands, [])

    def test_fetch_timeout_is_informative(self):
        self.fetch.stop()
        with mock.patch.object(self.mod.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired("gh", 60)) as request:
            with self.assertRaisesRegex(SystemExit, "gh api timed out.*retry"):
                self.invoke("--if-active")
            self.assertEqual(request.call_args.kwargs["timeout"], 60)

    def test_explicit_set_bypasses_unchanged_cache(self):
        self.invoke("--if-active")
        self.output_path().touch()
        self.render_mock.reset_mock()
        self.commands.clear()
        self.invoke("--set")
        self.render_mock.assert_called_once()
        self.assertEqual(len(self.commands), 1)

    def test_apply_failure_invalidates_cache_for_retry(self):
        self.run.stop()
        failing = mock.patch.object(self.mod.subprocess, "run", return_value=subprocess.CompletedProcess([], 1))
        failing.start()
        self.addCleanup(failing.stop)
        with self.assertRaisesRegex(SystemExit, "could not apply wallpaper.*retry"):
            self.invoke("--if-active")
        cache = self.output_path().with_suffix(".sha256")
        self.assertFalse(cache.exists())
        failing.stop()
        retry = mock.patch.object(self.mod.subprocess, "run", return_value=subprocess.CompletedProcess([], 0))
        retry.start()
        self.addCleanup(retry.stop)
        self.render_mock.reset_mock()
        self.invoke("--if-active")
        self.render_mock.assert_called_once()
        self.assertTrue(cache.exists())


if __name__ == "__main__":
    unittest.main()
