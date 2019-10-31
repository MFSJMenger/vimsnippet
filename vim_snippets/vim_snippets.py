# -*- coding: utf-8 -*-
#
from jinja2 import Template
#
from .parser import Parser
from .oscommands import mkdir, path_join


class SnippetFiles(object):

    file_mapping = Template("""{% for mapping in mappings %}{{mapping.mode}} {{mapping.map}} <SPACE><Esc>{{mapping.deletechar}}:call {{mapping.filename}}#{{mapping.func_name}}()<CR>:call {{mapping.find_next}}<CR> 
{% endfor %}
""")

    template_vimscript = Template("""
{% for mapping in mappings %} 
function! {{mapping.filename}}#{{mapping.func_name}}()
    let string = [{{mapping.snippet}}]
    :call vimtools#enter_text(string)
endfunction {% endfor %}
""")
    
    @staticmethod
    def set_deletechar(deletechar):
        Parser.set_deletechar(deletechar)

    @classmethod
    def create_vim_files(cls, path_vim, ftplugin, *files):
        parsers = [Parser(ftplugin, filename) for filename in files]
        cls._create(path_vim, ftplugin, parsers)

    @classmethod
    def _create(cls, path_vim, ftplugin, parsers):
        cls._create_autoload(path_vim, ftplugin, parsers)
        cls._create_ftplugin(path_vim, ftplugin, parsers)

    @classmethod
    def _create_ftplugin(cls, path_vim, ftplugin, parsers):
        """create ftplugin"""
        path_ftplugin = path_join(path_vim, 'ftplugin')
        mkdir(path_ftplugin)
        mappings = sum((parser.mappings for parser in parsers), [])

        with open(path_join(path_ftplugin, ftplugin + '.vim'), "w") as f:
            f.write(cls.file_mapping.render(mappings=mappings))

    @classmethod
    def _create_autoload(cls, path_vim, ftplugin, parsers):
        """ """
        autoload = path_join(path_vim, 'autoload')
        mkdir(autoload)

        for parser in parsers:
            with open(path_join(autoload, parser.filename + '.vim'), "w") as f:
                f.write(cls.template_vimscript.render(mappings=parser.mappings))
