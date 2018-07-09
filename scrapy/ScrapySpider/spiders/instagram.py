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

nivelbusqueda_profundidad = 1

class igSpider(scrapy.Spider):
	name = "ig"
	target_page=None
	driver = None
	logger = None

	def __init__(self, url=None, **kwargs):
		#Inicializar target_page con la url objetivo
		self.setLoggersLevel()
		self.logger.info("[SPIDER] - Red Social Instagram")
		self.target_page="https://www.instagram.com/fcklipez/"
		options = Options()
		#options.set_headless(headless=True)
		self.driver = webdriver.Firefox(firefox_options=options)

	def closed(self, reason):
		self.driver.quit()
		self.logger.info("[SPIDER] - Cerrar navegador")
		self.logger.info("[SPIDER] - Tarea del Spider finalizada")

	def start_requests(self):
		#Preparamos las cookies de login
		self.driver.get(cons.urlLoginIG)
		cookies = Path(cons.cookiesLK)
		if not cookies.is_file():
			self.loginCookies()
		try:
			self.load_cookie(self.driver,cons.cookiesIG)
		except:
			self.logger.warning("[SPIDER] WARNING - Error en carga de cookies")
			pass
		self.driver.refresh()
		return 	[scrapy.Request(url=self.driver.current_url, callback=self.login)]
		
	def login(self,response):
		self.logger.info("[SPIDER] - Login IG")
		if(self.driver.current_url == "https://www.instagram.com/"):
			#Spider logeado
			return 	[scrapy.Request(url=self.target_page, callback=self.parse)]
		else:
			#Cookies caducadas
			self.logger.warning('[SPIDER] - Cookies Invalidas')
			self.loginCookies()

	def loginCookies(self):
		self.logger.info("[SPIDER] - Generacion cookiesIG")
		time.sleep(1)
		username = self.driver.find_element_by_xpath("//input[@name='username']")
		password = self.driver.find_element_by_xpath("//input[@name='password']")
		username.send_keys(cons.userIG)
		password.send_keys(cons.passIG)
		self.driver.find_element_by_css_selector('._5f5mN').click()
		time.sleep(1) #Tiempo necesario para que procese el 'login'
		self.driver.get(cons.urlLoginIG)
		if(self.driver.current_url == "https://www.instagram.com/"):
			try:
				self.save_cookie(self.driver,cons.cookiesIG)
			except:
				self.logger.warning("[SPIDER] WARNING - Error en guardado de cookies")
				pass
			return 	[scrapy.Request(url=self.target_page, callback=self.parse)]
		else:
			self.logger.several("[SPIDER] SEVERAL - ERROR GENERANDO COOKIESIG LOGIN")

	def parse(self, response):
		self.logger.info('[SPIDER] - Parseando usuario objetivo: '+response.url)
		global nivelbusqueda_profundidad
		usuario = GraphItem()

		#Perfil de inicio
		self.driver.get(self.target_page)
		usuario.user = self.driver.find_element_by_xpath("//div[@class='nZSzR']//h1").text
		usuario.url = self.driver.current_url
		usuario.plataforma = "ig"

		#Listado de seguidos
		try:
			usuario.score = self.driver.find_element_by_xpath("//li//a[@class='-nal3 ']//span").text			
			listFollowing = self.parseFollowing(usuario,nivelbusqueda_profundidad)
			for followingRequest in listFollowing:
				yield followingRequest
		except NoSuchElementException:
			usuario.score = self.driver.find_element_by_xpath("//li//span[@class='-nal3 ']").text
			pass

		yield {'item':usuario}

		
	def parseFriend(self,response):
		self.logger.info('[SPIDER] - Parseando usuario relacionado '+response.url)
		usuario = GraphItem()

		#Perfil de inicio
		self.driver.get(response.url)
		usuario.user = self.driver.find_element_by_xpath("//div[@class='nZSzR']//h1").text
		usuario.url = self.driver.current_url
		usuario.relation.add(response.meta['item'])
		usuario.plataforma = "ig"

		#Listado de seguidos
		try:
			usuario.score = self.driver.find_element_by_xpath("//li//a[@class='-nal3 ']//span").text			
			if(response.meta['profundidad'] > 0):
				listFollower = self.parseFollowing(usuario,response.meta['profundidad'])
				for followerRequest in listFollower:
					yield followerRequest
		except NoSuchElementException:
			usuario.score = self.driver.find_element_by_xpath("//li//span[@class='-nal3 ']").text
			pass

		yield {'item':usuario}

	def parseFollowing(self,usuario,profundidad):
		listRequest = []
		numSeguidores = self.driver.find_element_by_xpath("//li[@class='Y8-fY '][3]//a//span").text

		self.driver.find_element_by_partial_link_text("seguidos").click()
		time.sleep(1)
		dialog = self.driver.find_element_by_xpath("//div[@class='j6cq2']")
		for x in range( int(int(numSeguidores)/12)+1):
			self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
			time.sleep(0.5)

		friendsLinks = self.driver.find_elements_by_xpath("//li//div//div//a")
		for friend in friendsLinks:
			request = scrapy.Request(friend.get_attribute("href"), callback=self.parseFriend)
			request.meta['item'] = usuario
			request.meta['profundidad'] = profundidad-1
			#self.logger.info(friend.get_attribute("href"))
			listRequest.append(request)

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
		self.logger=logging.getLogger('igSpider')
		self.logger.setLevel(logging.INFO)
		logging.getLogger("scrapy").setLevel(logging.INFO)
		logging.getLogger("neo4j").setLevel(logging.WARNING)
		logging.getLogger("selenium").setLevel(logging.INFO)