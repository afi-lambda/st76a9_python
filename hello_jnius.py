from __future__ import print_function
from jnius import autoclass

Stack = autoclass('java.util.Stack')
stack = Stack()
stack.push('hello')
stack.push('world')

print(stack.pop()) # --> 'world'
print(stack.pop()) # --> 'hello'
