"""

@author: Dylan
"""


class TestSuite(object):
    """
    classdocs
    """

    properties_list = []

    def __init__(self):
        self.properties = {}

    def set_testsuite_name(self, testsuite_name):
        self.testsuite_name = testsuite_name

    def set_tm_id(self, tm_id):
        self.tm_id = tm_id

    def get_testsuite_name(self):
        return self.testsuite_name

    def get_tm_id(self):
        return self.tm_id

    def add_property(self, prop, value):
        self.properties[prop] = value

    def get_property(self, prop):
        if prop in self.properties:
            value = self.properties[prop]
        else:
            value = None
        return value
