from flask import Flask, render_template, jsonify, Response
import xml.etree.ElementTree as ET
app = Flask(__name__)

tasks = ["test1", "test2", "test3"]
products = [
{"id": 1, "name": "Produit A", "price": 10.99},
{"id": 2, "name": "Produit B", "price": 24.99},
{"id": 3, "name": "Produit C", "price": 5.99}
]

@app.route('/')
def accueil():
    return render_template('index.html', \
    message='ceci est un message envoyé depuis le serveur Flask')


@app.route('/salut/<nom>')
def salut(nom):
    return render_template('salut.html', nom=nom)

@app.route('/index3')
def index3():
    return render_template('index3.html',
        message='ceci est un message recu depuis le serveur Flask')

@app.route('/tasks')
def task_list():
    return render_template('tasks.html', tasks=tasks)

@app.route('/products')
def get_products():
    return jsonify({"products" : products})

@app.route('/api/product-xml', methods=['GET'])
def get_products_xml():
    root = ET.Element('products')
    for product in products:
        item = ET.SubElement(root, 'product')
        ET.SubElement(item, 'id').text = str(product['id'])
        ET.SubElement(item, 'name').text = product['name']
        ET.SubElement(item, 'price').text = str(product['price'])
    return Response(ET.tostring(root), content_type='text/xml')


if __name__ == '__main__':
    app.run(debug=True)
