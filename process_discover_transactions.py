import re
import csv
import argparse

LIST_OF_STRINGS = lambda arg: arg.split(',')
DATE = lambda arg: tuple([int(date_element) for date_element in arg.split('/')])

def parse_arguements() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='TransactionRecordsCompiler',
        description='Processes the provided transaction records'
    )
    parser.add_argument(
        '--bank-statements',
        required=True,
        help='a list of bank statement CSV files',
        type=LIST_OF_STRINGS
    )
    parser.add_argument(
        '--discover-credit-statements',
        required=True,
        help='a list of discover credit statement CSV files',
        type=LIST_OF_STRINGS
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

    return parser


class TransactionRecordsCompiler:

    def __init__(self, bank_statements: list[str], discover_credit_statements: list[str],
                start_date: tuple[int, int, int], end_date: tuple[int, int, int]):
        self.__bank_statements: list[list[str]] = self.__read_in_bank_statements(bank_statements)
        self.__discover_credit_statements: list[str] = discover_credit_statements
        self.__start_date: tuple[int, int, int] = start_date
        self.__end_date: tuple[int, int, int] = end_date
        

    def __read_bank_statement(self, statement_file: str) -> list[str]:
        with open(statement_file) as csv_file:
            statement = csv.reader(csv_file, delimiter=',')
            return [entry for entry in statement]


    def __read_in_bank_statements(self, bank_statements: list[str]) -> list[list[str]]:
        return [
            self.__read_bank_statement(statement) \
            for statement in bank_statements
        ]

    
    def get_bank_statements(self) -> list[list[str]]:
        return self.__bank_statements


def main(compiler: TransactionRecordsCompiler) -> None:
    print(compiler.get_bank_statements()[0][0])


if __name__ == '__main__':
    args: argparse.Namespace = parse_arguements().parse_args()
    main(TransactionRecordsCompiler(args.bank_statements,
    args.discover_credit_statements, args.start_date, args.end_date))