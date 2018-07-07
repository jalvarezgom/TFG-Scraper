# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'scrapyspider',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = ScrapySpider.settings']},
    include_package_data=True,
)
