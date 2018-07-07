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
	elif(plataforma=="instagram"):
		r = requests.post('http://localhost:6800/schedule.json', data = {'project':'ScrapySpider','spider':'ig','user':request.args["q"]})
	elif(plataforma=="twitter"):
		r = requests.post('http://localhost:6800/schedule.json', data = {'project':'ScrapySpider','spider':'tw','user':request.args["q"]})
	elif(plataforma=="linkedin"):
		r = requests.post('http://localhost:6800/schedule.json', data = {'project':'ScrapySpider','spider':'lk','user':request.args["q"]})

	
	json= r.json()
	print(r.json())
	print(r.json()['status'])
	print(plataforma)

	if json['status']=="ok":
		session['url']=request.args["q"]
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
	conjunto = set()
	print(session['plataforma'] + ' ' + session['usuario'])

	#1. MATCH (userPr:Graphmv_item {user:"Rumiin_GG"})<--(inicio:Graphmv_item) RETURN userPr.user,userPr.score,inicio.user,inicio.score
	#2. MATCH (userPr:Graphmv_item {user:"Rumiin_GG"})<-[:AMIGOS*0..2]-(inicio:Graphmv_item)<--(fin) RETURN inicio.user,fin.user.fin.score
	print("caso1")
	cypher = 'MATCH (userPr:Graphmv_item {url:"'+session['url']+'"})<--(inicio:Graphmv_item) RETURN userPr.user,userPr.score,inicio.user,inicio.score'
	query = graph.run(cypher)
	data = query.data()
	print(data)
	nodes.append({'user': data[0].get('userPr.user'),'score':data[0].get('userPr.score')})
	conjunto.add(data[0].get('userPr.user'))
	for elem in data:
		nodes.append({'user': elem['inicio.user'],'score':elem['inicio.score']})
		links.append({'source':elem['userPr.user'],'target':elem['inicio.user']})
		conjunto.add(elem['inicio.user'])

	print("caso2")
	cypher = 'MATCH (userPr:Graphmv_item {url:"'+session['url']+'"})<-[:AMIGOS*0..2]-(inicio:Graphmv_item)<--(fin:Graphmv_item) RETURN inicio.user,fin.user,fin.score'
	query = graph.run(cypher)
	for elem in query.data():
		if (elem['fin.user'] not in conjunto):
			nodes.append({'user': elem['fin.user'],'score':elem['fin.score']})
			conjunto.add(elem['fin.user'])
		links.append({'source':elem['inicio.user'],'target':elem['fin.user']})
	
	return render_template('result.html', data={'nodes':nodes,'links':links})

@app.route('/query')
def status():
	print("query")
	



