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