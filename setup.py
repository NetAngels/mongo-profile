#!/usr/bin/env python
# -*- coding: utf8 -*-
# See http://www.mongodb.org/display/DOCS/Database+Profiler
from distutils.core import setup

import os, sys
reload(sys).setdefaultencoding("UTF-8")

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        return ''

setup(
    name='mongo-profile',
    version='0.4.1',
    author='NetAngels',
    author_email='info@netangels.ru',
    py_modules=['mongoprofile',],
    url='http://github.com/NetAngels/mongo-profile',
    license = 'BSD License',
    description = u'MongoDB profile helper',
    long_description = read('README.rst'),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database',
    ),
)
