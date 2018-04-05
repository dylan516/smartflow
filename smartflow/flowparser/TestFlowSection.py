'''

@author: Dylan
'''


class TestFlowSection(object):
    def __init__(self, section_name):
        self.section_name = section_name
        self.asclines = []
        self.csvlines = []

    def add_ascline(self, line):
        self.asclines.append(line)

    def get_asclines(self):
        return self.asclines

    def add_csvline(self, line):
        self.csvlines.append(line)

    def syncup_asclines(self):
        self.asclines = []
        for line in self.csvlines:
            self.asclines.append(''.join(line))

    def update_line(self, param, value):
        value_index = self.csvlines.index(param) + 1
        self.csvlines[value_index] = value
        self.syncup_asclines()

    def __str__(self):
        return '\n'.join(self.asclines)
