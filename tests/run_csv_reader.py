from app.tools.csv_reader import read_csv_metadata


def main() -> None:
    """
    Analyse le fichier CSV de démonstration et affiche
    les métadonnées validées au format JSON.
    """

    file_path = "data/inputs/clients.csv"

    print(f"Analyse du fichier : {file_path}")

    metadata = read_csv_metadata(file_path)

    print(metadata.model_dump_json(indent=2))


if __name__ == "__main__":
    main()