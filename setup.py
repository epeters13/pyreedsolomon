# Original Author    : Edwin G. W. Peters @ epeters
#   Creation date    : Fri Jan 29 15:19:20 2021 (+1100)
#   Email            : edwin.peters@unsw.edu.au
# ------------------------------------------------------------------------------
# Last-Updated       : Fri Jan 29 16:13:59 2021 (+1100)
#           By       : Edwin G. W. Peters @ epeters
# ------------------------------------------------------------------------------
# File Name          : setup.py
# Description        : 
# ------------------------------------------------------------------------------
# Copyright          : Insert license
# ------------------------------------------------------------------------------


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='pyreedsolomon',
    version='1.0.2',
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
)
