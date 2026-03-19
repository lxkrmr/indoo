from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock, patch

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

    def test_profile_list_supports_ndjson(self) -> None:
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
user = "deploy"
password = "secret"
""".strip()
                + "\n"
            )

            with self._patched_config_path(config_path):
                result = self.runner.invoke(app, ["--output", "ndjson", "profile", "list"])

            self.assertEqual(result.exit_code, 0, result.stdout)
            lines = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[0]["name"], "local")
            self.assertTrue(lines[0]["is_active"])

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

    def test_doctor_supports_text_output(self) -> None:
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
                result = self.runner.invoke(app, ["--output", "text", "doctor"])

            self.assertEqual(result.exit_code, 0, result.stdout)
            self.assertIn("ready to use", result.stdout)

    def test_write_and_show_accepts_json_payload_and_context_json(self) -> None:
        record = Mock()
        record.read.side_effect = [
            {"amount_total": 10, "state": "draft"},
            {"amount_total": 10, "state": "sale"},
        ]
        connection = Mock()
        connection.profile_name = "local"
        connection.context = {"lang": "de_DE"}
        connection.record.return_value = record

        with patch("indoo.cli.connect", return_value=connection):
            result = self.runner.invoke(
                app,
                [
                    "write-and-show",
                    "sale.order",
                    "42",
                    "amount_total",
                    "state",
                    "--json",
                    '{"state":"sale"}',
                    "--context-json",
                    '{"lang":"de_DE"}',
                ],
            )

        self.assertEqual(result.exit_code, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["write"], {"state": "sale"})
        record.write.assert_called_once_with({"state": "sale"})

    def test_write_and_show_rejects_value_and_json_together(self) -> None:
        result = self.runner.invoke(
            app,
            [
                "write-and-show",
                "sale.order",
                "42",
                "state",
                "--value",
                "state=sale",
                "--json",
                '{"state":"sale"}',
            ],
        )

        self.assertEqual(result.exit_code, 1, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("either --value or --json", payload["message"])

    def test_describe_returns_command_schema(self) -> None:
        result = self.runner.invoke(app, ["describe", "write-and-show"])

        self.assertEqual(result.exit_code, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "describe")
        self.assertEqual(payload["subject"], "write-and-show")
        self.assertTrue(any(option["name"] == "--json" for option in payload["options"]))

    def test_schema_is_alias_for_describe(self) -> None:
        result = self.runner.invoke(app, ["schema", "doctor"])

        self.assertEqual(result.exit_code, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["subject"], "doctor")

    def test_show_rejects_invalid_model_name(self) -> None:
        result = self.runner.invoke(app, ["show", "sale.order?bad=1", "42", "name"])

        self.assertEqual(result.exit_code, 1, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("Model name", payload["message"])

    def test_show_rejects_invalid_context_json(self) -> None:
        result = self.runner.invoke(app, ["show", "sale.order", "42", "name", "--context-json", "[]"])

        self.assertEqual(result.exit_code, 1, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("must be a JSON object", payload["message"])

    def _patched_config_path(self, config_path: Path) -> ExitStack:
        stack = ExitStack()
        stack.enter_context(patch("indoo.cli.default_config_path", return_value=config_path))
        stack.enter_context(patch("indoo.config.default_config_path", return_value=config_path))
        return stack


if __name__ == "__main__":
    unittest.main()
