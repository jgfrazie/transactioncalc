import re
import os
import csv
import argparse

### Types the raw date arguments passed
DATE = lambda arg: tuple([int(date_element) for date_element in arg.split('/')])

def type_statements(arg: str) -> list[str]:
    """Converts the raw argument of a statement into a list of file paths to statements

    Args:
        arg (str): either a list of file paths to statements deliminated by commas (,) or the path to a directory containing such

    Returns:
        list[str]: a list of OS paths to statements
    """
    if ',' in arg:
        return arg.split(',')
    return [
        os.path.join(arg, f) \
        for f in os.listdir(arg) \
            if os.path.isfile(os.path.join(arg, f))
    ]

def get_arguements() -> argparse.Namespace:
    """Gets the command line arguments

    Returns:
        argparse.Namespace: parsed command-line arguments
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='TransactionRecordsCompiler',
        description='Processes the provided transaction records'
    )
    parser.add_argument(
        '--bank-statements',
        help='a list of file paths to bank statement CSV files',
        type=type_statements
    )
    parser.add_argument(
        '--discover-credit-statements',
        help='a list of file paths to discover credit statement CSV files',
        type=type_statements
    )
    parser.add_argument(
        '--start-date',
        required=False,
        help='all transactions before this date are excluded from the compiled log',
        default='00/00/0000',
        type=DATE
    )
    parser.add_argument(
        '--end-date',
        required=False,
        help='all transactions after this date are excluded from the compiled log',
        default='99/99/9999',
        type=DATE
    )
    parser.add_argument(
        '--discover-statement'
    )
    return parser.parse_args()


class TransactionAggregator:

    def __init__(self, bank_statements: list[str], discover_credit_statements: list[str],
                start_date: tuple[int, int, int], end_date: tuple[int, int, int]):
        """Class constructor

        Args:
            bank_statements (list[str]): all bank statements used in this call
            discover_credit_statements (list[str]): all discover credit statements used in this call
            start_date (tuple[int, int, int]): the day, month, and year to consider as a starting point when processing specific methods
            end_date (tuple[int, int, int]): the day, month, and year to consider as a cut-off when processing specific methods
        """
        self.__bank_statements: list[list[str]] = bank_statements
        self.__discover_credit_statements: list[str] = self.__read_in_statements(discover_credit_statements)
        self.__start_date: tuple[int, int, int] = start_date
        self.__end_date: tuple[int, int, int] = end_date
        

    def __read_statement(self, statement_file: str) -> list[str]:
        """Reads in a single statement from a CSV

        Args:
            statement_file (str): the file path to the CSV

        Returns:
            list[str]: the contents of the CSV
        """
        with open(statement_file) as csv_file:
            statement = csv.reader(csv_file, delimiter=',')
            return [entry for entry in statement]


    def __read_in_statements(self, statements: list[str]) -> list[list[str]]:
        """Reads in all statement CSVs

        Args:
            statements (list[str]): file paths to CSVs of statements

        Returns:
            list[list[str]]: all CSVs of statements read in
        """
        return [
            self.__read_statement(statement) \
            for statement in statements
        ]

    
    def get_discover_statements(self) -> list[list[str]]:
        """Gets list of all discover credit statements

        Returns:
            list[list[str]]: The discover credit statements read in
        """
        return self.__discover_credit_statements


def main(compiler: TransactionAggregator) -> None:
    """Controls the operational flow of the program"""
    print(compiler.get_discover_statements()[0][1])


if __name__ == '__main__':
    args: argparse.Namespace = get_arguements()
    main(TransactionAggregator(args.bank_statements,
    args.discover_credit_statements, args.start_date, args.end_date))