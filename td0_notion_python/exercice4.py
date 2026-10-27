n = int(input("Entrer les nombres des élèves: "))
nb = 0
s = 0

for i in range(n):
    nb+= 1
    print("saisir note d'etudiant n° :", nb , )
    note = float(input())
    s+= note

    if i == 0:
        min_note = note
        max_note = note
    else:
        if note < min_note:
            min_note = note
        if note > max_note:
            max_note = note

print("La moyenne des notes est: ", s/n)   
print("La note minimale est: ", min_note)
print("La note maximale est: ", max_note)