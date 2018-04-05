"""

@author: Dylan
"""
from smartflow.flowparser.Utils import INITIAL_INTENT, INTENT

__all__ = ['Node', 'TestFlow', 'Flow_Node', 'Run_Node', 'Run_and_branch_Node',
           'MultiBin_Node', 'Group_Node', 'If_Node', 'Assignment_Node']


def intent_str(intent, node_str):
    lines = []
    for line in str(node_str).strip('\n').split('\n'):
        lines.append(intent + line + '\n')
    return ''.join(lines)


class Node(object):
    def __init__(self):
        self.intent = ''

    def set_intent(self, intent):
        self.intent = intent

    def add(self, node):
        node.set_intent(self.intent)
        self.node.add(node)
        return self


class TestFlow(Node):
    def __init__(self):
        super().__init__()
        self.intent = INITIAL_INTENT
        self.node = Flow_Node(self.intent)

    def __str__(self):
        node_str = '\n'
        node_str += intent_str('', str(self.node))
        return node_str


class Flow_Node(Node):
    def __init__(self, intent):
        super().__init__()
        self.intent = intent
        self.nodes = []

    def add(self, node):
        node.set_intent(self.intent)
        self.nodes.append(node)
        return self

    def __str__(self):
        node_str = ''
        for node in self.nodes:
            node_str += intent_str('', str(node))
        return node_str


class Run_Node(Node):
    def __init__(self, testsuite_name):
        super().__init__()
        self.testsuite_name = testsuite_name

    def __str__(self):
        node_str = intent_str(self.intent, 'run(%s);' % self.testsuite_name)
        return node_str


class Run_and_branch_Node(Node):
    def __init__(self, testsuite_name, then_node=None, else_node=None):
        super().__init__()

        self.then_branch = Flow_Node(self.intent + INTENT)
        self.else_branch = Flow_Node(self.intent + INTENT)
        self.testsuite_name = testsuite_name

        if then_node is not None:
            self.then_branch.add(then_node)

        if else_node is not None:
            self.else_branch.add(else_node)

    def __str__(self):
        node_str = ''

        node_str += intent_str(self.intent, 'run_and_branch(%s)\n' % self.testsuite_name)
        node_str += intent_str(self.intent, 'then\n')
        node_str += intent_str(self.intent, '{\n')

        if len(self.then_branch.nodes) > 0:
            node_str += intent_str(self.intent, self.then_branch)

        node_str += intent_str(self.intent, '}\n')
        node_str += intent_str(self.intent, 'else\n')
        node_str += intent_str(self.intent, '{\n')

        if len(self.else_branch.nodes) > 0:
            node_str += intent_str(self.intent, self.else_branch)

        node_str += self.intent + '}\n'
        return node_str


class MultiBin_Node(Node):
    def __init__(self):
        super().__init__()

    def __str__(self):
        node_str = ''
        node_str += intent_str(self.intent, 'multi_bin;\n')
        return node_str


class Group_Node(Node):
    def __init__(self, is_bypass, group_name, group_comment=''):
        super().__init__()

        self.group_name = group_name
        self.group_comment = group_comment
        self.groupbypass = ''
        if is_bypass:
            self.groupbypass = 'groupbypass,'
        self.group_branch = Flow_Node(self.intent + INTENT)

    def add(self, node):
        node.set_intent(self.group_branch.intent)
        self.group_branch.add(node)
        return self

    def __str__(self):
        node_str = ''
        node_str += intent_str(self.intent, '{\n')

        if len(self.group_branch.nodes) > 0:
            node_str += intent_str(self.intent, self.group_branch)

        line = '},%s open, "%s", "%s"' % (self.groupbypass, self.group_name, self.group_comment)
        node_str += intent_str(self.intent, line)

        return node_str


class If_Node(Node):
    def __init__(self, condition, then_node=None, else_node=None):
        super().__init__()

        self.condition = condition
        self.then_branch = Flow_Node(self.intent + INTENT)
        self.else_branch = Flow_Node(self.intent + INTENT)

        if then_node is not None:
            self.then_branch.add(then_node)

        if else_node is not None:
            self.else_branch.add(else_node)

    def __str__(self):
        node_str = ''
        node_str += intent_str(self.intent, 'if %s then\n' % self.condition)
        node_str += intent_str(self.intent, '{\n')

        if len(self.then_branch.nodes) > 0:
            node_str += intent_str(self.intent, self.then_branch)

        node_str += intent_str(self.intent, '}\n')
        node_str += intent_str(self.intent, 'else\n')
        node_str += intent_str(self.intent, '{\n')

        if len(self.else_branch.nodes) > 0:
            node_str += intent_str(self.intent, self.else_branch)

        node_str += self.intent + '}\n'
        return node_str


class Assignment_Node(Node):
    def __init__(self, variable, value):
        super().__init__()
        self.variable = variable
        self.value = value

    def __str__(self):
        node_str = intent_str(self.intent, '%s = %s;' % (self.variable, self.value))
        return node_str


class Char_Shmoo_on_fail_Node(Node):
    def __init__(self, testsuite_name):
        super().__init__()
        self.testsuite_name = testsuite_name

        self.testsuite = Flow_Node(self.intent)
        run_and_branch = Run_and_branch_Node(self.testsuite_name)
        run_and_branch.else_branch.add(Run_Node(self.testsuite_name + '_VMIN')) \
            .add(Run_Node(self.testsuite_name + '_FMAX')) \
            .add(Run_Node(self.testsuite_name + '_SHMOO'))
        self.testsuite.add(run_and_branch)

    def __str__(self):
        return intent_str(self.intent, str(self.testsuite))
