import json
import pandas as pd


def convert_csv_to_json(csv_file: str, json_file: str) -> None:
    df = pd.read_csv(csv_file)
    df.to_json(json_file, orient="records")


def get_json_obj(json_file: str) -> list | dict:
    """
    Args:
        json_file (str): path to json file

    Returns:
        list or dict: json object expressed as python obj
    """

    with open(json_file, "r") as file:
        json_oject = json.load(file)
        return json_oject


def name_json_array(json_obj: list, array_name: str) -> dict:
    """
    Takes an unnamed array of json objects and returns a dictionary.

    Ex:
    >>> data = [{ "id": 1, "course": "biology"}, {"id": 2, "course": "chemistry"}]
    >>> print(name_json_array(data, "courses"))
    { "courses" : [{ "id": 1, "course": "biology"}, {"id": 2, "course": "chemistry"}] }

    Args:
        json_obj (list): unnamed array of json objects
        array_name (str): key to the json array in the dict

    Returns:
        dict: dictionary with one key-value pair
    """

    output = {}
    output[f"{array_name}"] = json_obj

    return output


def combine_json_obj(
    og_obj: list | dict, add_obj: list | dict, attr: str = None
) -> list | dict:

    """
    Appends array of json obj to another array of json obj.

    Args:
        og_obj (list or dict): original json obj
        add_obj (list or dict): additional json obj to be combined
        attr (str): attribute in og_obj dictionary to append add_obj array to

    Returns:
        list or dict:
            array of combined json obj when both args are lists
            dict of combined json in all other cases
    """

    if type(add_obj) is list:
        if type(og_obj) is list:
            return [*og_obj, *add_obj]

        elif type(og_obj) is dict and attr is not None:
            for json_obj in add_obj:
                og_obj[attr].append(json_obj)
            return og_obj

        else:  # append objects to first key-value in dict
            first_key = list(og_obj.keys())[0]
            for json_obj in add_obj:
                og_obj[first_key].append(json_obj)
            return og_obj

    elif type(og_obj) is dict and type(add_obj) is dict:
        return og_obj | add_obj

    else:
        raise TypeError("Wrong combination of types for arguments.")


def create_json_file(json_obj: list | dict, file_name: str) -> None:
    with open(file_name, "w+") as file:
        json.dump(json_obj, file, indent=2)


def main():

    question_csv = "./ap-world-history/question.csv"
    convert_csv_to_json(question_csv, "test.json")
    # questions = get_json_obj(question_csv)
    # create_json_file(questions, "test.json")


if __name__ == "__main__":
    main()
