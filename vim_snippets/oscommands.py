import os

def isdir(directory):

    if not os.path.exists(directory):
        return False
    if not os.path.isdir(directory):
        raise Exception(f"{directory} exists but is not a folder!")
    return True

def remove_file(path):
    # file does not exisits do nothing
    if not os.path.exists(path):
        return
    # path exists but is not a file:
    if not os.path.isfile(path):
        raise Exception(f"{path} is not a file, cannot remove!")
    os.remove(path)


def mkdir(path):
    if not isdir(path):
        os.makedirs(path)

path_join = os.path.join
