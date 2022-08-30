import csv
from typing import cast
from stat import UF_APPEND
import bs4 as bs
from bs4.element import Tag

import re
import numpy as np #Using this to efficiently create the output file.

import subprocess 
import functools

from selenium import webdriver
from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager as EdgeDriverManager

from multiprocessing import Pool
from multiprocessing import Manager

import time


import pandas as pd

class Poem:
	def __init__(self, title: str, author: str, content: str) -> None:
		self.title = title
		self.author = author
		self.content = content

	def __str__(self) -> str:
		str = ""
		str += self.title + "\n"
		str += "By " + self.author + "\n\n"
		
		str += self.content
		return str

def getPoem(url: str, driver: WebDriver) -> Poem:

	driver.get(url) # Opening the website.
	html_source = driver.page_source 

	poem = getInfo(html_source)
	assert poem is not None
	return poem

def getInfo(html_source: str) -> Poem | None:
	# print(html_source)
	# subprocess.run("pbcopy", universal_newlines=True, input=html_source)

	#Creating beautiful soup object to parse the links.
	soup = bs.BeautifulSoup(html_source, features="html.parser")

	titleRaw = cast(Tag | None, soup.find("h1"))
	title = titleRaw.text.strip() if titleRaw else "Untitled"

	authorRaw = cast(Tag | None, soup.find("meta", property="article:author"))
	author = cast(str, authorRaw["content"]) if authorRaw else "Unkown author"

	
	if titleRaw is not None:
		if titleRaw.parent is not None:
			if titleRaw.parent.parent is not None:
				main = titleRaw.parent.parent
				
				texts = main.find_all("div", {"style" : "text-indent: -1em; padding-left: 1em;"})

				textsStripped = map(lambda x: x.text.strip(), texts)
				poem = "\n".join(textsStripped)

				return Poem(title, author, poem)

""" test 
with open("test/sample.html") as page:
	poem = getInfo("\n".join(page.readlines()))
	print(poem)
exit()
"""




service = EdgeService(EdgeDriverManager().install())

def worker(urls: list[str]) -> list[Poem]:
	driver = webdriver.Edge(service=service) # Setting up the browser with selenium.

	results = list(map(lambda url: getPoem(url, driver), urls))
	driver.quit()
	return results
	

def mp_handler(urls: list[str]):
	num_pools = min(5, len(urls))

	split_urls = cast(list[list[str]], np.array_split(urls, num_pools))

	pool = Pool(num_pools)

	name = 'results/poems ' + time.strftime("%m-%d-%Y %H:%M:%S") + '.csv'
	with open(name, 'w') as out:
		# empty frame for headers
		frame = pd.DataFrame([], columns=['title', 'author', 'content'])
		frame.to_csv(out.buffer)

		for results in pool.map(worker, split_urls):
			rows = list(map(lambda poem: [poem.title, poem.author, poem.content], results))
			frame = pd.DataFrame(rows, columns=['title', 'author', 'content'])
			frame.to_csv(out.buffer, header=False, index=False, quoting=csv.QUOTE_MINIMAL)












def main():
	with open("urls/PoetryFoundationUrls1-10.txt", "r") as urlfile:
		urls: list[str] = []
		for i in range(0, 50):
			urls.append(urlfile.readline())

		print(urls)

		mp_handler(urls)

if __name__=='__main__':
	main()
