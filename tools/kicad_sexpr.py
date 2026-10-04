"""Small read-only S-expression reader for library validation and test fixtures."""

import json
import re


def parse(text):
    stack = [[]]
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == '(':
            node = []
            stack[-1].append(node)
            stack.append(node)
        elif token == ')':
            if len(stack) == 1:
                raise ValueError('Unexpected closing parenthesis')
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if len(stack) != 1 or len(stack[0]) != 1:
        raise ValueError('Unbalanced or multiple root expressions')
    return stack[0][0]


def children(node, key):
    return [item for item in node if isinstance(item, list) and item and item[0] == key]


def child(node, key):
    return next(iter(children(node, key)), None)


def properties(node):
    return {p[1]: p[2] for p in children(node, 'property')}
