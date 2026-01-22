from stacksprout import trace, visualize_tree

@trace
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

factorial(5)
visualize_tree(factorial)
