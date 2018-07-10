# -*- coding: utf-8 -*-
'''
Setup File for Salint
'''
from setuptools import setup
setup(
    name='salint',
    version='0.0.1',
    description='Linter for SaltStack States',
    url='https://github.com/gtmanfred/salint',
    author='Daniel Wallace',
    author_email='daniel@saltstack.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['salint', 'salint.rules'],
    entry_points={  # Optional
        'console_scripts': [
            'salint=salint.script:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/gtmanfred/salint/issues',
        'Source': 'https://github.com/gtmanfred/salint/',
    },
)

