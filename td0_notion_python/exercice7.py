# 1 -

def fibalt(n):
    old = 0
    new = 1
    for i in range(n):
        temp = new
        new = old + new
        old = temp

    return old
# print(fibalt(10)) 

# 2 -
def fib(n):
    if n == 0:
        return 0
    else:
        if n == 1:
            return 1
        else:
            return fib(n - 1) + fib(n - 2)
print(fib(10))