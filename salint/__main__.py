# -*- coding: utf-8 -*-
import os

import salint


opts = {
    'fileserver_backend': ['roots'],
    'extension_modules': './.lintcache/extmods',
    'file_client': 'local',
    'cachedir': './.lintcache/',
    'file_roots': {
        'base': [
            os.getcwd(),
        ],
    },
    'state_top': 'salt://top.sls',
    'state_auto_order': True,
    'fileserver_followsymlinks': True,
    'fileserver_ignoresymlinks': False,
    'id': 'local',
    'saltenv': 'base',
    'pillar_cache': False,
    'pillar_roots': {},
    'renderer_blacklist': [],
    'renderer_whitelist': [],
    'hash_type': 'sha256',
    'file_buffer_size': 262144,
    'renderer': 'yaml_jinja',
    'log_level': 'warning',
    'file_ignore_regex': [],
    'file_ignore_glob': [],
}
lint = salint.Linter(opts)
lint.lint_all()
