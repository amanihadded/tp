# def factorial(n):
#     if n == 0:
#         return 1
#     else:
#         return n * factorial(n - 1) # Recursive call
# n = int(input("Enter a nonnegative integer: "))
# print("Factorial of", n, "is", factorial(n))

a = int(input("Enter a nombre négative a : "))
b= int(input("Enter a nombre négative b : "))

while a!=b:
    if a>b:
        a=a-b
    else:
        b=b-a
print("Le plus grand commun diviseur est : ", a)