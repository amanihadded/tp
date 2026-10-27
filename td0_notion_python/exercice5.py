n = int(input("enter un numbre: "))
nb = 0
for i in range(n):
    if (n% 2 == 0 and i%2 == 0):
        nb+=1
        print(i, 'est la diviseur paire de : ', n) 
if (nb == 0):
    print('il n y a pas de diviseur paire de : ', n)
