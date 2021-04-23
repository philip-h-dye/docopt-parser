#!/usr/bin/env python3

from __future__ import print_function

import sys
import os
import re
import shutil

from glob import glob

from invoke import task
from invoke.util import log

#------------------------------------------------------------------------------

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

def newline(): print()

body_color = u"\u001b[38;5;189m"  # blue
line_color = u"\u001b[38;5;186m"  # yellow
# ansi_reset	= u"\u001b[0m"
ansi_reset = ''

def start():
    newline()
    sys.stdout.write(body_color)

def separator():
    newline()
    print(line_color + ('- - - - - ' * 6) + ansi_reset)
    newline()

#------------------------------------------------------------------------------

def verbose_run(c, cmd):
    print('+ ' + cmd)
    result = c.run(cmd, pty=True, warn=True)
    # print('invoke : task exit status = {}'.format(str(result.exited)))
    if not result.ok:
        print('')
        print('task failed - aborting')
        exit(result.exited)
    return result

#------------------------------------------------------------------------------

def package_name():
    # If 'src' is a symlink, use base name of the symlink target
    if os.path.islink('src') and os.path.isdir('src/.'):
        return os.path.basename(os.readlink('src'))
    # Use script name as basis
    import inspect
    script_file = inspect.getfile(inspect.currentframe())
    return os.path.basename(os.path.dirname(os.path.abspath(script_file)))

#------------------------------------------------------------------------------

# Search for cython extension build artifacts when cleaning
EXTENSION_SOURCE_TOP_DEFAULTS = [package_name(), 'src']

#------------------------------------------------------------------------------

@task
def info(c):
    """
    Get runtime environment info.       Usage:  info
    """
    start()
    verbose_run(c, "python setup.py info")
    separator()

#------------------------------------------------------------------------------

# essentialy a forward declaration
@task
def clean_(c):
    clean(c)

#------------------------------------------------------------------------------

# @task(clean_)
@task(optional=['docs'])
def format(c, top='src'):
    """
    Run autopep8 on all .py files below 'src'.

    CHANGED: Run google's python formatter on all .py files below 'src'.

    Ideally 'src' is a symlink to your package source directory
    and tests are located at src/tests (actually <package-name>/tests).
    """

    # Didn't cut it.
    # verbose_run(c,"yapf --in-place "
    #             + ' '.join(list(python_source_files(top='src/.'))))

    # verbose_run(c,"autopep8 --in-place -aaaaaaaa "
    #             + ' '.join(list(python_source_files(top='src/.') )))
    start()
    for python_file in python_source_files(top='src/.'):
        # -a <= --aggressive : enough to pass flake8
        verbose_run(c, f"autopep8 --in-place -aaaaaaaa {python_file}")
    separator()

#------------------------------------------------------------------------------

@task(format)
def flake8(c, top='src'):
    """
    Run flake8 on all .py files below 'src'.

    Ideally 'src' is a symlink to your package source directory,
    <package-name>, and tests are located at src/tests (actually
    <package-name>/tests).
    """
    start()
    verbose_run(
        c,
        "flake8 " +
        ' '.join(
            list(
                python_source_files(
                    top='src/.'))))
    separator()

#------------------------------------------------------------------------------

# @task(clean_,flake8)
# @task(flake8, optional=['docs'])
@task(optional=['docs'])
def build(c, docs=False):
    """
    Build the package.                  Usage:  build [--docs]
    """
    start()
    verbose_run(c, "python setup.py build")
    if docs:
        verbose_run(c, "sphinx-build docs docs/_build")
    separator()

#------------------------------------------------------------------------------

# @task(build,optional=['main'])
@task(optional=['main'])
def test(c, main=False):
    """
    Run the test suite.                 Usage:  test [--main]

    Options :

      --main    Execute <package>/__main__.py and not the test suite

    """

    start()

    if main:
        # '-m' requires <package>/__main__.py
        package = slurp('package-name.txt').strip()
        main_args = 'main-args.txt'
        main_args = slurp(main_args).strip(
        ) if os.path.exists(main_args) else ''
        verbose_run(c, "python -m {} {} ".format(package, main_args))
    else:
        verbose_run(c, "python setup.py test")

    separator()

#------------------------------------------------------------------------------

# @task(clean_,flake8)
# @task(flake8, optional=['docs'])
# @task(optional=['docs'])
@task()
def wheel(c):
    """
    Build the wheel
    """
    start()
    verbose_run(c, "python setup.py bdist_wheel ")
    separator()

#------------------------------------------------------------------------------

# @task(build,optional=['system'])
@task(wheel, optional=['system'])
def install(c, system=False):
    """
    Install the package.                Usage:  install [--system]

    Install for the user (default) or, if '--system' specified, for all users.

    Options :

      --system  Install for all users

    """
    start()

    # Weirdly dies complaining about broken symlinks and such in temporary
    # directory, some related to tests
    # verbose_run(c, "python3 -m pip install %s ." % ('' if system else '--user'))

    # Building the wheel and installing from it works better
    package = package_name()
    verbose_run(c, f"python3 -m pip install --no-index "
                f" --find-links=dist {package} --force-reinstall %s "
                % ('' if system else '--user') )

    separator()

#------------------------------------------------------------------------------

@task(optional=('docs', 'no-bytecode', 'extra'))
def clean(c, docs=False, no_bytecode=False, extra=None):
    """
    Cleanup build & test artifacts.     Usage:  clean [options]

    Options :
      --no-bytecode   Retain .pyc and .pyo byte code files.
      --docs          Also remove 'docs/_build'.
      --extra <p>     Also remove files matching pattern <p>.
    """

    start()

    removed = 0

    # At the top level
    patterns = ['build', 'dist', '.eggs', '*.egg', '*.egg-info' ]
    if not no_bytecode:
        patterns += ['*.pyc', '*.pyo']
    if extra:
        patterns.append(extra)
    # print(f": clean : top : patterns = {patterns}")
    for pattern in patterns:
        for relative_path in glob(pattern):
            print("removing '{}'".format(relative_path))
            if os.path.isdir(relative_path):
                shutil.rmtree(relative_path)
            else :
                os.remove(relative_path)
            removed += 1
    if docs:
        relative_path = 'docs/_build'
        print("removing '{}'".format(relative_path))
        shutil.rmtree(relative_path)
        removed += 1

    # From the top level downward
    matcher_for_directories = re.compile(r'^(__pycache__|[.]pytest_cache)')
    file_patterns = r'.*~'
    if not no_bytecode:
        file_patterns += r'|.*[.](pyc|pyo|so|o|obj)'
    matcher_for_files = re.compile(r'^(' + file_patterns + r')$')

    for parent, subdirs, files in os.walk('.'):

        for subdir in subdirs:
            if matcher_for_directories.match(subdir):
                relative_path = os.path.join(parent, subdir)
                print("removing '{}'".format(relative_path))
                shutil.rmtree(relative_path)
                removed += 1

        for file_ in files:
            if matcher_for_files.match(file_):
                relative_path = os.path.join(parent, file_)
                print("removing '{}'".format(relative_path))
                os.remove(relative_path)
                removed += 1

    if removed <= 0:
        print('nothing to remove - primary cleanup')

    log.info('cleaned up')

    separator()

#------------------------------------------------------------------------------

def python_source_files(*, top='.', extension='py', exclude=[]):

    for file in ['setup.py', 'tasks.py']:
        if file in exclude:
            continue
        if os.path.exists(file):
            yield file

    if isinstance(top, str):
        top = [top]

    for area in top:
        if not os.path.exists(area):
            # print("- '{}' does not exist".format(area))
            continue
        for walk_root, walk_dirs, walk_files in os.walk(area):
            for file_name in walk_files:
                if file_name.endswith('.' + extension):
                    if file_name in exclude:
                        continue
                    file_path = os.path.join(walk_root, file_name)
                    if file_path in exclude:
                        continue
                    yield file_path

#------------------------------------------------------------------------------
