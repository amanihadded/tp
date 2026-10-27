a = float(input("Donner a: "))
b = float(input("Donner b: "))

if a!= 0:
    s = -b/a
else:
    if b == 0:
        s="Indéterminer"
    else:
        s=' impossible'
print ("lasolution est : ", s)