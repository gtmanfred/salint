# -*- coding: utf-8 -*-

import salt.state
import salt.ext.six as six


def requisites_match(self, state):

    def _sls_test(sls):
        return key == sls['state'] and (value == sls['__id__'] or value == sls['name'])

    for req_word in salt.state.STATE_REQUISITE_KEYWORDS | salt.state.STATE_REQUISITE_IN_KEYWORDS:
        for req in state.get(req_word, []):
            if isinstance(req, six.string_types):
                if not any(filter(lambda sls: req == sls['__sls__'], self.lowstate)):
                    self._logger('Unable to find requisite: %s', req)
            elif isinstance(req, dict):
                key, value = next(six.iteritems(req))
                if not any(filter(_sls_test, self.lowstate)):
                    self._logger('Unable to find requisite: %s', dict(req))
            else:
                self._logger('Unrecognized requisite type: %s', type(req))
