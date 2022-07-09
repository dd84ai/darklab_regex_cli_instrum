import argparse
import re
from dataclasses import dataclass
from typing import Tuple
from contextlib import suppress


@dataclass
class StringParams:
    quantity_of_digits: int
    regex_word_to_be_present: str
    regex_of_numbers: str
    is_number_check_enabled: bool
    regex_replacing: str


@dataclass
class FileParams:
    input_file: str
    output_file: str


class TestFactoryStringParams:
    def __new__(
        cls,
        regex_word_to_be_present="^rumor",
        regex_of_numbers="[0-9][0-9]*",
        quantity_of_digits=3,
        is_number_check_enabled=True,
        regex_replacing="",
    ):
        return StringParams(
            regex_word_to_be_present=regex_word_to_be_present,
            regex_of_numbers=regex_of_numbers,
            quantity_of_digits=quantity_of_digits,
            is_number_check_enabled=is_number_check_enabled,
            regex_replacing=regex_replacing,
        )


class TestFactoryFileParams:
    def __new__(cls):
        return FileParams(
            input_file="mbases.ini",
            output_file="output_file.txt",
        )


def read_console_input() -> Tuple[FileParams, StringParams]:
    parser = argparse.ArgumentParser(
        description="Copying selected by regex strings to new file"
    )
    parser.add_argument(
        "--input_file",
        type=str,
        default="mbases.ini",
        help='default="mbases.ini", file input to process',
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="output_file.txt",
        help='default="output_file.txt", output file name to save the result',
    )
    parser.add_argument(
        "--quantity_of_digits",
        type=int,
        default=5,
        help="default=5, check for amount of digits present in string, if is_number_check_enabled=True is enabled",
    )
    parser.add_argument(
        "--regex_word_to_be_present",
        type=str,
        default="^rumor",
        help='default="^rumor"'
        ', use as regex_word_to_be_present="^rumor"" in order to grab all words that begin with it'
        ', use regex_word_to_be_present="^rumor|^nickname|^local_faction" in order to grab multiple strings beginning with it"',
    )
    parser.add_argument(
        "--regex_of_numbers",
        type=str,
        default="[0-9][0-9]*",
        help='default="[0-9][0-9]*", regex to identify numbers when check is_number_check_enabled=True for their size is enabled',
    )
    parser.add_argument(
        "--regex_replacing",
        type=str,
        default="",
        help='default="", use as regex_replacing="^\[.*\]|;" in order to grab all strings with "[thing]" and having them replaced to ";"',
    )
    parser.add_argument(
        "--is_number_check_enabled",
        type=bool,
        default=False,
        help="default=False"
        "use True, in order to enable check for number size in strings. Regex for number size in regex_of_numbers parameter",
    )
    args = parser.parse_args()
    return FileParams(
        input_file=args.input_file,
        output_file=args.output_file,
    ), StringParams(
        quantity_of_digits=args.quantity_of_digits,
        regex_word_to_be_present=args.regex_word_to_be_present,
        regex_of_numbers=args.regex_of_numbers,
        is_number_check_enabled=args.is_number_check_enabled,
        regex_replacing=args.regex_replacing,
    )


class WrongStringException(Exception):
    pass


def get_desired_string(txt, string_params: StringParams, log=False) -> str:
    """
    >>> get_desired_string("The rain in Spain", TestFactoryStringParams())
    Traceback (most recent call last):
    script.WrongStringException: The word is not present

    >>> get_desired_string("rumor = base_0_rank, mission_end, 1, 132524", TestFactoryStringParams())
    'rumor = base_0_rank, mission_end, 1, 132524'

    >>> get_desired_string("nickname = 123", TestFactoryStringParams(regex_word_to_be_present="^rumor|^nickname|^local_faction"))
    'nickname = 123'

    >>> get_desired_string("local_faction = 564", TestFactoryStringParams(regex_word_to_be_present="^rumor|^nickname|^local_faction"))
    'local_faction = 564'

    >>> get_desired_string("[GF_NPC]", TestFactoryStringParams(regex_replacing="^\[.*\]|;"), log=True)
    ';\\n'
    """
    if string_params.regex_replacing != "":
        word_to_find, word_to_replace_with = string_params.regex_replacing.split("|")
        if re.search(word_to_find, txt):
            return word_to_replace_with + "\n"

    if not re.search(string_params.regex_word_to_be_present, txt):
        raise WrongStringException("The word is not present")

    found_numbers = re.findall(string_params.regex_of_numbers, txt)

    if string_params.is_number_check_enabled:
        if all(
            [len(number) < string_params.quantity_of_digits for number in found_numbers]
        ):
            raise WrongStringException("size of numbers is wrong")

    return txt


def copy_desired_strings(
    file_params: FileParams, string_params: StringParams, log=False
):
    """
    >>> copy_desired_strings(TestFactoryFileParams(), TestFactoryStringParams(), log = True)
    copied 8786 lines
    """
    with open(file_params.input_file, "r") as file_:
        lines = file_.readlines()

    lines_to_write = []
    for line in lines:

        with suppress(WrongStringException):
            pass
            desired_string = get_desired_string(
                line,
                string_params,
            )
            lines_to_write.append(desired_string)

    with open(file_params.output_file, "w") as file_:
        for line in lines_to_write:
            file_.write(line)

    print(f"copied {len(lines_to_write)} lines")


if __name__ == "__main__":
    file_params, string_params = read_console_input()
    copy_desired_strings(file_params, string_params)
