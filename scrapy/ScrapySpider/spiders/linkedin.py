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

class lkSpider(scrapy.Spider):
	name = "lk"
	target_page=None
	target_page2 = "https://www.linkedin.com/in/santiago-rodriguez-ortego/"
	header = {
	    "accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	    "accept-encoding" : "gzip, deflate, sdch, br",
	    "accept-language" : "en-US,en;q=0.8,ms;q=0.6",
	    "user-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
	}
	handle_httpstatus_list = [999]
	driver = None
	logger = None

	def __init__(self, url=None, **kwargs):
		#Inicializar target_page con la url objetivo
		self.setLoggersLevel()
		self.logger.info("[SPIDER] - Red Social Linkedin")
		self.target_page = "https://www.linkedin.com/in/santiago-rodriguez-ortego/"
		options = Options()
		#options.set_headless(headless=True)
		self.driver = webdriver.Firefox(firefox_options=options)
		

	def closed(self, reason):
		self.driver.quit()
		self.logger.info("[SPIDER] - Cerrar navegador")
		self.logger.info("[SPIDER] - Tarea del Spider finalizada")

	def start_requests(self):
		self.driver.get(cons.urlLoginLK)
		cookies = Path(cons.cookiesLK)
		if not cookies.is_file():
			self.loginCookies()
		try:
			self.load_cookie(self.driver,cons.cookiesLK)
		except:
			self.logger.warning("[SPIDER] WARNING - Error en carga de cookies")
			pass
		self.driver.get(cons.urlLK)
		#return 	[scrapy.Request(url=self.target_page2, callback=self.parseContact ,headers=self.header,cookies=self.driver.get_cookies())]
		return 	[scrapy.Request(url=self.driver.current_url, headers=self.header, callback=self.login)]

	def login(self,response):
		self.logger.info("[SPIDER] - Login LK")
		if(self.driver.current_url == cons.urlLK):
			if (self.target_page == cons.urlPerfilUsuario):
				return 	[scrapy.Request(url=self.target_page, callback=self.parse ,headers=self.header,cookies=self.driver.get_cookies())]
			else:
				return 	[scrapy.Request(url=self.target_page, callback=self.parseContact ,headers=self.header,cookies=self.driver.get_cookies())]
		else:
			#Cookies caducadas
			self.logger.warning('[SPIDER] - Cookies Invalidas')
			self.driver.get(cons.urlLoginLK)
			self.loginCookies()

	def loginCookies(self):
		self.logger.info("[SPIDER] - Generacion CookiesLK")
		username = self.driver.find_element_by_xpath("//input[@name='session_key']")
		password = self.driver.find_element_by_xpath("//input[@name='session_password']")
		username.send_keys(cons.userLK)
		password.send_keys(cons.passLK)
		self.driver.find_element_by_css_selector('.btn-primary').click()
		time.sleep(1)
		if(self.driver.current_url == cons.urlLoginLK):
			self.logger.several("[SPIDER] SEVERAL - ERROR GENERANDO COOKIESLK LOGIN")
		else:
			try:
				self.save_cookie(self.driver,cons.cookiesLK)
			except:
				self.logger.warning("[SPIDER] WARNING - Error en guardado de cookies")
				pass
			if (self.target_page == cons.urlPerfilUsuario):
				return 	[scrapy.Request(url=self.target_page, callback=self.parse ,headers=self.header,cookies=self.driver.get_cookies())]
			else:
				return 	[scrapy.Request(url=self.target_page, callback=self.parseContact ,headers=self.header,cookies=self.driver.get_cookies())]

	def parse(self, response):
		self.logger.info('[SPIDER] - Parseando usuario objetivo: '+response.url)
		global nivelbusqueda_profundidad
		usuario = GraphItem()

		#Perfil de inicio
		self.driver.get(self.target_page)
		usuario.user = self.driver.find_element_by_xpath("//div[@class='pv-top-card-v2-section__info mr5']//div//h1").text
		usuario.url = self.driver.current_url
		usuario.score = 0
		usuario.plataforma = "lk"

		#Listado de seguidos
		listContacts = self.parseContactList(usuario, nivelbusqueda_profundidad)
		for contact in listContacts:
			yield contact

		yield {'item':usuario}
		
	def parseContact(self,response):
		self.logger.info('[SPIDER] - Parseando usuario relacionado '+response.url)
		usuario = GraphItem()

		#Perfil de inicio
		self.driver.get(response.url)
		usuario.user = self.driver.find_element_by_xpath("//div[@class='pv-top-card-v2-section__info mr5']//div//h1").text
		usuario.url = self.driver.current_url
		usuario.score = 0
		usuario.plataforma = "lk"

		#Listado de competencias
		try: 
			#Usuario que presenta una relación
			usuario.relation.add(response.meta['item'])
			if (profundidad > 0):
				listContacts = self.parseCompetenciaList(usuario,response.meta['profundidad']-1)
				for contact in listContacts:
					yield contact
		except: 
			#Usuario objetivo distinto al propietario de las credenciales del inicio de sesión
			global nivelbusqueda_profundidad
			listContacts = self.parseCompetenciaList(usuario,nivelbusqueda_profundidad)
			for contact in listContacts:
				yield contact


		yield {'item':usuario}

	def parseCompetenciaList(self,usuario,profundidad):
		listRequest = []
		numElemValListCompetencia = 20

		#Scroll de la pagina web
		for x in range (3):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(0.5)
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
		time.sleep(0.5)
		
		listElementShortCompetencia = self.driver.find_elements_by_xpath("//section//ol[@class='pv-skill-categories-section__top-skills pv-profile-section__section-info section-info pb4']//li//div[@class='pv-skill-category-entity__skill-wrapper tooltip-container']//a//span[2]")
		for elem in listElementShortCompetencia:
			elem.click()
			time.sleep(1)

			listContact = self.driver.find_elements_by_xpath("//ul[@class='pv-endorsers__list list-style-none']//li//a")
			for cont in listContact:
				url = cont.get_attribute("href")
				request = scrapy.Request(url, callback=self.parseContact ,headers=self.header,cookies=self.driver.get_cookies())
				request.meta['item'] = usuario
				request.meta['profundidad'] = profundidad-1
				listRequest.append(request)

			self.driver.execute_script("document.getElementsByClassName('artdeco-dismiss')[0].click()")

		self.driver.find_element_by_xpath("//button[@class='pv-profile-section__card-action-bar pv-skills-section__additional-skills artdeco-container-card-action-bar']").click()
		time.sleep(1)
		listElementLongCompetencia = self.driver.find_elements_by_xpath("//div[@class='skill-categories-expanded']//div//ol//li//div")
		for elem in listElementLongCompetencia:
			elem.click()
			time.sleep(1)
		time.sleep(5)

		return listRequest

	def parseContactList(self,usuario,profundidad):
		self.driver.get(cons.urlContactsLK)
		numContacts = self.driver.find_element_by_xpath("//section//header[@class='mn-connections__header']//h2").text.split()[0]
		numElemScroll = 40
		listRequest = []

		for x in range ( int(int(numContacts)/numElemScroll+1)):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(1)

		for x in range(int(numContacts)):
			try:
				url = self.driver.find_element_by_xpath("//section//ul//li["+str(x+1)+"]//div//div[1]//a").get_attribute("href")
				request = scrapy.Request(url, callback=self.parseContact ,headers=self.header,cookies=self.driver.get_cookies())
				request.meta['item'] = usuario
				request.meta['profundidad'] = profundidad-1
				listRequest.append(request)
			except:
				self.logger.info("[SPIDER] WARNING - Excepcion controlada parseContactList()")
				pass

		return listRequest

	def tratar_usuario (self,response):
		return 0

	def calcular_puntacion(self,response):
		return 0

	def save_cookie(self,driver, path):
		with open(path, 'wb') as filehandler:
			pickle.dump(driver.get_cookies(), filehandler)

	def load_cookie(self,driver, path):
		with open(path, 'rb') as cookiesfile:
			cookies = pickle.load(cookiesfile)
			for cookie in cookies:
				driver.add_cookie(cookie)
	
	def setLoggersLevel (self):
		self.logger=logging.getLogger('lkSpider')
		self.logger.setLevel(logging.INFO)
		logging.getLogger("scrapy").setLevel(logging.INFO)
		logging.getLogger("neo4j").setLevel(logging.WARNING)
		logging.getLogger("selenium").setLevel(logging.INFO)