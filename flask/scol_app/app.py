import os
from datetime import date
from decimal import Decimal

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from passlib.hash import pbkdf2_sha256
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_babel import Babel
from flask_admin.theme import Bootstrap4Theme
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/scol'
app.config['SECRET_KEY'] = 'a8F3kL9xQ2vN7mR5pT1wZ6cD4hJ0sB8y'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Flask-Uploads : repertoire de telechargement des photos ----------------
# Le chemin est construit a partir de app.root_path pour que l'application
# fonctionne quel que soit le dossier depuis lequel elle est lancee.
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(app.root_path, 'static', 'image')
os.makedirs(app.config['UPLOADED_PHOTOS_DEST'], exist_ok=True)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Classe(db.Model):
    __tablename__ = 'classe'

    CodClass = db.Column(db.String(10), primary_key=True)
    NomClass = db.Column(db.String(50), nullable=False)
    NbrEtud = db.Column(db.Integer, default=0)

    etudiants = db.relationship("Etudiant", back_populates="classe",
                                cascade="all, delete-orphan")


class Etudiant(db.Model):
    __tablename__ = 'etudiant'

    NCE = db.Column(db.String(10), primary_key=True)
    Nom = db.Column(db.String(50), nullable=False)
    Prenom = db.Column(db.String(50), nullable=False)
    DateNais = db.Column(db.Date)
    LieuNais = db.Column(db.String(50))
    photo = db.Column(db.String(255))
    CodClass = db.Column(
        db.String(10),
        db.ForeignKey('classe.CodClass', onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )

    classe = db.relationship("Classe", back_populates="etudiants")
    absences = db.relationship("Absence", back_populates="etudiant",
                               cascade="all, delete-orphan")


class Matiere(db.Model):
    __tablename__ = 'matiere'

    CodMat = db.Column(db.String(15), primary_key=True)
    IntMat = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)

    absences = db.relationship("Absence", back_populates="matiere",
                               cascade="all, delete-orphan")


class Absence(db.Model):
    __tablename__ = 'absence'

    CodMat = db.Column(
        db.String(15),
        db.ForeignKey('matiere.CodMat', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True
    )
    NCE = db.Column(
        db.String(10),
        db.ForeignKey('etudiant.NCE', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True
    )
    DateA = db.Column(db.Date, primary_key=True)
    NHA = db.Column(db.Numeric(4, 2), nullable=False)

    matiere = db.relationship("Matiere", back_populates="absences")
    etudiant = db.relationship("Etudiant", back_populates="absences")

class UserForm(FlaskForm):
    username = StringField("Nom d'utilisateur",
                           validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe",
                             validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Ajouter")


class AbsenceForm(FlaskForm):
    nce = StringField("Numéro Carte Étudiant (NCE)",
                      validators=[DataRequired(), Length(max=10)])
    submit = SubmitField("Afficher les absences")

class UserAdmin(ModelView):
    form = UserForm
    page_size = 5
    can_set_page_size = True
    column_exclude_list = ['password']

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = pbkdf2_sha256.hash(form.password.data)


babel = Babel(app)

admin = Admin(app, name='Admin', theme=Bootstrap4Theme(), index_view=AdminIndexView(name='Admin panel'))

admin.add_view(UserAdmin(User, db.session))
admin.add_view(ModelView(Classe, db.session))
admin.add_view(ModelView(Etudiant, db.session))
admin.add_view(ModelView(Matiere, db.session))
admin.add_view(ModelView(Absence, db.session))

db.create_all()

@app.route('/users')
def liste_users():
    users = User.query.order_by(User.username).all()
    return render_template('liste_users.html', users=users)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = UserForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Ce nom d'utilisateur existe déjà.", "danger")

        elif User.query.filter_by(email=form.email.data).first():
            flash("Cet email est déjà enregistré.", "danger")

        else:
            nouvel_user = User(
                username=form.username.data,
                email=form.email.data,
                password=pbkdf2_sha256.hash(form.password.data)
            )

            db.session.add(nouvel_user)
            db.session.commit()

            flash(f"Utilisateur {nouvel_user.username} ajouté.", "success")
            return redirect(url_for('liste_users'))

    return render_template('add_user.html', form=form)


@app.route('/absences', methods=['GET', 'POST'])
def absences_etudiant():
    form = AbsenceForm()
    etudiant = None
    absences = []

    if form.validate_on_submit():
        etudiant = Etudiant.query.filter_by(NCE=form.nce.data).first()

        if etudiant is None:
            flash("Aucun étudiant ne correspond à ce NCE.", "danger")
        else:
            absences = sorted(etudiant.absences, key=lambda a: a.DateA)

    return render_template('absece_Etudiant.html',
                           form=form, etudiant=etudiant, absences=absences)


# --- Outil de calcul des NHA -------------------------------------------------
# Le NHA est note au format heures.minutes (1.45 = 1 h 45), pas en decimal :
# 1.45 + 3.30 doit donner 5.15 (et non 4.75). On additionne donc en minutes.
def somme_nha(valeurs):
    total_minutes = 0

    for v in valeurs:
        heures = int(v)
        minutes = int(round((float(v) - heures) * 100))
        total_minutes += heures * 60 + minutes

    return f"{total_minutes // 60}.{total_minutes % 60:02d}"


# --- Question 1 : classe la plus nombreuse + mise a jour de NbrEtud ----------
@app.route('/classe-max')
def classe_max():
    # On compte les lignes de la table Etudiant (jamais Classe.NbrEtud).
    resultat = (db.session.query(Etudiant.CodClass,
                                 func.count(Etudiant.NCE).label('nb'))
                .group_by(Etudiant.CodClass)
                .order_by(func.count(Etudiant.NCE).desc())
                .first())

    if resultat is None:
        flash("Aucun etudiant enregistre.", "danger")
        return render_template('classe_max.html', classe=None, nb=0)

    cod_class, nb = resultat

    # Mise a jour de la colonne NbrEtud de cette classe precise.
    classe = db.session.get(Classe, cod_class)
    classe.NbrEtud = nb
    db.session.commit()

    return render_template('classe_max.html', classe=classe, nb=nb)


# --- Question 2 : total des absences par module pour un etudiant ------------
@app.route('/absences/<string:nce_id>')
def totAbsece_Etudiant(nce_id):
    etudiant = Etudiant.query.get_or_404(nce_id)

    # Requete Flask-SQLAlchemy : un regroupement par module pour cet etudiant.
    groupes = (db.session.query(Absence.CodMat,
                                func.sum(Absence.NHA).label('total'))
               .filter(Absence.NCE == nce_id)
               .group_by(Absence.CodMat)
               .order_by(func.sum(Absence.NHA).desc())
               .all())

    # La somme SQL etant decimale, on la recalcule en base 60 (cf. somme_nha).
    totaux = []
    for cod_mat, _ in groupes:
        nha = [v for (v,) in db.session.query(Absence.NHA)
               .filter(Absence.NCE == nce_id, Absence.CodMat == cod_mat)]
        totaux.append((cod_mat, somme_nha(nha)))

    return render_template('totAbsece_Etudiant.html',
                           etudiant=etudiant, totaux=totaux)


# --- Question 3 : les 3 modules les plus absentes, toutes classes ------------
@app.route('/top-absences')
def top_absences():
    top = (db.session.query(Matiere.CodMat, Matiere.IntMat,
                            func.sum(Absence.NHA).label('total'))
           .join(Absence, Matiere.CodMat == Absence.CodMat)
           .group_by(Matiere.CodMat, Matiere.IntMat)
           .order_by(func.sum(Absence.NHA).desc())
           .limit(3)
           .all())

    resultats = []
    for cod_mat, int_mat, _ in top:
        nha = [v for (v,) in db.session.query(Absence.NHA)
               .filter(Absence.CodMat == cod_mat)]
        resultats.append((cod_mat, int_mat, somme_nha(nha)))

    return render_template('top_absences.html', resultats=resultats)


# --- Jeu de donnees d'exemple ------------------------------------------------
@app.route('/seed')
def seed():
    if Classe.query.first() is not None:
        flash("Le jeu de donnees est deja charge.", "danger")
        return redirect(url_for('classe_max'))

    db.session.add_all([
        Classe(CodClass='IngTA2-D', NomClass='IngTA2-D', NbrEtud=0),
        Classe(CodClass='IngTA2-A', NomClass='IngTA2-A', NbrEtud=0),
    ])

    db.session.add_all([
        Matiere(CodMat='ThGraphe', IntMat='Theorie des graphes',
                Description='Graphes, parcours et plus courts chemins'),
        Matiere(CodMat='ProgWebPyt', IntMat='Programmation Web avec Python',
                Description='Flask, SQLAlchemy et Jinja2'),
        Matiere(CodMat='BasDon', IntMat='Bases de donnees',
                Description='Modele relationnel et SQL'),
        Matiere(CodMat='RezInfo', IntMat='Reseaux informatiques',
                Description='Modele OSI et TCP/IP'),
    ])
    db.session.flush()

    db.session.add_all([
        Etudiant(NCE='E1', Nom='Ben Foulen', Prenom='Foulen',
                 DateNais=date(2004, 5, 12), LieuNais='Tunis',
                 CodClass='IngTA2-D'),
        Etudiant(NCE='E2', Nom='Trabelsi', Prenom='Ahmed',
                 DateNais=date(2004, 2, 3), LieuNais='Sousse',
                 CodClass='IngTA2-D'),
        Etudiant(NCE='E3', Nom='Gharbi', Prenom='Salma',
                 DateNais=date(2005, 9, 21), LieuNais='Sfax',
                 CodClass='IngTA2-D'),
        Etudiant(NCE='E4', Nom='Mansour', Prenom='Yassine',
                 DateNais=date(2004, 11, 7), LieuNais='Bizerte',
                 CodClass='IngTA2-A'),
    ])
    db.session.flush()

    db.session.add_all([
        # Les cinq absences de l'enonce pour E1.
        Absence(NCE='E1', CodMat='ThGraphe',
                DateA=date(2025, 12, 20), NHA=Decimal('1.45')),
        Absence(NCE='E1', CodMat='ThGraphe',
                DateA=date(2025, 12, 27), NHA=Decimal('3.30')),
        Absence(NCE='E1', CodMat='ProgWebPyt',
                DateA=date(2025, 12, 20), NHA=Decimal('1.45')),
        Absence(NCE='E1', CodMat='ProgWebPyt',
                DateA=date(2025, 12, 27), NHA=Decimal('1.45')),
        Absence(NCE='E1', CodMat='ProgWebPyt',
                DateA=date(2026, 1, 3), NHA=Decimal('1.45')),
        # Quelques absences supplementaires pour le classement /top-absences.
        Absence(NCE='E2', CodMat='BasDon',
                DateA=date(2025, 12, 20), NHA=Decimal('3.30')),
        Absence(NCE='E2', CodMat='BasDon',
                DateA=date(2026, 1, 10), NHA=Decimal('1.45')),
        Absence(NCE='E2', CodMat='ProgWebPyt',
                DateA=date(2025, 12, 27), NHA=Decimal('3.30')),
        Absence(NCE='E3', CodMat='ThGraphe',
                DateA=date(2026, 1, 3), NHA=Decimal('1.45')),
        Absence(NCE='E3', CodMat='ProgWebPyt',
                DateA=date(2026, 1, 10), NHA=Decimal('3.30')),
        Absence(NCE='E4', CodMat='RezInfo',
                DateA=date(2025, 12, 20), NHA=Decimal('1.45')),
        Absence(NCE='E4', CodMat='RezInfo',
                DateA=date(2026, 1, 3), NHA=Decimal('1.45')),
    ])

    db.session.commit()

    flash("Jeu de donnees charge : 2 classes, 4 matieres, 4 etudiants, "
          "12 absences.", "success")
    return redirect(url_for('classe_max'))


# --- Gestion des photos ------------------------------------------------------
def allowed_image(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def supprimer_photo(nom_fichier):
    # Evite de laisser des images orphelines dans static/image.
    if not nom_fichier:
        return

    chemin = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], nom_fichier)
    if os.path.exists(chemin):
        os.remove(chemin)


# --- Liste des etudiants -----------------------------------------------------
@app.route('/students')
def students():
    etudiants = Etudiant.query.order_by(Etudiant.NCE).all()
    return render_template('students.html', etudiants=etudiants)


# --- Ajout d'un etudiant avec sa photo ---------------------------------------
@app.route('/addStudent/', methods=['GET', 'POST'])
def addStudent():
    if request.method == 'POST':
        try:
            form = request.form
            nce = form['nce'].strip()
            nom = form['nom'].strip()
            prenom = form['prenom'].strip()
            date_nais = form['date_nais']
            lieu_nais = form['lieu_nais'].strip()
            cod_class = form['cod_class']
            photo = request.files.get('photo')

            # Les controles sont faits avant d'ecrire le fichier, pour ne pas
            # laisser d'image orpheline si l'ajout est finalement refuse.
            if photo and photo.filename and not allowed_image(photo.filename):
                flash('File type not allowed.', 'danger')
            elif not nce or not nom or not prenom:
                flash('Field(s) cannot be empty.', 'danger')
            elif db.session.get(Etudiant, nce) is not None:
                flash(f"L'etudiant {nce} existe deja.", 'danger')
            else:
                # Enregistrement de l'image avec Flask-Uploads.
                photo_name = photos.save(photo) if photo and photo.filename else ''

                etudiant = Etudiant(
                    NCE=nce,
                    Nom=nom,
                    Prenom=prenom,
                    DateNais=date.fromisoformat(date_nais) if date_nais else None,
                    LieuNais=lieu_nais or None,
                    CodClass=cod_class,
                    photo=photo_name or None
                )

                db.session.add(etudiant)
                db.session.commit()

                flash('Student added successfully', 'success')
                return redirect(url_for('students'))

        except UploadNotAllowed:
            flash('Upload not allowed.', 'danger')

        except Exception as e:
            db.session.rollback()
            flash(f'Failed operation: {str(e)}', 'danger')

    classes = Classe.query.order_by(Classe.NomClass).all()
    return render_template('addStudent.html', classes=classes)


# --- Edition d'un etudiant et de sa photo ------------------------------------
@app.route('/editStudent/<string:student_nce>', methods=['GET', 'POST'])
def editStudent(student_nce):
    etudiant = db.session.get(Etudiant, student_nce)

    if etudiant is None:
        flash('Student not found', 'danger')
        return redirect(url_for('students'))

    if request.method == 'POST':
        try:
            form = request.form
            etudiant.Nom = form['nom'].strip()
            etudiant.Prenom = form['prenom'].strip()
            etudiant.LieuNais = form['lieu_nais'].strip() or None
            etudiant.CodClass = form['cod_class']

            date_nais = form['date_nais']
            etudiant.DateNais = date.fromisoformat(date_nais) if date_nais else None

            photo = request.files.get('photo')

            # Verification de l'extension avant toute ecriture : si le fichier
            # est refuse, aucune modification n'est enregistree.
            if photo and photo.filename and not allowed_image(photo.filename):
                db.session.rollback()
                flash('File type not allowed.', 'danger')
            else:
                if photo and photo.filename:
                    ancienne_photo = etudiant.photo
                    etudiant.photo = photos.save(photo)
                    supprimer_photo(ancienne_photo)
                # Sinon, aucune photo envoyee : l'ancienne est conservee.

                db.session.commit()

                flash('Student information updated successfully', 'success')
                return redirect(url_for('students'))

        except UploadNotAllowed:
            flash('Upload not allowed.', 'danger')

        except Exception as e:
            db.session.rollback()
            flash(f'Failed operation: {str(e)}', 'danger')

    classes = Classe.query.order_by(Classe.NomClass).all()
    return render_template('editStudent.html', etudiant=etudiant, classes=classes)


# --- Suppression d'un etudiant -----------------------------------------------
@app.route('/deleteStudent/<string:student_nce>')
def deleteStudent(student_nce):
    etudiant = db.session.get(Etudiant, student_nce)

    if etudiant is None:
        flash('Student not found', 'danger')
        return redirect(url_for('students'))

    try:
        ancienne_photo = etudiant.photo

        db.session.delete(etudiant)
        db.session.commit()

        supprimer_photo(ancienne_photo)
        flash('Student deleted successfully', 'success')

    except IntegrityError:
        db.session.rollback()
        flash('Cannot delete the student. It is linked to other records.',
              'danger')

    return redirect(url_for('students'))


# --- Menu de l'administrateur -----------------------------------------------
admin.add_link(MenuLink(name='Liste des etudiants',
                        url='/students', category='Etudiants'))
admin.add_link(MenuLink(name='Ajouter un etudiant',
                        url='/addStudent/', category='Etudiants'))
admin.add_link(MenuLink(name='Classe la plus nombreuse',
                        url='/classe-max', category='Statistiques'))
admin.add_link(MenuLink(name='Absences par etudiant',
                        url='/absences', category='Statistiques'))
admin.add_link(MenuLink(name='Top 3 des absences',
                        url='/top-absences', category='Statistiques'))
admin.add_link(MenuLink(name='Charger le jeu de donnees',
                        url='/seed', category='Statistiques'))


if __name__ == '__main__':
    app.run(debug=True)
