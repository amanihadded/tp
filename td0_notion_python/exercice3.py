def Deviner():
    n = int(input("donner n : "))
    d = int(input("donner d : "))

    r = n
    q = 0
    while r >= d:
        r = r - d
        q = q +1
    print("le reste est : ", r)
    print("le quotient est : ", q)

Deviner()