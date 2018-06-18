# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging

import time,pickle

class ScrapyRedditSpiderMiddleware(object):
	# Not all methods need to be defined. If a method is not defined,
	# scrapy acts as if the spider middleware does not modify the
	# passed objects.

	#parseRS = { 'tw': lambda:parseResponseTwitter(driver), 'lk': lambda:parseResponseLinkedin(driver), 'ig': lambda:parseResponseInstagram(driver)}
	parseRS = {'lk': lambda:parseResponseLinkedin(driver),'ig': lambda:parseResponseInstagram(driver)}

	def process_request(self,request,spider):
		logging.info('DownloaderMiddleware ->' + spider.name)
		print (request)
		driver = webdriver.Firefox()	
		driver.get(request.url)
		#print(driver.page_source)
		if(spider.name == 'lk'):
			body = self.parseResponseLinkedin(driver)
		elif (spider.name =='ig'):
			body = self.parseResponseInstagram(driver,request)
		else:
			body = driver.page_source
		

		return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)

	def parseResponseTwitter(self,driver):
		logging.info('Ejecutando parseResponseTwitter ->' + driver.current_url);

	def parseResponseLinkedin(self,driver):
		logging.info('Ejecutando parseResponseLinkedin ->' + driver.current_url);

	def parseResponseInstagram(self,driver,request):
		logging.info('Ejecutando parseResponseInstagram ->' + driver.current_url);
		try:
			time.sleep(1)
			username = driver.find_element_by_xpath("//input[@name='username']")
			password = driver.find_element_by_xpath("//input[@name='password']")
			username.send_keys("dracon70@hotmail.com")
			password.send_keys("juanas1995")
			#entrar = driver.find_element_by_link_text('Regístrate').click()
			#logging.info (entrar)
			print("Caso1")
			print(driver.get_cookies())
			#self.load_cookie(driver,"prueba.txt")
			driver.find_element_by_css_selector('._5f5mN').click()
			print("Caso2")
			print(driver.get_cookies())
			time.sleep(3)
			driver.get('https://www.instagram.com/')
			print("Caso3 " +driver.current_url)
			print(driver.get_cookies())
			self.save_cookie(driver,"./ScrapySpider/spiders/cookies/ig.txt")

			
			driver2 = webdriver.Firefox()
			print("Caso1")
			print(driver2.get_cookies())
			driver2.get('https://www.instagram.com/')
			time.sleep(1)
			print("CasoCarga")
			self.load_cookie(driver2,"prueba.txt")
			print(driver.get_cookies())
			driver2.get('https://www.instagram.com/')
			
			
			logging.info ("Page is ready!")
			time.sleep(3)
			return driver.page_sourceasd
		except TimeoutException:
			print ("Loading took too much time!")
	
	def save_cookie(self,driver, path):
		with open(path, 'wb') as filehandler:
			pickle.dump(driver.get_cookies(), filehandler)

	def load_cookie(self,driver, path):
		with open(path, 'rb') as cookiesfile:
			cookies = pickle.load(cookiesfile)
			for cookie in cookies:
				driver.add_cookie(cookie)