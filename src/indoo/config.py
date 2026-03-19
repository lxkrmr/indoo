from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib


@dataclass(slots=True)
class ConnectionProfile:
    url: str
    db: str
    user: str
    password: str


@dataclass(slots=True)
class IndoConfig:
    path: Path
    active_profile: str | None
    profiles: dict[str, ConnectionProfile]

    @classmethod
    def load(cls, path: Path | None = None) -> "IndoConfig":
        config_path = path or default_config_path()
        if not config_path.exists():
            raise FileNotFoundError(
                f"Config file not found at {config_path}. "
                "Create a profile with `indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin`."
            )

        data = tomllib.loads(config_path.read_text())
        raw_profiles = data.get("profiles", {})
        profiles = {
            name: ConnectionProfile(
                url=profile_data["url"],
                db=profile_data["db"],
                user=profile_data["user"],
                password=profile_data["password"],
            )
            for name, profile_data in raw_profiles.items()
        }

        return cls(
            path=config_path,
            active_profile=data.get("active_profile"),
            profiles=profiles,
        )

    @classmethod
    def create_empty(cls, path: Path | None = None) -> "IndoConfig":
        return cls(path=path or default_config_path(), active_profile=None, profiles={})

    def resolve_profile(self, name: str | None = None) -> tuple[str, ConnectionProfile]:
        profile_name = name or self.active_profile
        if not profile_name:
            available = ", ".join(sorted(self.profiles)) or "none"
            raise KeyError(
                "No active profile is configured. "
                f"Available profiles: {available}. "
                "Choose one with `indoo profile use <name>` or create one with "
                "`indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin`."
            )
        if profile_name not in self.profiles:
            available = ", ".join(sorted(self.profiles)) or "none"
            raise KeyError(
                f"Profile {profile_name!r} was not found. "
                f"Available profiles: {available}. "
                "Check `indoo profile list`."
            )
        return profile_name, self.profiles[profile_name]

    def add_profile(self, name: str, profile: ConnectionProfile, make_active: bool = False) -> None:
        self.profiles[name] = profile
        if make_active or not self.active_profile:
            self.active_profile = name

    def use_profile(self, name: str) -> None:
        if name not in self.profiles:
            available = ", ".join(sorted(self.profiles)) or "none"
            raise KeyError(f"Profile {name!r} was not found. Available profiles: {available}.")
        self.active_profile = name

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        if self.active_profile:
            lines.append(f'active_profile = "{escape_toml(self.active_profile)}"')
            lines.append("")

        for name in sorted(self.profiles):
            profile = self.profiles[name]
            lines.append(f"[profiles.{name}]")
            lines.append(f'url = "{escape_toml(profile.url)}"')
            lines.append(f'db = "{escape_toml(profile.db)}"')
            lines.append(f'user = "{escape_toml(profile.user)}"')
            lines.append(f'password = "{escape_toml(profile.password)}"')
            lines.append("")

        content = "\n".join(lines).rstrip() + "\n"
        self.path.write_text(content)


def default_config_path() -> Path:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is not set. Set APPDATA or create the config file manually.")
        return Path(appdata) / "indoo" / "config.toml"
    return Path.home() / ".config" / "indoo" / "config.toml"


def escape_toml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
