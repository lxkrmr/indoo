from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from indoo.config import ConnectionProfile, IndoConfig, default_config_path


class ConfigTests(unittest.TestCase):
    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            config = IndoConfig.create_empty(path)
            config.add_profile(
                "local",
                ConnectionProfile(
                    url="http://localhost:8069",
                    db="odoo",
                    user="admin",
                    password="admin",
                ),
                make_active=True,
            )
            config.save()

            loaded = IndoConfig.load(path)

            self.assertEqual(loaded.active_profile, "local")
            self.assertIn("local", loaded.profiles)
            self.assertEqual(loaded.profiles["local"].url, "http://localhost:8069")

    def test_default_config_path_uses_home_config_on_unix(self) -> None:
        with patch("indoo.config.os.name", "posix"), patch("indoo.config.Path.home", return_value=Path("/tmp/test-home")):
            path = default_config_path()

        self.assertEqual(path, Path("/tmp/test-home/.config/indoo/config.toml"))

    def test_resolve_profile_requires_active_or_explicit_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = IndoConfig.create_empty(Path(tmp) / "config.toml")
            config.add_profile(
                "staging",
                ConnectionProfile(
                    url="https://example.com",
                    db="db",
                    user="user",
                    password="pw",
                ),
            )
            config.active_profile = None

            with self.assertRaises(KeyError) as exc:
                config.resolve_profile()

        self.assertIn("indoo profile use <name>", str(exc.exception))


if __name__ == "__main__":
    unittest.main()
