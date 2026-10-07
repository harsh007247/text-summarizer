import os
from box.exceptions import BoxValueError
import yaml
from textsummarizer.logging import logger
# from ensure import ensure_annotations# ye annotation verify krne ke liye use hota h new version ke sath compatible nhi h toh mein nhi kr rha hu
from box import ConfigBox
from pathlib import Path
from typing import Any

def read_yaml(path_to_yaml: Path)-> ConfigBox:
    """reads yaml file and structures
    
    Args:
        path_to_yaml (str): path like input

    Raises:
        ValueError: if yaml file is empty
        e:empty file

    Returns:
            Configbox : ConfigBox type


    """
    try:
        with open(path_to_yaml) as yaml_file:
            content=yaml.safe_load(yaml_file)
            logger.info(f"yaml file: {path_to_yaml} loaded succesfully")
            return ConfigBox(content)

    except BoxValueError:
        raise ValueError("yaml file is empty")

    except Exception as e:
        raise e



def creat_directories(path_to_directories:list,verbose=True):
    """create a list of directories
    
    Args:
        path_to_directories (list): list of path of directories
        ignorelog (bool,optional): ignore if multiple dirs is to be created.Default to false

    
    """
    for path in path_to_directories:
        os.makedirs(path,exist_ok=True)
        if verbose:
            logger.info(f"create director at : {path}")

def get_size(path:Path)-> str:
    """get size in kb
    
    Args:
        path(Path):Path of the file

    Returns:
            str: Size in kb

    """
    size_in_kb=round(os.path.getsize(path)/1024)
    return f" ~{size_in_kb} KB"
