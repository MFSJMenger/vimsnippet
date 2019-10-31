import os
from collections import namedtuple
from copy import deepcopy
import yaml
#
from jinja2 import Template
#
from .oscommands import remove_file


class Parser(object):

    def __init__(self, ftplugin, filename):
        self.filename = os.path.basename(filename).rpartition('.')[0]
        self.preprocessor = _Preprocessor(filename)
        self.mappings = []
        self._generate_mappings(ftplugin)

    @staticmethod
    def set_deletechar(deletechar):
        _PrepareMappings.set_deletechar(deletechar)

    def _parse(self):

        name = f"PARSED_FILE_{self.filename}__PARSED"

        with open(name, "w") as f:
            f.write(self.preprocessor.parse())

        with open(name, "r") as f:
            out = yaml.load(f, Loader=yaml.SafeLoader)

        remove_file(name)

        return out

    def _generate_mappings(self, ftplugin):
        parsed = self._parse()
        default = parsed['mappings']
        self.filename = f"mappings_{self.filename}_{ftplugin}"
        for category, functions in parsed.items():
            if category == 'mappings':
                continue
            for func_name, function in functions.items():
                self.mappings.append(_PrepareMappings.create_entry(default, function, self.filename, f"{category}_call_{func_name}"))


class _Preprocessor(object):

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        start_end = "# ----------------------------------------"
        len_indent = 4
        out = ""
        last_line = None
        nindent = 0

        with open(self.filename, "r") as fl:

            for line in fl:
                if start_end in line:
                    nindent = len(last_line) - len(last_line.lstrip())

                    out += " "*nindent
                    out += "tmpl: |\n"
                    nindent += len_indent
                    for line in fl:
                        if start_end in line:
                            break
                        out += " "*nindent
                        out += line
                    continue
                out += line 
                last_line = line
        return out


class _PrepareMappings(object):
    """All functions to create a suitable string for vim"""

    next_marker = '<++>'
    #
    MapSetting = namedtuple("MapSetting", ('map', 'mode',
                                           'find_next', 'filename',
                                           'func_name', 'deletechar',
                                           'snippet'))

    implemented_modes = {
                'insert': 'inoremap',
                'normal': 'nnoremap',
    }

    settings = { 
            'leader': None,
            'typ': 'insert',
            'deletechar': 'x',
            'find_next': 'vimtools#find_next_marker()',
            'map': None,
    }

    @classmethod
    def set_deletechar(cls, deletechar):
        if deletechar is None:
            return
        cls.settings['deletechar'] = deletechar


    @classmethod
    def create_entry(cls, default, snippet, filename, func_name):
        """create entry"""
        settings = deepcopy(cls.settings)
        settings['filename'] = filename
        settings['func_name'] = func_name
        
        for key in settings.keys():
            if snippet.get(key, None) is not None:
                settings[key] = snippet[key]
            else:
                if default.get(key, None) is not None:
                    settings[key] = default[key]
        
        string = snippet.get('tmpl', None) 
        if string is None:
            return
        
        settings['snippet'] = ", ".join(cls.prepare_vimstr(line)
                                        for line in  string.splitlines())
        
        return cls.MapSetting(cls._join_mappings(settings['leader'], settings['map']),
                          cls._get_mapping_command(settings['typ']),
                          settings['find_next'],
                          settings['filename'],
                          settings['func_name'],
                          settings['deletechar'],
                          settings['snippet'])

    @classmethod
    def prepare_vimstr(cls, line):
        line = cls._prepare_vimstr(line)
        return "'" + line + "'"

    @classmethod
    def _prepare_vimstr(cls, line):
        """Modifie line so that it fits the vim script needs"""
        next_marker = cls.next_marker
        len_next_marker = len(next_marker)
        # replace single quotes with double quotes!
        line = line.replace("'", '"')
        # do nothing        
        if next_marker not in line:
            return line
        # Add additional spaces, if needed
        characters_left = len(line) - line.rfind(next_marker) - len_next_marker
        # add additional space!
        if characters_left == 0:
            line += " "
        if characters_left == 1:
            # should not happen in the current implementation
            if line[-1] == "\n":
                line += " "
        return line


    @classmethod
    def _get_mapping_command(cls, command):
        
        if command not in cls.implemented_modes:
            raise Exception(f"{command} not understood!")
        
        return cls.implemented_modes[command]

    @staticmethod
    def _join_mappings(*args):
        return "".join(arg.strip() if arg is not None else "" for arg in args)
