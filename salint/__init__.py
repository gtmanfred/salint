# -*- coding: utf-8 -*-
import inspect
import logging
import os
import sys

import salt.loader
import salt.state
import salt.ext.six as six


log = logging.getLogger('testlog')
log_format = '%(statefile)-8s | %(stateid)s | %(statename)s | %(message)s'
date_format = '%H:%M:%S'
formatter = logging.Formatter(log_format, datefmt=date_format)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel('warning'.upper())
handler.setFormatter(formatter)
logging.root.addHandler(handler)


class Linter(object):
    def __init__(self, opts=None, pillar=None, grains=None):
        self.opts = opts or {}
        self.opts['pillar'] = pillar or {}
        self.opts['grains'] = grains or {}
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
        self.minion_mods= salt.loader.minion_mods(self.opts)
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
            __context__['retcode'] = 1
            return errors
        return st_.state.compile_high_data(high_)

    def _logger(self, message, *args):
        log.warning(message, *args, extra=self.info)

    @property
    def tests(self):
        return [
            test for _, test in inspect.getmembers(Linter, predicate=lambda meth: inspect.isfunction(meth) and meth.__name__.startswith('_test_case'))
        ]

    def _test_case_requisites_match(self, state):
        for req_word in salt.state.STATE_REQUISITE_KEYWORDS | salt.state.STATE_REQUISITE_IN_KEYWORDS:
            for req in state.get(req_word, []):
                if isinstance(req, six.string_types):
                    if not any(filter(lambda sls: req == sls['__sls__'], self.lowstate)):
                        self._logger('Unable to find requisite: %s', req)
                elif isinstance(req, dict):
                    key, value = next(six.iteritems(req))
                    if not any(filter(lambda sls: key == sls['state'] and (value == sls['__id__'] or value == sls['name']), self.lowstate)):
                        self._logger('Unable to find requisite: %s', dict(req))
                else:
                    self._logger('Unrecognized requisite type: %s', type(req))

    def _test_case_match_args(self, state):
        if state['state'] not in self.mods:
            self._logger('State module does not exist: %s', state['state'])
        if not hasattr(self.mods[state['state']], state['fun']):
            self._logger('State function does not exist: %s.%s', state['state'], state['fun'])
        args = salt.utils.args.get_function_argspec(getattr(self.mods[state['state']], state['fun']))
        for arg in six.iterkeys(state):
            if arg not in args and arg not in salt.state.STATE_REQUISITE_KEYWORDS | salt.state.STATE_REQUISITE_IN_KEYWORDS | salt.state.STATE_RUNTIME_KEYWORDS | {'name',}:
                self._logger('Arg not accepted by state %s.%s: %s', state['state'], state['fun'], arg)

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
