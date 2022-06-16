import re

def get_file_content(file_name):
    """
    Args: 
        file_name (str): name of the text file
    
    Returns: 
        str: content of the text file
    """
    
    with open(file_name, encoding="utf-8") as file:
        file_content = file.read() # string
        
    return file_content

def remove_phrases(file_content, *regex_lists, regex_flags=re.I|re.M):
    """Removes phrases using regex
    
    Args:
        file_content (str): text content 
        regex_lists (list): list of regex to remove phrases by
        regex_flags
        
    Returns:
        str: the text content with phrases removed 
    """
        
    for regex_list in regex_lists:
        for regex in regex_list: 
            file_content = re.sub(regex, '', file_content, flags=regex_flags)
    
    return file_content
