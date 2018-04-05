'''

@author: Dylan
'''


class Testmethodparameter(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.parameters = []

    def set_tm_id(self, tm_id):
        self.tm_id = tm_id

    def get_tm_id(self):
        return self.tm_id

    def add_param(self, param, value):
        self.parameters.append(param)
        self.parameters.append(value)

    def get_param(self, param):
        if (param in self.parameters):
            value_index = self.parameters.index(param) + 1
            value = self.parameters[value_index]
        else:
            value = None
        return value

    def update_param(self, param, value):
        if (param in self.parameters):
            value_index = self.parameters.index(param) + 1
            self.parameters[value_index] = value
