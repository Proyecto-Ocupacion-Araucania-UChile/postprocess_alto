import os
import shutil

def suppress_char(line):
    punctuation = "!:;\",?’.⁋"
    for sign in punctuation:
        line = line.replace(sign, " ")
    return line

def journal_activity(path, action, file, n, p_word, c_word):
    """
    Journal logs to recover all actions to change text and people can verify it !
    :param path: str, path to folder
    :param file: str, name file
    :param n: int, line number
    :param p_word: str, word pre correction
    :param c_word: str, zord post correction
    :return: None
    """

    if os.path.isfile(f"{path}/activity.txt"):
        with open(f"{path}/activity.txt", "a") as f:
            f.write(f"{action}: {file}, l.{n} -> {p_word} change to {c_word}")
            f.write("\n")
    else:
        with open(f"{path}/activity.txt", "w") as f:
            f.write(f"{action}: {file}, l.{n} -> {p_word} change to {c_word}")
            f.write("\n")

def cleaning_folder(path):
    # cleaning folder
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
