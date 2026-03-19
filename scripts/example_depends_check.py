from indoo.client import OdooConnection
from indoo.config import IndoConfig


def main() -> None:
    config = IndoConfig.load()
    profile_name, profile = config.resolve_profile()
    connection = OdooConnection.connect(profile_name, profile)
    record = connection.record("your.model", 42)

    before = record.read(["field_x", "computed_y"])
    record.write({"field_x": 10})
    after = record.read(["field_x", "computed_y"])

    print({"before": before, "after": after})


if __name__ == "__main__":
    main()
