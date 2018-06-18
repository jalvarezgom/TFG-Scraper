import scrapy,pickle,time,logging,json
import ScrapySpider.constantes as cons
from ScrapySpider.mv_item import mv_item,Graphmv_item
from py2neo import Graph,authenticate

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

parsearAptitudes = 0
nivelbusqueda_profundidad = 1
#authenticate("localhost:7474", "neo4j", "my_password")

class lkSpider(scrapy.Spider):
	name = "lk"
	login_page="https://www.linkedin.com/m/login/"
	target_page="https://www.linkedin.com/in/jaime-alvarez-gomez-a4000a153/"
	header = {
	    "accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	    "accept-encoding" : "gzip, deflate, sdch, br",
	    "accept-language" : "en-US,en;q=0.8,ms;q=0.6",
	    "user-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
	}
	handle_httpstatus_list = [999]
	driver = None

	def __init__(self, url=None, **kwargs):
		print("---Linkedin---")
		self.driver = webdriver.Firefox()
		#Inicializar target_page con la url objetivo

	def start_requests(self):
		self.driver.get(cons.urlLoginLK)
		self.load_cookie(self.driver,cons.cookiesLK)
		self.driver.get(cons.urlLK)
		return 	[scrapy.Request(url=self.driver.current_url, headers=self.header, callback=self.login)]

	def login(self,response):
		print("---Login---")
		print (self.driver.current_url)
		if(self.driver.current_url == cons.urlLK):
			print("Cookies Validas")
			#return 	[scrapy.Request(url=self.target_page, callback=self.parse, headers = self.headers)]
			return 	[scrapy.Request(url=self.target_page, callback=self.parse ,headers=self.header,cookies=self.driver.get_cookies())]
		else:
			#Cookies caducadas
			print("Cookies Invalidas")
			self.driver.get(cons.urlLoginLK)
			self.loginCookies()

	def loginCookies(self):
		print("--Generacion CookiesLK--")
		username = self.driver.find_element_by_xpath("//input[@name='session_key']")
		password = self.driver.find_element_by_xpath("//input[@name='session_password']")
		username.send_keys(cons.userLK)
		password.send_keys(cons.passLK)
		self.driver.find_element_by_css_selector('.btn-primary').click()
		time.sleep(1)
		if(self.driver.current_url == cons.urlLoginLK):
			print("ERROR GENERANDO COOKIESLK LOGIN")
		else:
			self.save_cookie(self.driver,cons.cookiesLK)
			return 	[scrapy.Request(url=self.target_page, callback=self.parse ,headers=self.header,cookies=self.driver.get_cookies())]

	def parse(self, response):
		print("--Inicio Parse()--")
		global nivelbusqueda_profundidad
		usuario = Graphmv_item()
		print("pruebaaaa")
		print(response.body)
		#Perfil de inicio
		self.driver.get(self.target_page)
		usuario.user = self.driver.find_element_by_xpath("//div[@class='pv-top-card-v2-section__info mr5']//div//h1").text
		usuario.url = self.driver.current_url
		usuario.score = 0

		#Listado de seguidos
		listContacts = self.parseContacts(usuario, nivelbusqueda_profundidad)
		for contact in listContacts:
			yield contact

		yield {'item':usuario}
		
	def parseContact(self,reponse):
		print("--Inicio Parse()--")
		usuario = Graphmv_item()
		logging.info(response.meta['profundidad'])
		#Perfil de inicio
		self.driver.get(response.url)
		usuario.user = self.driver.find_element_by_xpath("//div[@class='pv-top-card-v2-section__info mr5']//div//h1").text
		usuario.url = self.driver.current_url
		usuario.score = 0


		return 0

	def parseCompetencia(self,response):
		return 0

	def parseContacts(self,usuario,profundidad):
		self.driver.get(cons.urlContactsLK)
		numContacts = self.driver.find_element_by_xpath("//section//header[@class='mn-connections__header']//h2").text.split()[0]
		numElemScroll = 40
		listRequest = []

		for x in range ( int(int(numContacts)/numElemScroll+1)):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(1)

		logging.info( int(numContacts)/numElemScroll+1)
		logging.info(self.driver.find_element_by_xpath("//section//ul//li//div//div[1]//a").get_attribute("href"))
		#contactsLinks = self.driver.find_elements_by_xpath("//section//ul//li")
		for x in range(int(numContacts)):
			try:
				url = self.driver.find_element_by_xpath("//section//ul//li["+str(x+1)+"]//div//div[1]//a").get_attribute("href")
				request = scrapy.Request(url, callback=self.parseContact ,headers=self.header,cookies=self.driver.get_cookies())
				request.meta['item'] = usuario
				request.meta['profundidad'] = profundidad-1
				listRequest.append(request)
			except:
				logging.info("Excepcion generada parseContacs()")

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
	