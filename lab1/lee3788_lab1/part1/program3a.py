n = int(input("How many Fibonacci numbers would you like to generate? "))
fib = []
a, b, i = 1, 1, 0
while i < n:
    fib.append(a)
    a, b = b, a + b
    i += 1
print("The Fibonacci Sequence is: " + ', '.join(map(str, fib)))
