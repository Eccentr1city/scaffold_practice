import time
# File used for testing

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for fib_number in fibonacci(100):
    print(fib_number)
    time.sleep(0.1)
