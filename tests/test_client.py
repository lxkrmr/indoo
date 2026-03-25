from __future__ import annotations

import unittest

from indoo.client import normalize_field_info, parse_odoo_url


class ClientTests(unittest.TestCase):
    def test_normalize_field_info_keeps_useful_metadata(self) -> None:
        info = normalize_field_info(
            "state",
            {
                "type": "selection",
                "string": "Status",
                "required": False,
                "readonly": True,
                "selection": [("draft", "RFQ"), ("done", "Locked")],
            },
        )

        self.assertEqual(info["name"], "state")
        self.assertEqual(info["type"], "selection")
        self.assertTrue(info["readonly"])
        self.assertEqual(info["selection"], [["draft", "RFQ"], ["done", "Locked"]])

    def test_parse_odoo_url_maps_http_to_jsonrpc(self) -> None:
        host, protocol, port = parse_odoo_url("http://localhost:8069")

        self.assertEqual(host, "localhost")
        self.assertEqual(protocol, "jsonrpc")
        self.assertEqual(port, 8069)

    def test_parse_odoo_url_maps_https_to_jsonrpc_ssl(self) -> None:
        host, protocol, port = parse_odoo_url("https://odoo.example.com")

        self.assertEqual(host, "odoo.example.com")
        self.assertEqual(protocol, "jsonrpc+ssl")
        self.assertEqual(port, 443)

    def test_parse_odoo_url_rejects_non_http_scheme(self) -> None:
        with self.assertRaises(ValueError) as exc:
            parse_odoo_url("jsonrpc://localhost:8069")

        self.assertIn("Use http:// or https://", str(exc.exception))



if __name__ == "__main__":
    unittest.main()
