from pathlib import Path

from src.wow_item_csv_exporter import WowItemCsvExporter
from scrape_utils import ScrapeUtils

class OutputValidation:

    TEST_FOLDER = "tests"
    BASE_TEST_OUTPUT_FOLDER = "test_output"
    BASE_OUTPUT_FOLDER = "output"

    @staticmethod
    def validate(item_csv: str) -> None:
        test_folder: Path = Path.cwd() / OutputValidation.TEST_FOLDER / OutputValidation.BASE_TEST_OUTPUT_FOLDER
        output_folder: Path = Path.cwd() / OutputValidation.BASE_OUTPUT_FOLDER
        subfolder = WowItemCsvExporter.ITEMS_FOR_SPEC_FOLDER
        csv_to_validate = WowItemCsvExporter.ALL_COLUMNS_CSV_NAME
        real_out = ScrapeUtils.Persistence.read_textfile(output_folder / item_csv / subfolder / csv_to_validate)
        test_out = ScrapeUtils.Persistence.read_textfile(test_folder / item_csv / subfolder / csv_to_validate)
        out1_match = real_out == test_out
        if not out1_match:
            print("Warning: output does not match expected output!")
            #OutputValidation.print_differences(real_out1, test_out1)
        else:
            print("Validation was passed.")

    @staticmethod
    def print_differences(actual: str, expected: str) -> None:
        expected_lines = expected.splitlines()
        actual_lines = actual.splitlines()
        for i, (expected_line, actual_line) in enumerate(zip(expected_lines, actual_lines), start=1):
            if expected_line != actual_line:
                print(f"Line {i} differs:")
                print(f"Expected: {expected_line}")
                print(f"Actual:   {actual_line}")
                break
        if len(expected_lines) != len(actual_lines):
            print("File lengths differ.")
            print(f"Expected file length: {len(expected_lines)} lines.")
            print(f"Actual file length: {len(actual_lines)} lines.")
