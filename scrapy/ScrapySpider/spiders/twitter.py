import scrapy,pickle,time,logging
import ScrapySpider.constantes as cons
from ScrapySpider.mv_item import GraphItem
from py2neo import Graph
#from pkg_resources import resource_string,resource_stream,resource_listdir
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options




nivelbusqueda_profundidad = 2

class twSpider(scrapy.Spider):
	name = "tw"
	#login_page="https://mobile.twitter.com/login"
	target_page = None
	header = {
	    "accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	    "accept-encoding" : "gzip, deflate, sdch, br",
	    "accept-language" : "en-US,en;q=0.8,ms;q=0.6",
	    "user-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
	}
	driver = None
	logger = None

	def __init__(self, user=None, **kwargs):
		#Inicializar target_page con la url objetivo
		self.setLoggersLevel()
		self.logger.info("[SPIDER] - Red Social Twitter")
		self.target_page = "https://twitter.com/Rumiin_GG"
		options = Options()
		#options.set_headless(headless=True)
		self.driver = webdriver.Firefox(firefox_options=options)

	def closed(self, reason):
		self.driver.quit()
		self.logger.info("[SPIDER] - Cerrar navegador")
		self.logger.info("[SPIDER] - Tarea del Spider finalizada")

	def start_requests(self):
		self.driver.get(cons.urlLoginTW)
		"""
		logging.info("file_string1")
		file_string = resource_listdir(
			__name__, 
			"",
		)
		logging.info(file_string)
		logging.info("file_string2")
		file_string = resource_listdir(
			"ScrapySpider", 
			"",
		)
		logging.info(file_string)
		"""
		cookies = Path(cons.cookiesTW)
		if not cookies.is_file():
			self.loginCookies()
		try:
			self.load_cookie(self.driver,cons.cookiesTW)
		except:
			self.logger.warning("[SPIDER] WARNING - Error en carga de cookies")
			pass
		self.driver.refresh()
		return 	[scrapy.Request(url=self.driver.current_url, headers=self.header, callback=self.login)]
		
	def login(self,response):
		logging.info("[SPIDER] - Login TW")
		if(self.driver.current_url == "https://twitter.com/"):
			#Spider logeado
			return 	[scrapy.Request(url=self.target_page, headers=self.header, callback=self.parse)]
		else:
			#Cookies caducadas
			self.logger.warning('[SPIDER] - Cookies Invalidas')
			self.loginCookies()

	def loginCookies(self):
		self.logger.info("[SPIDER] - Generacion CookiesTW")
		time.sleep(1)
		username = self.driver.find_element_by_xpath("//div[@class='clearfix field'][1]//input")
		password = self.driver.find_element_by_xpath("//div[@class='clearfix field'][2]//input")
		username.send_keys(cons.userTW)
		password.send_keys(cons.passTW)
		self.driver.find_element_by_xpath("//div[@class='clearfix']//button").click()
		time.sleep(1) #Tiempo necesario para que procese el 'login'
		#self.driver.get(self.login_page)
		if(self.driver.current_url == "https://twitter.com/"):
			try:
				self.save_cookie(self.driver,cons.cookiesTW)
			except:
				self.logger.warning("[SPIDER] WARNING - Error en guardado de cookies")
				pass
			return 	[scrapy.Request(url=self.target_page, headers=self.header, callback=self.parse)]
		else:
			self.logger.several("[SPIDER] SEVERAL - ERROR GENERANDO COOKIESIG LOGIN")


	def parse(self, response):
		self.logger.info('[SPIDER] - Parseando usuario objetivo: '+response.url)
		global nivelbusqueda_profundidad
		usuario = GraphItem()

		#Perfil de Inicio
		usuario.user = response.xpath("//div[@class='ProfileHeaderCard']//h2//a//span//b/text()").extract_first()
		usuario.url = response.url
		usuario.score = response.xpath("//li[@class='ProfileNav-item ProfileNav-item--followers']//a//span[@class='ProfileNav-value']/@data-count").extract_first()
		self.logger.info("Puntuacion: "+usuario.score)
		usuario.plataforma = "tw"

		#Listado de seguidos
		listFollowing = self.parseFollowing(response,usuario,nivelbusqueda_profundidad,response.url+"/following")
		for followingRequest in listFollowing:
			yield followingRequest

		yield {'item':usuario} 
		
	def parseFriend(self,response):
		self.logger.info('[SPIDER] - Parseando usuario relacionado '+response.url)
		usuario = GraphItem()
		
		#Perfil de Inicio
		usuario.user = response.xpath("//div[@class='ProfileHeaderCard']//h2//a//span//b/text()").extract_first()
		usuario.url = response.url
		usuario.score = response.xpath("//li[@class='ProfileNav-item ProfileNav-item--followers']//a//span[@class='ProfileNav-value']/@data-count").extract_first()
		self.logger.info("Puntuacion: "+usuario.score)
		usuario.relation.add(response.meta['item'])
		usuario.plataforma = "tw"

		try:
			if(response.meta['profundidad']>0):
				listFollowing = self.parseFollowing(response,usuario,response.meta['profundidad'],response.url+"/following")
				for followingRequest in listFollowing:
					yield followingRequest
		except:
			self.logger.warning("[SPIDER] - Error controlado parseando 'parseFriend'")
			pass
			
		yield {'item':usuario}

	def parseFollowing(self,response,usuario,profundidad,url):
		listRequest = []
		numSeguidores = response.xpath("//li[@class='ProfileNav-item ProfileNav-item--following']//a//span[@class='ProfileNav-value']/text()").extract_first()
		# Carga por scroll: 3 Divs con 6 elementos cada uno
		divsScroll = 3
		elemsPorDiv = 6
		numElemsScroll = int(numSeguidores)/(divsScroll * elemsPorDiv)

		self.driver.get(url)
		for x in range(int(numElemsScroll)):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(0.5)

		try:
			for x in range((int(numElemsScroll))*3):
				self.logger.debug("[SPIDER] - Extrayendo información de Div - "+str(x+1))
				for y in range(6):
					followingLink = self.driver.find_element_by_xpath("//div[@class='GridTimeline-items has-items']//div[@class='Grid Grid--withGutter']["+str(x+1)+"]//div[@class='Grid-cell u-size1of2 u-lg-size1of3 u-mb10']["+str(y+1)+"]//div//div//a")
					request = scrapy.Request(followingLink.get_attribute("href"), callback=self.parseFriend, headers=self.header)
					request.meta['item'] = usuario
					request.meta['profundidad'] = profundidad-1
					listRequest.append(request)
		except:
			self.logger.warning("[SPIDER] WARNING - Error controlado parseando 'parseFollowing'")
			pass

		return listRequest

	def tratar_usuario (self,response):
		return 0

	def calcular_puntacion(self,response):
		return 0

	def save_cookie(self,driver, path):
		with open(path, 'wb+') as filehandler:
			pickle.dump(driver.get_cookies(), filehandler)

	def load_cookie(self,driver, path):
		with open(path, 'rb') as cookiesfile:
			cookies = pickle.load(cookiesfile)
			for cookie in cookies:
				driver.add_cookie(cookie)

	def setLoggersLevel (self):
		self.logger=logging.getLogger('twSpider')
		self.logger.setLevel(logging.INFO)
		
		logging.getLogger("scrapy").setLevel(logging.INFO)
		logging.getLogger("neo4j").setLevel(logging.WARNING)
		logging.getLogger("selenium").setLevel(logging.INFO)
		