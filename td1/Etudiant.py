# class Etudiant:
#     def __init__(self, nom, prenom, age):
#         self.nom = nom
#         self.prenom = prenom
#         self.age = age

#     def __str__(self):
#         return 'Nom: {}, Prénom: {}, Âge: {}'.format(self.nom, self.prenom, self.age)

# e1 = Etudiant('amani', 'hadded', 23)
# print(e1)


class Etudiant:
    def __init__(self, nom, id, inscritcours, fraisannuels):
        self.nom = nom
        self.id = id
        self.inscritcours = inscritcours
        self.fraisannuels = fraisannuels

    def __str__(self):
        return 'Nom : {}, id : {}, inscritCours : {}, fraisAnnuels : {}'.format(self.nom, self.id, self.inscritcours, self.fraisannuels)

    def __lt__(self, other):
        return self.fraisannuels < other.fraisannuels


class ArtsEtudiant(Etudiant):
    def __init__(self, nom, id, inscritcours, fraitsannuels, projet):
        super().__init__(nom, id, inscritcours, fraitsannuels )
        self.projet = projet

    def __str__(self):
        return super().__str__() + '\nProjet : {}'.format(self.projet)

class CommerceEtudiant(Etudiant):
    def __init__(self, nom, id, inscritcours, fraitsannuels, entreprisestage):
        super().__init__(nom, id, inscritcours, fraitsannuels )
        self.entreprisestage = entreprisestage

    def __str__(self):
        return super().__str__() + '\nStage : {}'.format(self.entreprisestage)

class TechEtudiant(Etudiant):
    def __init__(self, Nom, ID, InscritCours, FraisAnnuels, Projet, EntrepriseStage):
        super().__init__(Nom, ID, InscritCours, FraisAnnuels)
        self.projet = Projet
        self.entreprise_stage = EntrepriseStage

    def __str__(self):
        return super().__str__() + '\nProjet : {}\nStage : {}'.format(self.projet, self.entreprise_stage)

e1 = Etudiant('E1', 'Cours1', 'TC', 6000)
ae1 = ArtsEtudiant('Ahmed', 'A1', 'History', 8000, 'A')
ce1 = CommerceEtudiant('Sami', 'C3', 'Digital Marketing', 11400, 'Digital Consultancy')
te1 = TechEtudiant('Amira', 'T4', 'Computer Science', 15000, 'A', 'Computer Tech')

print(e1)
print()
print(ae1)
print()
print(ce1)
print()
print(te1)
print()
if te1 > ce1:
 print("Les frais annuels d'un étudiant en technique sont \
 plus élevés que ceux d'un étudiant de commerce.")
else:
 print("Les frais annuels d'un étudiant en technique sont \
 inférieurs à ceux d'un étudiant de commerce.")