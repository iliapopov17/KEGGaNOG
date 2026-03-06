import pathlib

from kegganog.processing import data_processing


def test_parse_emapper_filters_and_formats_kegg_ko(tmp_path):
    input_file = tmp_path / "emapper.tsv"
    temp_folder = tmp_path / "temp"
    temp_folder.mkdir()

    input_file.write_text(
        "\n".join(
            [
                "## header line 1",
                "## header line 2",
                "## header line 3",
                "## header line 4",
                "KEGG_ko\tOther",
                "ko:K00001,ko:K00002\tX",
                "-\tY",
                "ko:K00003\tZ",
            ]
        )
        + "\n"
    )

    output_path = data_processing.parse_emapper(str(input_file), str(temp_folder))

    content = pathlib.Path(output_path).read_text().strip().splitlines()
    assert content == ["SAMPLE K00001", "SAMPLE K00002", "SAMPLE K00003"]
