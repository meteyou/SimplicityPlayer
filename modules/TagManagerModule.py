import json
import logging
import os


class TagManagerModule:
    def __init__(self, config):
        self._config = config
        self._tagsFilePath = config.get('TagManagerModule', 'tagsFilePath',
                                        fallback='../data/tags.json')

        self.tags = {}
        self.load_tags()

    def load_tags(self):
        try:
            with open(self._tagsFilePath, 'r') as tagsFile:
                self.tags = json.load(tagsFile)
        except (IOError, ValueError) as e:
            self.tags = {}
            logging.getLogger('sp').error(f'Unable to load tag file')
            logging.getLogger('sp').exception(e)

    def save_tags(self):
        with open(self._tagsFilePath, 'w') as tagsFile:
            json.dump(self.tags, tagsFile)

    def add_tag(self, tag, name):
        self.tags[tag] = name
        self.save_tags()

    def remove_tag(self, tag):
        del self.tags[tag]
        self.save_tags()

    def get_tags(self):
        return self.tags

    def get_tag(self, tag):
        return self.tags[tag]