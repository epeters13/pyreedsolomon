# Original Author    : Edwin G. W. Peters @ epeters
#   Creation date    : Fri Jan 29 15:19:20 2021 (+1100)
#   Email            : edwin.peters@unsw.edu.au
# ------------------------------------------------------------------------------
# Last-Updated       : Fri Feb  5 18:03:11 2021 (+1100)
#           By       : Edwin G. W. Peters @ epeters
# ------------------------------------------------------------------------------
# File Name          : setup.py
# Description        : 
# ------------------------------------------------------------------------------
# Copyright          : Insert license
# ------------------------------------------------------------------------------


import setuptools

def _run_git_command(cmd):
    git_error = None
    from subprocess import Popen, PIPE
    stdout = None
    try:
        popen = Popen(["git"] + cmd, stdout=PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
            git_error = "git returned error code %d: %s" % (popen.returncode, stderr)
    except OSError:
        git_error = "(OS error, likely git not found)"

    if git_error is not None:
        print("Trouble invoking git")
        print("The package directory appears to be a git repository, but I could")
        print("not invoke git to check whether my submodules are up to date.")
        print("")
        print("The error was:")
        print(git_error)
        print("Hit Ctrl-C now if you'd like to think about the situation.")
        count_down_delay(delay=0)
    if stdout:
        return stdout.decode("utf-8"), git_error
    else:
        return '', "(subprocess call to git did not succeed)"

    
print('checking out submodules')
stdout,git_error = _run_git_command(["submodule", "update", "--init"])

# HACK we need to make the config.h file.  All our config parameters are provided already, so it can be empty
open('reed-solomon/src/config.h','a').close()

if git_error is None:
    print("git submodules initialized successfully")
else:
    print(f'git submodule initialization failed')
    print(stdout)
    print(git_error)

reed_solomon = setuptools.Extension('librs',
                                    define_macros = [
                                        ('CONFIG_REED_SOLOMON_ENC8','1'),
                                        ('CONFIG_REED_SOLOMON_DEC8','1'),
                                        ('CONFIG_REED_SOLOMON_ENC16','1'),
                                        ('CONFIG_REED_SOLOMON_DEC16','1')
                                    ],
                                    sources = ['reed-solomon/src/rs_codec.cc','reed-solomon/src/reed_solomon.c'])


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='pyreedsolomon',
    version='1.0.3',
    packages=setuptools.find_packages(),
    url='https://github.com/mugpahug/pyreedsolomon',
    license='GPL3',
    author='Edwin G. W. Peters',
    author_email='edwin.g.w.peters@gmail.com',
    description='Fast python interface to the linux kernel reed solomon libraries',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='reed solomon reed-solomon reedsolomon forward error correction',
    install_requires=[
        'numpy'
    ],
    ext_modules = [reed_solomon]
)
