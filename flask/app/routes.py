from app import app
from flask import render_template, request, session, jsonify
import requests,json

from py2neo import Graph

graph = Graph("http://localhost:7474/db/data/")

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/search')
def search():
	#Hacer peticion POST adjuntando url del usuario
	url=request.args["q"].split("/")
	plataforma = url[2].split(".")[1]
	if(plataforma=="mediavida"):
		r = requests.post('http://localhost:6800/schedule.json', data = {'project':'ScrapySpider','spider':'mv','user':request.args["q"]})
		session['plataforma'] = "mv"
	elif(plataforma=="instagram"):
		r = requests.post('http://localhost:6800/schedule.json', data = {'project':'ScrapySpider','spider':'ig','user':request.args["q"]})
		session['plataforma'] = "ig"
	elif(plataforma=="twitter"):
		r = requests.post('http://localhost:6800/schedule.json', data = {'project':'ScrapySpider','spider':'tw','user':request.args["q"]})
		session['plataforma'] = "tw"
	elif(plataforma=="linkedin"):
		r = requests.post('http://localhost:6800/schedule.json', data = {'project':'ScrapySpider','spider':'lk','user':request.args["q"]})
		session['plataforma'] = "lk"
	
	json= r.json()
	print(r.json())
	print(r.json()['status'])
	print(plataforma)

	if json['status']=="ok":
		session['url']=request.args["q"]
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
	conjunto = set()
	print(session['plataforma'] + ' ' + session['usuario'])

	#1. MATCH (userPr:Graphmv_item {user:"Rumiin_GG"})<--(inicio:Graphmv_item) RETURN userPr.user,userPr.score,inicio.user,inicio.score
	#2. MATCH (userPr:Graphmv_item {user:"Rumiin_GG"})<-[:AMIGOS*0..2]-(inicio:Graphmv_item)<--(fin) RETURN inicio.user,fin.user.fin.score
	print("caso1")
	cypher = 'MATCH (userPr {url:"'+session['url']+'"})<--(inicio) RETURN userPr.user,userPr.score,inicio.user,inicio.score'
	query = graph.run(cypher)
	data = query.data()

	nodes.append({'user': data[0].get('userPr.user'),'score':data[0].get('userPr.score')})
	conjunto.add(data[0].get('userPr.user'))
	for elem in data:
		if (elem['inicio.user'] not in conjunto):
			nodes.append({'user': elem['inicio.user'],'score':elem['inicio.score']})
			conjunto.add(elem['inicio.user'])
		links.append({'source':elem['userPr.user'],'target':elem['inicio.user']})
		

	print("caso2")
	cypher = 'MATCH (userPr:GraphItem {url:"'+session['url']+'"})<-[:AMIGOS*0..2]-(inicio:GraphItem)<--(fin:GraphItem) RETURN inicio.user,fin.user,fin.score'
	query = graph.run(cypher)
	for elem in query.data():
		if (elem['fin.user'] not in conjunto):
			nodes.append({'user': elem['fin.user'],'score':elem['fin.score']})
			conjunto.add(elem['fin.user'])
		links.append({'source':elem['inicio.user'],'target':elem['fin.user']})
	
	session['listNodes'] =list(conjunto)
	return render_template('result.html', data={'nodes':nodes,'links':links})

@app.route('/query')
def query():
	usuario = request.args["usuario"]
	nivel = request.args["nivel"]
	puntuacion = request.args["puntuacion"]
	usuario = "xeven"
	nivel = "2"
	puntuacion = "4400"
	aux = '1,2,3\n4,5,6\n'

	cypher = 'MATCH (userPr:GraphItem {user:"'+usuario+'",plataforma:"'+"mv"+'"})<-[:RELATION*0..'+nivel+']-(n:GraphItem) WHERE toInteger(n.score)>'+puntuacion+' RETURN n'
	query = graph.run(cypher)
	data = json.dumps(query.data())
	print(data)
	response = app.response_class(
		response=data,
		status=200,
		mimetype='application/json',
		headers={"Content-disposition":"attachment; filename=data.json"}
	)
	return response	
	



