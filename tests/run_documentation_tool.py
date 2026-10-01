import json

from app.tools import analyze_documentation_file


def main() -> None:
    file_path = (
        "data/documentation/"
        "clients_documentation.md"
    )

    print(f"Analyse du document : {file_path}")

    result = analyze_documentation_file(
        file_path
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()