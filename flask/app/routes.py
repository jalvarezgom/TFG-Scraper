from app import app
from flask import render_template, request, session, jsonify
import requests,json

from py2neo import Graph

graph = Graph("http://localhost:7474/db/data/")

@app.route('/')
@app.route('/index')
def index():
    #print('Hello world!')
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
		session['url']=url
		session['plataforma'] = plataforma
		session['usuario'] = url[-1]
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

@app.route('/result')
def result():
	nodes = []
	links = []
	print(session['plataforma'] + ' ' + session['usuario'])

	cypher = 'MATCH (user {user:"' +session['usuario']+ '"}) RETURN user.user,user.score'
	query = graph.data(cypher)
	nodes.append({'user': query[0].get("user.user"),'score':query[0].get("user.score")})

	cypher = 'MATCH (inicio:Graphmv_item {user:"' + session['usuario'] + '"})<-[:AMIGOS*1..2]-(fin:Graphmv_item) RETURN inicio.user,fin.user,fin.score'
	query = graph.run(cypher)
	#query = graph.run('MATCH (n)-[r]->(m) RETURN n.user,m.user,m.score;')
	#aux = query.data()
	
	for objList in query.data():
		nodes.append({'user': objList['fin.user'],'score':objList['fin.score']})
		links.append({'source':objList['inicio.user'],'target':objList['fin.user']})
		
	print(nodes)
	print(links)
	return render_template('result.html', data={'nodes':nodes,'links':links})





