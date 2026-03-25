from indoo.client import OdooConnection
from indoo.config import IndoConfig


def main() -> None:
    config = IndoConfig.load()
    profile_name, profile = config.resolve_profile()
    connection = OdooConnection.connect(profile_name, profile)

    records = connection.model("your.model").list(
        ["field_x", "computed_y"],
        limit=10,
        offset=0,
    )

    print(records)


if __name__ == "__main__":
    main()
