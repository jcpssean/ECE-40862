import random

a = [random.randrange(100) for i in range(10)]
print(a)
n = int(input("Enter number: "))
b = [i for i in a if i < n]
print(f"The new list is {b}")