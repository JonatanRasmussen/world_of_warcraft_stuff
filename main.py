import unittest
from tests.budo_tests import BudoTests
from wowhead_test import MainWowheadPipeline

class Main():
    @staticmethod
    def tests_and_main() -> None:
        suite = unittest.TestLoader().loadTestsFromTestCase(BudoTests)
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        if result.wasSuccessful():
            Main.main()
        else:
            print("One or more tests failed. Main program not executed.")

    @staticmethod
    def main() -> None:
        MainWowheadPipeline.main()

if __name__ == "__main__":
    Main.tests_and_main()