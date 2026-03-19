from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from indoo.cli import app


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_profile_add_creates_active_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.toml"
            with self._patched_config_path(config_path):
                result = self.runner.invoke(
                    app,
                    [
                        "profile",
                        "add",
                        "local",
                        "--url",
                        "http://localhost:8069",
                        "--db",
                        "odoo",
                        "--user",
                        "admin",
                        "--password",
                        "admin",
                    ],
                )

            self.assertEqual(result.exit_code, 0, result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["active_profile"], "local")
            self.assertTrue(config_path.exists())

    def test_doctor_suggests_switch_when_active_profile_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.toml"
            config_path.write_text(
                """
active_profile = "local"

[profiles.local]
url = "http://localhost:8069"
db = "odoo"
user = "admin"
password = "admin"

[profiles.staging]
url = "https://example.com"
db = "odoo"
user = "admin"
password = "admin"
""".strip()
                + "\n"
            )

            with self._patched_config_path(config_path), patch(
                "indoo.cli.OdooConnection.connect",
                side_effect=RuntimeError("connection refused"),
            ):
                result = self.runner.invoke(app, ["doctor"])

            self.assertEqual(result.exit_code, 1, result.stdout)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["next_command"], "indoo profile use staging")

    def test_doctor_reports_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.toml"
            config_path.write_text(
                """
active_profile = "local"

[profiles.local]
url = "http://localhost:8069"
db = "odoo"
user = "admin"
password = "admin"
""".strip()
                + "\n"
            )

            with self._patched_config_path(config_path), patch("indoo.cli.OdooConnection.connect", return_value=object()):
                result = self.runner.invoke(app, ["doctor"])

            self.assertEqual(result.exit_code, 0, result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["checked_profile"], "local")

    def _patched_config_path(self, config_path: Path) -> ExitStack:
        stack = ExitStack()
        stack.enter_context(patch("indoo.cli.default_config_path", return_value=config_path))
        stack.enter_context(patch("indoo.config.default_config_path", return_value=config_path))
        return stack


if __name__ == "__main__":
    unittest.main()
