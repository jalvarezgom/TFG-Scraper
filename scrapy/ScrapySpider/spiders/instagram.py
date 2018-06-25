import scrapy,pickle,time,logging,json
import ScrapySpider.constantes as cons
from ScrapySpider.mv_item import mv_item,Graphmv_item
from py2neo import Graph,authenticate

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

nivelbusqueda_profundidad = 2
#authenticate("localhost:7474", "neo4j", "my_password")

class igSpider(scrapy.Spider):
	name = "ig"
	#login_page="https://www.instagram.com/accounts/login/"
	target_page="https://www.instagram.com/fcklipez/"
	driver = None

	def __init__(self, url=None, **kwargs):
		print("---Instagram---")
		self.driver = webdriver.Firefox()
		#Inicializar target_page con la url objetivo


	def start_requests(self):
		#Preparamos las cookies de login
		self.driver.get(cons.urlLoginIG)
		self.load_cookie(self.driver,cons.cookiesIG)
		self.driver.refresh()
		return 	[scrapy.Request(url=self.driver.current_url, callback=self.login)]
		
	def login(self,response):
		print("---Login IG---")
		if(self.driver.current_url == "https://www.instagram.com/"):
			#Spider logeado
			return 	[scrapy.Request(url=self.target_page, callback=self.parse)]
		else:
			#Cookies caducadas
			print('Cookies Invalidas')
			self.loginCookies()

	def loginCookies(self):
		print("--Generacion CookiesIG--")
		username = self.driver.find_element_by_xpath("//input[@name='username']")
		password = self.driver.find_element_by_xpath("//input[@name='password']")
		username.send_keys(cons.userIG)
		password.send_keys(cons.passIG)
		self.driver.find_element_by_css_selector('._5f5mN').click()
		time.sleep(1) #Tiempo necesario para que procese el 'login'
		self.driver.get(cons.urlLoginIG)
		if(self.driver.current_url == "https://www.instagram.com/"):
			self.save_cookie(self.driver,cons.cookiesIG)
			#return 	[scrapy.Request(url=self.target_page, callback=self.parse)]
		else:
			print("ERROR GENERANDO COOKIESIG LOGIN")

	def parse(self, response):
		print('Parsear Usuario principal')
		global nivelbusqueda_profundidad
		usuario = Graphmv_item()

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

		yield {'item':usuario}

		
	def parseFriend(self,response):
		print('Parsear Usuario Amigo')
		usuario = Graphmv_item()

		#Perfil de inicio
		self.driver.get(response.url)
		usuario.user = self.driver.find_element_by_xpath("//div[@class='nZSzR']//h1").text
		usuario.url = self.driver.current_url
		usuario.amigos.add(response.meta['item'])
		usuario.plataforma = "ig"

		#Listado de seguidos
		try:
			usuario.score = self.driver.find_element_by_xpath("//li//a[@class='-nal3 ']//span").text			
			if(response.meta['profundidad'] > 0):
				listFollower = self.parseFollowing(usuario,response.meta['profundidad'])
				#logging.info(listFollower)
				for followerRequest in listFollower:
					yield followerRequest
		except NoSuchElementException:
			usuario.score = self.driver.find_element_by_xpath("//li//span[@class='-nal3 ']").text

		

		yield {'item':usuario}

	def parseFollowing(self,usuario,profundidad):
		listRequest = []
		numSeguidores = self.driver.find_element_by_xpath("//li[@class='Y8-fY '][3]//a//span").text
		logging.info(int(numSeguidores)/12)

		self.driver.find_element_by_partial_link_text("seguidos").click()
		time.sleep(1)
		dialog = self.driver.find_element_by_xpath("//div[@class='j6cq2']")
		for x in range( int(int(numSeguidores)/12)+1):
			self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
			time.sleep(1)

		friendsLinks = self.driver.find_elements_by_xpath("//li//div//div//a")
		for friend in friendsLinks:
			request = scrapy.Request(friend.get_attribute("href"), callback=self.parseFriend)
			request.meta['item'] = usuario
			request.meta['profundidad'] = profundidad-1
			logging.info(friend.get_attribute("href"))
			#yield request
			listRequest.append(request)

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