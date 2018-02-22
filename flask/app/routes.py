from app import app
from flask import render_template, request


@app.route('/')
@app.route('/index')
def index():
    print('Hello world!')
    return render_template('index.html')

@app.route('/search')
def search():
	#Hacer peticion POST adjuntando url del usuario
	print(request.args["q"])
	return render_template('search.html')

@app.route('/resultado/<plataforma>/<usuario>')
def result(plataforma,usuario):
	print(plataforma + "-" + usuario)
	return render_template('result.html')