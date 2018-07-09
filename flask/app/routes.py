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
	plataforma = url[2].split(".")[len(url[2].split("."))-2]
	print(url)
	print(plataforma)
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
	
	respjson= r.json()
	print(r.json())
	print(r.json()['status'])
	print(plataforma)

	if respjson['status']=="ok":
		session['url']=request.args["q"]
		session['usuario'] = url[-1]
		session['idSearch'] =respjson['jobid']
		
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
	session['url'] = "https://twitter.com/PeterDracon70"

	cypher = 'MATCH (userPr:GraphItem {url:"'+session['url']+'"})<-[:RELATION*0..2]-(inicio:GraphItem) RETURN toInteger(avg(toInteger(inicio.score))), count(inicio)'
	query = graph.run(cypher)
	dataMedia = query.data()
	print(dataMedia)
	print(dataMedia[0].get('toInteger(avg(toInteger(inicio.score)))'))
	print(dataMedia[0].get('count(inicio)'))
	media = dataMedia[0].get('toInteger(avg(toInteger(inicio.score)))')
	numTotal = dataMedia[0].get('count(inicio)')
	#Tratar resultado
	#1.MATCH (userPr:GraphItem {url:"'+session['url']+'"})<--(inicio:GraphItem) WHERE toInteger(inicio.score)>'+MEDIA+' RETURN userPr.user,userPr.score,inicio.user,inicio.score
	#2.MATCH (userPr:GraphItem {url:"'+session['url']+'"})<-[:RELATION*0..2]-(inicio:GraphItem)<--(fin:GraphItem) WHERE toInteger(inicio.score)>'+MEDIA+' AND toInteger(fin.score)>'+MEDIA+' RETURN inicio.user,fin.user,fin.score

	#1. MATCH (userPr:Graphmv_item {user:"Rumiin_GG"})<--(inicio:Graphmv_item) RETURN userPr.user,userPr.score,inicio.user,inicio.score
	#2. MATCH (userPr:Graphmv_item {user:"Rumiin_GG"})<-[:AMIGOS*0..2]-(inicio:Graphmv_item)<--(fin) RETURN inicio.user,fin.user.fin.score
	
	if(numTotal < 250):
		print("caso1")
		cypher = 'MATCH (userPr:GraphItem {url:"'+session['url']+'"})<--(inicio:GraphItem) RETURN userPr.user,userPr.score,inicio.user,inicio.score'
		query = graph.run(cypher)
		data1 = query.data()
		#print(data1)		

		print("caso2")
		cypher = 'MATCH (userPr:GraphItem {url:"'+session['url']+'"})<-[:RELATION*0..2]-(inicio:GraphItem)<--(fin:GraphItem) RETURN inicio.user,fin.user,fin.score'
		query = graph.run(cypher)
		data2 = query.data()
	else:
		#Filtrar resultado
		condicion = False
		mediaDiezPorciento = media*0.1
		opAum = False
		opDism = False
		while(not condicion):
			print("caso1")
			cypher = 'MATCH (userPr:GraphItem {url:"'+session['url']+'"})<--(inicio:GraphItem)  WHERE toInteger(inicio.score)>'+str(media)+' RETURN userPr.user,userPr.score,inicio.user,inicio.score'
			query = graph.run(cypher)
			data1 = query.data()

			print("caso2")
			cypher = 'MATCH (userPr:GraphItem {url:"'+session['url']+'"})<-[:RELATION*0..2]-(inicio:GraphItem)<--(fin:GraphItem) WHERE toInteger(inicio.score)>'+str(media)+' AND toInteger(fin.score)>'+str(media)+' RETURN inicio.user,fin.user,fin.score'
			query = graph.run(cypher)
			data2 = query.data()

			if ((len(data1)+len(data2)) >250 ):
				#Aumento la media
				if(opDism):
					media = media +mediaDiezPorciento/2
				else:
					media = media +mediaDiezPorciento
				opAum=True
			elif ((len(data1)+len(data2)) <200 and not opAum):
				#Disminuyo la media
				media = media - mediaDiezPorciento
				opDism=True
			else:
				condicion = True

			#print(len(data1))
			#print(len(data2))
	session['usuario'] = data1[0].get('userPr.user')	
	nodes.append({'user': data1[0].get('userPr.user'),'score':data1[0].get('userPr.score')})
	conjunto.add(data1[0].get('userPr.user'))
	for elem in data1:
		if (elem['inicio.user'] not in conjunto):
			nodes.append({'user': elem['inicio.user'],'score':elem['inicio.score']})
			conjunto.add(elem['inicio.user'])
		links.append({'source':elem['userPr.user'],'target':elem['inicio.user']})
	#print(data)
	for elem in data2:
		if (elem['fin.user'] not in conjunto):
			nodes.append({'user': elem['fin.user'],'score':elem['fin.score']})
			conjunto.add(elem['fin.user'])
		links.append({'source':elem['inicio.user'],'target':elem['fin.user']})
	
	session['listNodes'] =list(conjunto)
	return render_template('result.html', data={'nodes':nodes,'links':links,'media':media})

@app.route('/query')
def query():
	usuario = request.args["usuario"]
	nivel = request.args["nivel"]
	puntuacion = request.args["puntuacion"]
	data=""
	if (usuario == ""):
		usuario = session['usuario']
	if (nivel == ""):
		nivel = "2"
	if (puntuacion == ""):
		puntuacion = "0"

	if (usuario in session['listNodes']):
		cypher = 'MATCH (userPr:GraphItem {user:"'+usuario+'",plataforma:"'+session['plataforma']+'"})<-[:RELATION*0..'+nivel+']-(n:GraphItem) WHERE toInteger(n.score)>'+puntuacion+' RETURN n'
		query = graph.run(cypher)
		data = json.dumps(query.data())
		print(data)
	else:
		data = "Usuario introducido no encontrado en la consulta inicial"
	response = app.response_class(
		response=data,
		status=200,
		mimetype='application/json',
		headers={"Content-disposition":"attachment; filename=data.json"}
	)
	return response	
	



