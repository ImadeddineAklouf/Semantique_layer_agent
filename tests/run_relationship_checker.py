from app.tools.relationship_checker import (
    analyze_relationship,
)


def main() -> None:
    report = analyze_relationship(
        source_file_path=(
            "data/inputs/orders.csv"
        ),
        source_column="CLIENT_ID",
        target_file_path=(
            "data/inputs/clients.csv"
        ),
        target_column="CLIENT_ID",
        documented_cardinality="many-to-one",
    )

    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()