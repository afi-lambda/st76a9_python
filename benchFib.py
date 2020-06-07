from __future__ import print_function
def benchFib(n):
    if n < 2:
        return 1
    else:
        return benchFib(n - 1) + benchFib(n - 2) + 1

print(benchFib(1))
print(benchFib(2))
print(benchFib(3))
print(benchFib(4))
print(benchFib(5))
