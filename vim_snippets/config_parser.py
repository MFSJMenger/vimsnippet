from collections import namedtuple
import yaml


FtPlugin = namedtuple("FtPlugin", ("name", "files"))


def parse_config(configfile):
    
    with open(configfile, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    settings = {
        'deletechar': config['deletechar'],
        'pyversion': config['pyversion'],
        'doc': config['doc'],
        'path_vim': config['path'],
    }

    ftplugin = [FtPlugin(ftplugin, tuple(files)) for ftplugin, files in config['ftplugins'].items()]
    
    return ftplugin, settings
