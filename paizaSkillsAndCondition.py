from typing import Iterator
import requests
import lxml.html
from lxml import etree
import chardet
import re
import collections

languages = []
platforms = []
databases = []
nessesaryConditionKeys = []
nessesaryConditionValues = []
workLocations = []
ranks = []

def main():
	session = requests.Session()
	urls = scrape_list_page()
	for url in urls:
		response = session.get(url)
		offerDetail = scrape_detail_page(response)
		#print(offerDetail)
	
	print("workLocations = ")
	print([k for k, v in collections.Counter(workLocations).items() if v >= 1])
	print("languages = ")
	print([k for k, v in collections.Counter(languages).items() if v >= 1])
	print("databases = ")
	print([k for k, v in collections.Counter(databases).items() if v >= 1])
	print("platforms = ")
	print([k for k, v in collections.Counter(platforms).items() if v >= 1])
	print("nessesaryConditionKeys = ")
	print([k for k, v in collections.Counter(nessesaryConditionKeys).items() if v >= 1])
	print("nessesaryConditionValues = ")
	print([k for k, v in collections.Counter(nessesaryConditionValues).items() if v >= 1])
	print("ranks = ")
	print([k for k, v in collections.Counter(ranks).items() if v >= 1])


def scrape_list_page():
	urlList = []
	for i in range(1,99):
		str0 = "https://paiza.jp/career/job_offers?page=%d" % (i)
		response = requests.get(str0)
		html = lxml.html.fromstring(response.text)
		html.make_links_absolute(response.url)
		for j in range(2,22):
			str = "#pagebody > div.jobContents.clearfix > div.main > div.boxPickup > div:nth-child(%d) > div.c-job_offer-box__header > a" % (j)
			for a in html.cssselect(str):
				url = a.get('href')
				urlList.append(url)
	return urlList

def cssSelect(html,selector):
	try:
		str1 = html.cssselect(selector)[0].text
	except:
		str1 = "NaN"
	return str1.strip()

def scrapeWorkLocation(html,selector):
	try:
		str1 = html.cssselect(selector)[0].text
		#print(str1)
		str1 = re.sub(r'\s','',str1)
		workLocations.append(str1)
	except:
		str1 = "NaN"
	return str1

def scrapeLanguageAndFramework(html,selector):
	try:
		str1 = html.cssselect(selector)[0].text_content()
		#print("skill:"+str1)
		for skill in str1.splitlines():
			if(skill != ''):
				languages.append(skill)
	except:
		str1 = "NaN"
	return str1.replace('\n',',')

def scrapeDatabase(html,selector):
	try:
		str1 = html.cssselect(selector)[0].text_content()
		for database in str1.split('、'):
			databases.append(re.sub(r"\s","",database))
	except:
		str1 = "NaN"
	return str1

def scrapePlatforms(html,selector):
	try:
		str1 = html.cssselect(selector)[0].text_content()
		for platform in str1.split('、'):
			platforms.append(re.sub(r"\s","",platform))
	except:
		str1 = "NaN"
	return str1

def tableManipulation(html,selector):
	table = html.cssselect(selector)[0].text_content()
	contentList = table.splitlines()
	for i in range(len(contentList)):
		if contentList[i] == "クラウドプラットフォーム":
			platformList = contentList[i+3].split('、')
			for p in platformList:
				platforms.append(p)

def getRanks(html,selector):
	rank = html.cssselect(selector)[0].text_content()
	rank = re.sub(r"通過ランク：",'',rank)
	rank = re.sub(r"\s","",rank)
	ranks.append(rank)
	return rank

def scrapeNesessaryCondition(html,selector):
	try:
		str1 = html.cssselect(selector)[0].text_content()
	except:
		str1 = "NaN"
	str1 = str(str1)
	#print('before:' + str1)
	str1 = re.sub(r'以下すべてのご経験をお持ちの方からのご応募をおまちしています！','',str1)
	str1 = re.sub(r"\s","",str1)
	for line in str1.split('・'):
		line = re.sub(r"のいずれか","",line)
		line = re.sub(r"のすべて","",line)
		line = re.sub(r"（.*","",line)
		line = re.sub(r"\(.*","",line)
		result = re.split('(趣味or実務|実務)',line)
		#print(len(result))
		#print(result)
		if result[0] != '':
			for item in result[0].split(','):
				nessesaryConditionKeys.append(item)
			#nessesaryConditionKeys.append(result[0])

		if len(result) >= 3:
			nessesaryConditionValues.append(result[2])
		#print(result)
	
	#print(str1.split(' '))
	#print('after:'+str1)
	return str1.split(',')


def scrape_detail_page(response: requests.Response) -> dict:
	html = lxml.html.fromstring(response.text)
	#print(response.url)
	offerDetail = {
		'url':response.url,
		'corpname':cssSelect(html,'#corpname > a'),
		'occupation':cssSelect(html,'#job-offer-occupation'),
		'salary':cssSelect(html,'#job-offer-salary-range'),
		'framework':scrapeLanguageAndFramework(html,'#job-offer-dev-framework'),
		'database':scrapeDatabase(html,'#job-offer-databases'),
		'work location':scrapeWorkLocation(html,'#job-offer-feature > div > dl > dd:nth-child(6)'),
		'main dev language':scrapeLanguageAndFramework(html,'#job-offer-main-dev-language'),
		'sub dev language':scrapeLanguageAndFramework(html,'#job-offer-sub-dev-language'),
		'necessary':scrapeNesessaryCondition(html,'#job-offer-recruitement-requirements > dd:nth-child(2)'),
		'rank':getRanks(html,'#main > div.t-two-column.js-toc-content > div.t-two-column__sub-side.u-hidden-on-mobile > div > div.u-mb--20 > div > div > div > div > span'),
		# 'title':html.cssselect('#bookTitle')[0].text_content(),
		# 'price':html.cssselect('.buy')[0].text
		#'cloud platform':scrapePlatforms(html,'#job-offer-feature > div.p-job-offer-summary-area > dl > dd:nth-child(14) > p'),
	}
	tableManipulation(html,'#job-offer-feature > div.p-job-offer-summary-area > dl')
	return offerDetail

if __name__ == '__main__':
	main()