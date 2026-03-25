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

    def test_search_defaults_to_id_only_with_safe_limit(self) -> None:
        connection = Mock()
        connection.profile_name = "local"
        connection.context = {}
        connection.model.return_value.search.return_value = [{"id": 7}, {"id": 9}]

        with patch("indoo.cli.connect", return_value=connection):
            result = self.runner.invoke(app, ["search", "res.partner"])

        self.assertEqual(result.exit_code, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "search")
        self.assertEqual(payload["fields"], ["id"])
        self.assertEqual(payload["limit"], 10)
        self.assertEqual(payload["offset"], 0)
        self.assertEqual(payload["records"], [{"id": 7}, {"id": 9}])
        connection.model.return_value.search.assert_called_once_with(["id"], limit=10, offset=0, domain=[])

    def test_search_accepts_requested_fields_limit_and_offset(self) -> None:
        connection = Mock()
        connection.profile_name = "local"
        connection.context = {"lang": "de_DE"}
        connection.model.return_value.search.return_value = [{"id": 49, "name": "Alexander Kramer"}]

        with patch("indoo.cli.connect", return_value=connection):
            result = self.runner.invoke(
                app,
                [
                    "search",
                    "res.partner",
                    "name",
                    "--limit",
                    "20",
                    "--offset",
                    "20",
                    "--context-json",
                    '{"lang":"de_DE"}',
                ],
            )

        self.assertEqual(result.exit_code, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["fields"], ["id", "name"])
        self.assertEqual(payload["limit"], 20)
        self.assertEqual(payload["offset"], 20)
        self.assertEqual(payload["context"], {"lang": "de_DE"})
        connection.model.return_value.search.assert_called_once_with(["id", "name"], limit=20, offset=20, domain=[])

    def test_search_accepts_domain_filter(self) -> None:
        connection = Mock()
        connection.profile_name = "local"
        connection.context = {}
        connection.model.return_value.search.return_value = [{"id": 5, "bid_price": 10.0}]

        with patch("indoo.cli.connect", return_value=connection):
            result = self.runner.invoke(
                app,
                [
                    "search",
                    "product.product",
                    "bid_price",
                    "--domain",
                    "[('bid_price', '>', 0)]",
                ],
            )

        self.assertEqual(result.exit_code, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["domain"], [["bid_price", ">", 0]])
        self.assertEqual(payload["records"], [{"id": 5, "bid_price": 10.0}])
        connection.model.return_value.search.assert_called_once_with(
            ["id", "bid_price"], limit=10, offset=0, domain=[("bid_price", ">", 0)]
        )

    def test_search_domain_with_prefix_operator(self) -> None:
        connection = Mock()
        connection.profile_name = "local"
        connection.context = {}
        connection.model.return_value.search.return_value = []

        with patch("indoo.cli.connect", return_value=connection):
            result = self.runner.invoke(
                app,
                [
                    "search",
                    "product.product",
                    "--domain",
                    "['|', ('name', 'ilike', 'Gold'), ('name', 'ilike', 'Silver')]",
                ],
            )

        self.assertEqual(result.exit_code, 0, result.stdout)
        connection.model.return_value.search.assert_called_once_with(
            ["id"],
            limit=10,
            offset=0,
            domain=["|", ("name", "ilike", "Gold"), ("name", "ilike", "Silver")],
        )

    def test_search_rejects_invalid_field_name_with_example(self) -> None:
        with patch("indoo.cli.connect"):
            result = self.runner.invoke(
                app,
                ["search", "res.partner", "id,name"],
            )

        self.assertNotEqual(result.exit_code, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("Invalid field name", payload["message"])
        self.assertIn("indoo search res.partner id name email", payload["message"])

    def test_search_rejects_invalid_domain(self) -> None:
        with patch("indoo.cli.connect"):
            result = self.runner.invoke(
                app,
                ["search", "product.product", "--domain", "not a domain"],
            )

        self.assertNotEqual(result.exit_code, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("Domain must be", payload["message"])

    def test_search_rejects_domain_that_is_not_a_list(self) -> None:
        with patch("indoo.cli.connect"):
            result = self.runner.invoke(
                app,
                ["search", "product.product", "--domain", "('name', 'ilike', 'Gold')"],
            )

        self.assertNotEqual(result.exit_code, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("Domain must be a list", payload["message"])

    def test_fields_returns_metadata(self) -> None:
        connection = Mock()
        connection.profile_name = "local"
        connection.model.return_value.fields.return_value = [
            {
                "name": "notes",
                "type": "text",
                "string": "Terms and Conditions",
                "required": False,
                "readonly": False,
            },
            {
                "name": "state",
                "type": "selection",
                "string": "Status",
                "required": False,
                "readonly": True,
                "selection": [["draft", "RFQ"], ["done", "Locked"]],
            },
        ]

        with patch("indoo.cli.connect", return_value=connection):
            result = self.runner.invoke(app, ["fields_get", "purchase.order", "notes", "state"])

        self.assertEqual(result.exit_code, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "fields_get")
        self.assertEqual(payload["model"], "purchase.order")
        self.assertEqual(payload["fields"][0]["name"], "notes")
        self.assertEqual(payload["fields"][1]["selection"][0][0], "draft")

    def test_fields_reports_unknown_field_without_keyerror_quotes(self) -> None:
        connection = Mock()
        connection.profile_name = "local"
        connection.model.return_value.fields.side_effect = KeyError("Unknown fields: nope")

        with patch("indoo.cli.connect", return_value=connection):
            result = self.runner.invoke(app, ["fields_get", "purchase.order", "nope"])

        self.assertEqual(result.exit_code, 1, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["message"], "Unknown fields: nope")

    def test_read_rejects_invalid_model_name_with_example(self) -> None:
        result = self.runner.invoke(app, ["read", "res partner", "1", "name"])
        self.assertNotEqual(result.exit_code, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("indoo search res.partner id name", payload["message"])

    def test_read_rejects_invalid_model_name(self) -> None:
        result = self.runner.invoke(app, ["read", "sale.order?bad=1", "42", "name"])

        self.assertEqual(result.exit_code, 1, result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("Model name", payload["message"])

    def test_read_rejects_invalid_context_json(self) -> None:
        result = self.runner.invoke(app, ["read", "sale.order", "42", "name", "--context-json", "[]"])

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
