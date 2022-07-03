import os
import shutil


def suppress_char(line):
    """
    Function to remove special characters
    :param line: str, line to need cleanup
    :return: str, line
    """
    punctuation = "!:;\",?’.⁋"
    for sign in punctuation:
        line = line.replace(sign, " ")
    return line


def cleaning_folder(path):
    """
    clean folder
    :param path:
    :return: None
    """
    for filename in os.listdir(path):
        if filename != "readme.md":
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


