# -*- coding: utf-8 -*-


def test_bad_yaml_dict(self, state):
    this = self.rendered[state['__id__']]['.'.join([state['state'], state['fun']])]
    for dict_ in this:
        if len(dict_) > 1 and None in dict_.values():
            for key in dict_:
                self._logger('Dictionary values not indented enough: %s is None', key)
                return
