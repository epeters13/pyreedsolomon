# Original Author    : Edwin G. W. Peters @ epeters
#   Creation date    : Fri Jan 29 15:19:20 2021 (+1100)
#   Email            : edwin.g.w.petersatgmail.com
# ------------------------------------------------------------------------------
# Last-Updated       : Fri Feb  5 18:24:05 2021 (+1100)
#           By       : Edwin G. W. Peters @ epeters
# ------------------------------------------------------------------------------
# File Name          : setup.py
# Description        : 
# ------------------------------------------------------------------------------
# Copyright          : GPLV3
# ------------------------------------------------------------------------------


import setuptools
from git_helpers import check_git_submodules



# init the reed-solomon userspace kernel interface library
check_git_submodules()
    
# HACK we need to make the config.h file.  All our config parameters are provided already, so it can be empty
open('reed-solomon/src/config.h','a').close()


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
