import re
import os
import csv
import types
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
        self.__bank_statements: list[list[dict[str, str | float]]] = self.__read_in_statements(bank_statements, is_bank=True) if bank_statements is not None else None
        self.__discover_credit_statements: list[list[dict[str, str | float]]] = self.__read_in_statements(discover_credit_statements, is_discover=True) if discover_credit_statements is not None else None
        self.__start_date: tuple[int, int, int] = start_date
        self.__end_date: tuple[int, int, int] = end_date
        

    def __read_statement(self, statement_file: str, converter: types.FunctionType | None) -> list[dict[str, str | float]]:
        """Reads in a single statement from a CSV. If flag is specified, processes it to standardized format. Otherwise, only takes in raw CSV format.

        Args:
            statement_file (str): the file path to the CSV
            converter (types.FunctionType | None): a function to convert the raw statement into the standardize form. If None, return raw_statement.

        Returns:
            list[dict[str, str | float]]: the contents of the CSV
        """
        with open(statement_file) as csv_file:
            statement = csv.reader(csv_file, delimiter=',')
            raw_statement: list[list[str]] = [entry for entry in statement]
            keys: list[str] = raw_statement[0]
            raw_statement = raw_statement[1:]
            typed_statement: list[dict[str, str | float]] = []
            for entry_id in range(len(raw_statement)):
                entry: list[str] = raw_statement[entry_id]
                raw_statement[entry_id] = {keys[element_id]: entry[element_id] for element_id in range(len(entry))}
            return raw_statement if converter is None else converter(raw_statement)


    def __read_in_statements(self, statements: list[str], is_discover: bool=False, is_bank: bool=False) -> list[list[dict[str, str | float]]]:
        """Reads in all statement CSVs. If flag is specified, processes it to standardized format. Otherwise, only takes in raw CSV format.

        Args:
            statements (list[str]): file paths to CSVs of statements
            is_discover (bool, optional): flag signifies this is a discover credit statement. Defaults to False.
            is_bank (bool, optional): flag signifies this is a bank statement. Defaults to False.

        Returns:
            list[list[dict[str, str | float]]]: all CSVs of statements read in
        """
        if is_discover and is_bank:
            raise RuntimeError('statement cannot be both a discover and bank statement')

        return [
            self.__read_statement(
                statement,
                self.__convert_discover_statement if is_discover \
                    else None if is_bank \
                    else None
            ) \
            for statement in statements
        ]


    def __convert_discover_statement(self, statement: list[dict[str, str | float]]) -> list[dict[str, str | float]]:
        """Converts discover's statement format to a standardized one

        Args:
            statement (list[dict[str, str  |  float]]): the discover formatted statement

        Returns:
            list[dict[str, str | float]]: the standard formatted statement
        """
        for entry_id in range(len(statement)):
            entry: dict[str, str | float] = statement[entry_id]
            del entry['Post Date']
            statement[entry_id]: dict[str, str | float] = {
                'Date': entry.pop('Trans. Date'),
                'Description': entry.pop('Description'),
                'Amount': float(entry.pop('Amount').replace(',', '')),
                'Category': entry.pop('Category')
            }
        return statement

    
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