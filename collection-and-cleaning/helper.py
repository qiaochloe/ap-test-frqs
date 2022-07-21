from os import listdir
import pandas as pd


def get_files(dir_name: str) -> list:
    """Returns a list of the names of all the files in a directory"""

    files = [file for file in listdir(dir_name) if file.endswith(".txt")]
    return files


def get_file_content(file_name: str) -> str:
    """
    Args:
        file_name (str): name of the text file

    Returns:
        str: content of the text file
    """

    with open(file_name, encoding="utf-8") as file:
        file_content = file.read()  # string
    return file_content


def create_csv(df: pd.DataFrame, file_name: str) -> None:

    with open(f"{file_name}", "w+") as file:
        df.to_csv(file, index=False)
