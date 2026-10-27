from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def accueil():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    confirmation = None
    if request.method == 'POST':
        nom = request.form['nom']
        confirmation = 'Merci {}, ton message a bien été reçu.'.format(nom)
    return render_template('contact.html', confirmation=confirmation)


if __name__ == '__main__':
    app.run(debug=True)
