import json
import logging


class StateManagerModule:
    def __init__(self, config):
        self._config = config
        self._statesFilePath = config.get('StateManagerModule', 'statesFilePath',
                                          fallback='data/states.json')

        self._current = {}
        self._states = {}
        self.load_states()

    def load_states(self):
        try:
            with open(self._statesFilePath, 'r') as statesFile:
                tmp = json.load(statesFile)
                self._current = tmp.get('current', {})
                self._states = tmp.get('states', {})
        except (IOError, ValueError) as e:
            self._current = {}
            self._states = {}
            logging.getLogger('sp').error(f'Unable to load state file')
            logging.getLogger('sp').exception(e)

    def save_states(self):
        with open(self._statesFilePath, 'w') as statesFile:
            json.dump({'current': self._current, 'states': self._states},
                      statesFile)

    def get_tag(self, file_name):
        if file_name in self._states:
            return self._states[file_name]

        return None
