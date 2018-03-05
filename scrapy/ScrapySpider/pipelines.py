# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from py2neo import Graph



class ScrapyRedditPipeline(object):
	graph = Graph("http://localhost:7474/db/data/")

	def process_item(self, item, spider):
		print(item)
		self.graph.push(item['item'])
		return item
