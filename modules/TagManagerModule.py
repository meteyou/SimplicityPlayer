import json
import logging
import os


class TagManagerModule:
    def __init__(self, config):
        self._config = config
        self._tagsFilePath = config.get('TagManagerModule', 'tagsFilePath',
                                        fallback='data/tags.json')

        self._tags = {}
        self.load_tags()

    def load_tags(self):
        # Create the file if it does not exist
        if not os.path.exists(self._tagsFilePath):
            self.save_tags()

        try:
            with open(self._tagsFilePath, 'r') as tagsFile:
                self._tags = json.load(tagsFile)
        except (IOError, ValueError) as e:
            self._tags = {}
            logging.getLogger('sp').error(f'Unable to load tag file')
            logging.getLogger('sp').exception(e)

    def save_tags(self):
        # Create the directory if it does not exist
        os.makedirs(os.path.dirname(self._tagsFilePath), exist_ok=True)

        with open(self._tagsFilePath, 'w') as tagsFile:
            json.dump(self._tags, tagsFile)

    def add_tag(self, tag, name):
        self._tags[str(tag)] = name
        self.save_tags()

    def remove_tag(self, tag):
        if tag in self._tags:
            del self._tags[tag]
            self.save_tags()

    def get_tags(self):
        return self._tags

    def get_tag(self, tag):
        if tag in self._tags:
            return self._tags[tag]

        return None
