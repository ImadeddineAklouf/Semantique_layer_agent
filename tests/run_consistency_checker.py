from app.tools.business_document_parser import (
    parse_business_document,
)
from app.tools.consistency_checker import (
    compare_metadata_with_documentation,
)
from app.tools.csv_reader import read_csv_metadata
from app.tools.document_reader import read_document


def main() -> None:
    metadata = read_csv_metadata(
        "data/inputs/clients.csv"
    )

    document = read_document(
        "data/documentation/"
        "clients_documentation.md"
    )

    documentation = parse_business_document(
        document
    )

    report = compare_metadata_with_documentation(
        metadata=metadata,
        documentation=documentation,
    )

    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()