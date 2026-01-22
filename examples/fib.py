from stacksprout import trace, visualize_tree

@trace
def fib(n):
    if n <= 1:
        return 1
    return fib(n-1) + fib(n-2)

fib(6)
visualize_tree(fib)
