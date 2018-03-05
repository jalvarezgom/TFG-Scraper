import scrapy
from ScrapySpider.mv_item import mv_item,Graphmv_item
from datetime import datetime, date, time, timedelta
from py2neo import Graph,authenticate

scrap_amigos=True
nivelbusqueda_profundidad = 0
#authenticate("localhost:7474", "neo4j", "my_password")
graph = Graph("http://localhost:7474/db/data/")

class mvSpider(scrapy.Spider):
    name = "mv"
    """allowed_domains=[
        'https://www.mediavida.com'
    ]"""
    start_urls = [
        'https://www.mediavida.com/id/xeven',
    ]
    def __init__(self, user=None, **kwargs):
        print("asdasdasd")
        print(user)

    def parse(self, response):
        global scrap_amigos,graph
        #item = mv_item() #Creamos item
        usuario = Graphmv_item()
        principal = True
        if 'item' in response.meta:
            principal = False

        #item['user']= response.static("div.user-info h1::text").extract_first() #Extraemos el usuario
        #item['url'] = response.url
        self.tratar_usuario(usuario,response)

        panelderecho = response.css("div.b-side")
        panelamigos = panelderecho[len(panelderecho)-2]
        #print (item)

        if principal:
            for amigo in panelamigos.css("ul.avatar-list li a::attr(href)").extract():
                # yield response.follow("https://www.mediavida.com"+ amigo, callback=self.parse)
                request = scrapy.Request("https://www.mediavida.com" + amigo, callback=self.parse)

                request.meta['item'] = usuario
                request.meta['profundidad'] = nivelbusqueda_profundidad-1
                yield request
        else:
            profundidad= response.meta['profundidad']
            usuario.amigos.add(response.meta['item'])
            if profundidad > 0:
                for amigo in panelamigos.css("ul.avatar-list li a::attr(href)").extract():
                    # yield response.follow("https://www.mediavida.com"+ amigo, callback=self.parse)
                    request = scrapy.Request("https://www.mediavida.com" + amigo, callback=self.parse)
                    request.meta['item'] = usuario
                    request.meta['profundidad'] = profundidad-1
                    yield request

        #usuario.amigos.add("hwki")
        #print(usuario)
        yield {'item':usuario}

    def calcular_puntacion(self,noticias,temas,mensajes,firmas,fecha):
        fecha_registro = datetime(int(fecha[5]), int(fecha[3].split("/")[1]), int(fecha[3].split("/")[0]))
        fecha_actual = datetime.now()
        puntuacion_user = noticias*10 + temas*5 + mensajes*1 + firmas*1 + (fecha_actual-fecha_registro).days*1
        return puntuacion_user

    def tratar_usuario (self,usuario,response):
        usuario.user = response.css("div.user-info h1::text").extract_first()  # Extraemos el usuario
        usuario.url = response.url

        valores = []
        for dato in response.css("div.hero-menu ul li"):
            valores.append(int(dato.css("a strong::attr(title)").extract_first().split(" ")[0]))
        # print(valores)
        fr_fecha = response.css("div.c-side ul.user-meta li span::attr(title)").extract_first().split(" ")

        # item['score'] = self.calcular_puntacion(valores[0],valores[1],valores[2],valores[3],fr_fecha)
        usuario.score = self.calcular_puntacion(valores[0], valores[1], valores[2], valores[3], fr_fecha)