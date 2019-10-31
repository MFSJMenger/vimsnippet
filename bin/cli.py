# -*- coding: utf-8 -*-

"""Console script for vim_snippets."""
import os
import sys
#
import click
#
from vim_snippets import SnippetFiles
from vim_snippets import parse_config
from vim_snippets import mkdir


@click.command()
@click.argument('configfile', nargs=1)
def main(configfile):
    """Console script for vim_snippets."""
    ftplugins, settings = parse_config(configfile)

    path_vim = settings['path_vim']
    # in case bundle path does not exists, create it!
    mkdir(path_vim)
    #
    SnippetFiles.set_deletechar(settings['deletechar'])
    for ftplugin in ftplugins:
        SnippetFiles.create_vim_files(path_vim, ftplugin.name, *ftplugin.files)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
