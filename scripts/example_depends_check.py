from odoo_lab.client import Lab, LabConfig


def main() -> None:
    lab = Lab(LabConfig.from_env())
    record = lab.record("your.model", 42)

    before = record.read(["field_x", "computed_y"])
    record.write({"field_x": 10})
    after = record.read(["field_x", "computed_y"])

    print({"before": before, "after": after})


if __name__ == "__main__":
    main()
