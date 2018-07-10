# -*- coding: utf-8 -*-

import salt.ext.six as six
import salt.state
import salt.utils.args

_keywords = salt.state.STATE_REQUISITE_KEYWORDS | \
            salt.state.STATE_REQUISITE_IN_KEYWORDS | \
            salt.state.STATE_RUNTIME_KEYWORDS | \
            {'name'}


def match_args(self, state):
    if state['state'] not in self.mods:
        self._logger('State module does not exist: %s', state['state'])
    if not hasattr(self.mods[state['state']], state['fun']):
        self._logger('State function does not exist: %s.%s', state['state'], state['fun'])
    args = salt.utils.args.get_function_argspec(getattr(self.mods[state['state']], state['fun']))
    if args.keywords is not None:
        return
    for arg in six.iterkeys(state):
        if arg not in args and arg not in _keywords:
            self._logger(
                'Arg not accepted by state %s.%s: %s',
                state['state'], state['fun'], arg,
            )
