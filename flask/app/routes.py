from app import app
from flask import render_template, request, session, jsonify
import requests,json


@app.route('/')
@app.route('/index')
def index():
    print('Hello world!')
    return render_template('index.html')

@app.route('/search')
def search():
	#Hacer peticion POST adjuntando url del usuario
	#parametros={'user': usuario}
	url=request.args["q"].split("/")
	plataforma = url[2].split(".")[1]
	if(plataforma=="mediavida"):
		r = requests.post('http://localhost:6800/schedule.json', data = {'project':'ScrapySpider','spider':'mv'})
		#r = requests.get('http://localhost:6800/listprojects.json')
	elif(plataforma=="facebook"):
		r = requests.get('http://httpbin.org/get', params={'user': url[-1]})
	elif(plataforma=="twitter"):
		r = requests.get('http://httpbin.org/get', params={'user': url[-1]})
	
	json= r.json()
	print(r.json())
	print(r.json()['status'])
	print(plataforma)

	if json['status']=="ok":
		session['plataforma'] = plataforma
		session['idSearch'] =json['jobid']
		
		return render_template('search.html')
	else:
		return render_template('searchError.html')

@app.route('/status')
def status():
	r = requests.get('http://localhost:6800/listjobs.json', params = {'project':'ScrapySpider'})
	print(r.json())
	if any(session['idSearch'] in s['id'] for s in r.json()['running']) or any(session['idSearch'] in s['id'] for s in r.json()['pending']):
		return jsonify(status='false')
	else:
		return jsonify(status='true')

@app.route('/resultado/<plataforma>/<usuario>')
def result(plataforma,usuario):
	print(plataforma + "-" + usuario)
	return render_template('result.html')





app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'