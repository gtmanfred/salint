# -*- coding: utf-8 -*-
import inspect
import logging
import os
import pkg_resources
import sys

import salt.loader
import salt.state
import salt.ext.six as six

import salint.rules

if six.PY2:
    import imp

    def load_module(fullname, path):
        fp, pathname, description = imp.find_module(fullname, [path])
        return imp.load_module(fullname, fp, pathname, description)
else:
    import importlib

    def load_module(fullname, path):
        return importlib.machinery.PathFinder.find_module(fullname, [path]).load_module()

log_format = '%(statefile)s | %(stateid)s | %(statename)s | %(message)s'
date_format = '%H:%M:%S'
formatter = logging.Formatter(log_format, datefmt=date_format)

log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel('warning'.upper())
handler.setFormatter(formatter)
logging.root.addHandler(handler)


class Linter(object):
    def __init__(self, opts=None):
        self.opts = opts or {}
        self._load_modules()
        self._load_renderers()

    def _load_modules(self):
        dict(salt.loader.LazyLoader(
            salt.loader._module_dirs(self.opts, 'states', 'states'),
            self.opts,
            tag='lint',
            virtual_enable=False,
        ))
        self.mods = {}
        for module in filter(lambda mod: mod.startswith('salt.loaded.int.lint'), sys.modules):
            mod = sys.modules[module]
            self.mods[getattr(mod, '__virtualname__', module.split('.')[-1])] = mod
            for alias in getattr(mod, '__virtual_aliases__', []):
                self.mods[alias] = mod

    def _load_renderers(self):
        self.minion_mods = salt.loader.minion_mods(self.opts)
        self.renderers = salt.loader.render(
            self.opts,
            self.minion_mods,
        )

    def get_low(self, mods):
        st_ = salt.state.HighState(self.opts)

        if isinstance(mods, six.string_types):
            mods = mods.split(',')
        st_.push_active()
        try:
            high_, errors = st_.render_highstate({'base': mods})
        finally:
            st_.pop_active()
        errors = st_.state.verify_high(high_)
        if errors:
            return errors
        return st_.state.compile_high_data(high_)

    def _logger(self, message, *args, **kwargs):
        level = kwargs.pop('level', 'warning')
        getattr(log, level)(message, *args, extra=self.info)

    def _get_members(self, mod):
        return inspect.getmembers(mod, predicate=inspect.isfunction)

    @property
    def tests(self):
        for parent, _, rulefiles in os.walk(os.path.dirname(salint.rules.__file__)):
            for rulefile in rulefiles:
                if not rulefile.endswith('.py') or rulefile == '__init__.py':
                    continue
                for ret in self._get_members(load_module(rulefile[:-3], parent)):
                    yield ret[1]
        for rulefile in pkg_resources.iter_entry_points('salint.rules', name=None):
            for ret in self._get_members(rulefile.load()):
                yield ret[1]

    def render_state(self, path):
        return salt.template.compile_template(
            path,
            self.renderers,
            'jinja|yaml',
            self.opts['renderer_blacklist'],
            self.opts['renderer_whitelist'],
        )

    def lint_sls(self, sls):
        self.lowstate = self.get_low(sls)
        self.rendered = self.render_state(os.path.join(*sls.split('.')) + '.sls')

        for state in self.lowstate:
            if sls != state['__sls__']:
                continue
            self.info = {
                'stateid': state['__id__'],
                'statename': state['name'],
                'statefile': state['__sls__'] + '.sls',
            }
            for test in self.tests:
                test(self, state)

    def lint_all(self):
        for parent, _, statefiles in os.walk('.'):
            if parent.startswith('.') and parent not in ('.', '..'):
                continue
            for sls in statefiles:
                if sls.endswith('.sls'):
                    if parent == '.':
                        self.lint_sls(sls[:-4])
                    else:
                        self.lint_sls('.'.join([parent.replace(os.sep, '.'), sls[:-4]]))
