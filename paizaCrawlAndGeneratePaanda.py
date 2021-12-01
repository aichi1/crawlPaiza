from typing import Iterator
import requests
import lxml.html
from lxml import etree
import chardet
import re
import collections
import pandas as pd

workLocations = ['東京都', '宮城県', '京都府', '北海道', '大阪府', '神奈川県', '愛知県', '沖縄県', '茨城県', '福岡県', '埼玉県', '広島県', '滋賀県', '愛媛県', '福井県', '兵庫県', '岡山県', '和歌山県', '香川県', '山口県', '静岡県', '群馬県', '石川県', '佐賀県', '千葉県', '秋田県', '熊本県', '大分県', '福島県', '徳島県', '長崎県', '島根県', '長野県']
languages = ['JavaScript', 'PHP', 'Ruby', 'Python2', 'Python3', 'Go言語', 'C', 'Spring', 'Laravel', 'React', 'Vue.js', 'Java', 'Visual Basic(VB.NET)', 'HTML+CSS', 'SQL', 'Kotlin', 'Swift', 'Django', 'TypeScript', 'Angular', 'HTML5+CSS3', 'C++', 'C＃', '.NET Framework', 'FuelPHP', 'Smarty', 'Android SDK', 'iOS SDK', 'Objective-C', 'Struts', 'Ruby on Rails', 'jQuery', 'Node.js', 'Symfony', 'Zend Framework', 'CakePHP', 'CodeIgniter', 'Flutter', 'Express', 'Next.js', 'Perl', 'React Native', 'Knockout.js', '自社フレームワーク', 'Scala', 'Rust', 'Haskell', 'Gin', 'Play Framework', 'Slim', 'Flask', 'Unity', 'Unreal Engine', 'Phalcon', 'Catalyst', 'ECMAScript', 'Java EE', 'Bootstrap', 'MATLAB', 'MyBatis', 'Nuxt.js', 'Bash', 'Sass', 'F#', 'OpenGL', 'Hibernate', 'COBOL', 'Riot.js', 'CUDA C/C++', 'Chainer', 'Caffe', 'TensorFlow', 'PL/SQL', 'Ethna', 'cocos2d', 'Seasar2', 'JSF', 'Xamarin', 'R言語', 'DirectX', 'Backbone.js', 'ABAP', 'iBATIS', 'Tornado', 'Lua', 'cocos2d-x', 'Echo', 'Haml', 'Ember.js', 'prototype.js', 'Titanium Mobile', 'Elixir', 'CoffeeScript', 'Pyramid', 'Dojo Toolkit', 'Revel', 'Sinatra', 'Camping', 'Waves', 'Pylons', 'ngCore', 'Foundation', 'ActionScript', 'Groovy', 'Erlang', 'AHDL', 'Verilog HDL', 'VHDL']
databases = ['MongoDB', 'MySQL', 'PostgreSQL', 'Oracle', 'DynamoDB', 'MicrosoftSQLServer', 'DB2', 'cassandra', 'SQLite', 'mSQL']
platforms = ['Amazon Web Service', 'Microsoft Azure', 'Google Cloud Platform', 'Firebase', 'さくらのクラウド', 'Salesforce', 'Alibaba', 'Google App Engine', 'Heroku', 'IBM Cloud(IBM Bluemix)', 'Netlify']
nessesaryConditionKeys = ['Web開発', 'C', 'Python2', 'Go言語', '何らかのシステム開発経験', 'Python3', 'JavaScript', 'HTML5+CSS3', 'インフラ設計', 'インフラ構築', 'TypeScript', 'C++', 'コンシューマーゲーム', '画像処理', 'C＃', 'プログラムコーディング', '.NETFramework', 'PHP', 'スマートフォンアプリ開発', 'Swift', 'Objective-C', 'Java', 'Ruby', 'Kotlin', 'SQL', 'システム設計', 'Flutter', 'Laravel', 'Perl', 'デスクトップアプリ開発', '要件定義', 'Scala', 'Haskell', 'Erlang', 'Scheme', 'プロジェクトマネジメント', 'RubyonRails', 'Node.js', '制御組込み系開発', 'コンシューマーゲーム開発', 'React', 'VisualBasic', 'Spring', 'AndroidSDK', 'ECMAScript', '汎用系開発業務', 'メンバー育成', 'VerilogHDL', 'VHDL', 'MATLAB', 'メンバーマネジメント', 'CTO／技術責任者', 'B2B', '自社製品/自社サービス', 'Vue.js', '研究開発', 'HTML+CSS', '業務システム/パッケージ', 'リサーチ、解析', 'データベースの設計、チューニング', 'ネットワーク設計', 'ラインマネジメント', 'Sass', 'Unity', '機械学習', 'Rust', 'チームの指針策定と牽引', '予実管理', 'セキュリティソフトウェア開発', 'テスト', '保守、追加開発', 'B2C', 'Bash', 'WEBサイト、CMS', 'COBOL', 'ソーシャルゲーム', 'Lua', 'Groovy', 'UnrealEngine', 'オンラインゲーム', 'SaaS', '金融/保険', 'スマートフォンアプリ', 'jQuery', '新規開発の企画', 'PL/SQL', 'Django', 'ReactNative', '受託開発', 'Next.js', 'Nuxt.js', '大規模', 'Angular', 'ハードウェア制御', '組込み', 'DirectX', 'OpenGL', 'R言語', 'Struts', 'ポータルサイト', 'AI', 'JavaEE', 'ミドルウェア', 'CakePHP', 'OS', 'ミドルウェア開発', 'ABAP', 'ActionScript', 'Haml', 'iOSSDK', 'Win/Macアプリケーション']
nessesaryConditionValues = {'１年未満':1,'１年以上':2, '３年以上':3, '５年以上':4}
ranks = {'S':5,'A':4,'B':3,'C':2,'D':1,'E':0}

def salaryRangeToEstimatedSalary(str):
  str = re.sub(' 〜 ','',str)
  str = re.sub(' 〜','',str)
  str = re.sub('万円','',str)
  str = re.sub(',','',str)
  result = re.split('万',str)
  a = 0.0
  b = 0.0
  a = int(result[0])
  if len(result) >= 2:
    b = int(result[1])
    return (a+b)/2
  else:
    return a

def skillDict():
	dict = {}
	dict['url'] = ""
	dict['corpname'] = ""
	dict['occupation'] = ""
	dict['salary'] = ""
	dict['estimatedSalary'] = 0
	for i in workLocations:
		dict[i] = 0
	for i in languages:
		dict[i] = 0
	for i in databases:
		dict[i] = 0
	for i in platforms:
		dict[i] = 0
	for i in nessesaryConditionKeys:
		dict['nessesary-'+i] = 0
	dict['rank'] = 0
	return dict

def main():
	k = 0
	dict = skillDict()
	df = pd.DataFrame([dict])
	df.to_csv('skillSet.csv')
	session = requests.Session()
	urls = scrape_list_page()
	for url in urls:
		if(url == "https://paiza.jp/career/job_offers/11260?from=list" ):
			continue
		response = session.get(url)
		print(url)
		if k % 100 == 0:
			df.to_csv('salary-skillSet%d.csv' % k)
			df = pd.DataFrame([dict])
		try:
			offerDetail = scrape_detail_page(response)
			#print(offerDetail)
			df2 = pd.DataFrame([offerDetail])
			# print("------%d--------" % k)
			# print(df2)
			# df2.to_csv('./skillSetTest/test%d.csv' %k)
			k +=1
		finally:
			df = df.append(df2)
			print(k)
	#df.to_csv('salary-skillSet.csv')
	


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
		#workLocations.append(str1)
	except:
		str1 = "NaN"
	return str1

def scrapeLanguageAndFramework(html,selector):
	result = []
	try:
		str1 = html.cssselect(selector)[0].text_content()
		#print("skill:"+str1)
		for skill in str1.splitlines():
			if(skill != ''):
				#languages.append(skill)
				result.append(skill)
	except:
		str1 = "NaN"
	#return str1.replace('\n',',')
	return result

def scrapeDatabase(html,selector):
	result = []
	try:
		str1 = html.cssselect(selector)[0].text_content()
		for database in str1.split('、'):
			#databases.append(re.sub(r"\s","",database))
			result.append(re.sub(r"\s","",database))
	except:
		str1 = "NaN"
	return result

def scrapePlatform(html,selector):
	result = []
	table = html.cssselect(selector)[0].text_content()
	contentList = table.splitlines()
	for i in range(len(contentList)):
		if contentList[i] == "クラウドプラットフォーム":
			platformList = contentList[i+3].split('、')
			for p in platformList:
				#platforms.append(p)
				result.append(p)
	return result

def getRanks(html,selector):
	rank = html.cssselect(selector)[0].text_content()
	rank = re.sub(r"通過ランク：",'',rank)
	rank = re.sub(r"\s","",rank)
	#ranks.append(rank)
	return rank

def scrapeNesessaryCondition(html,selector):
	keyValue = {}
	try:
		str1 = html.cssselect(selector)[0].text_content()
	except:
		str1 = "NaN"
	str1 = str(str1)
	#print('before:' + str1)
	str1 = re.sub(r'以下すべてのご経験をお持ちの方からのご応募をおまちしています！','',str1)
	str1 = re.sub(r"\s","",str1)

	for line in str1.split('・'):
		#print(line)
		line = re.sub(r"のいずれか","",line)
		line = re.sub(r"のすべて","",line)
		result = re.split('(趣味or実務|実務)',line)
		key = result[0]
		key = re.sub(r"（.*","",key)
		key = re.sub(r"\(.*","",key)
		key = re.split(',',key)
		value = ""
		if len(result) == 1:
			continue
		if len(result) > 2:
			value = result[2]

		
		for i in key:
			if i != '' and i in nessesaryConditionKeys:
				keyValue[i] = value
			#keyValue[key] = value
	return keyValue


def scrape_detail_page(response: requests.Response) -> dict:
	html = lxml.html.fromstring(response.text)
	dict = skillDict()
	dict['url'] = response.url
	dict['corpname'] = cssSelect(html,'#corpname > a')
	dict['occupation'] = cssSelect(html,'#job-offer-occupation')
	dict['salary'] = cssSelect(html,'#job-offer-salary-range')
	dict['estimatedSalary'] = salaryRangeToEstimatedSalary(dict['salary'])
	frameWork = scrapeLanguageAndFramework(html,'#job-offer-dev-framework')
	for i in frameWork:
		dict[i] = 1
	database = scrapeDatabase(html,'#job-offer-databases')
	for i in database:
		dict[i] = 1
	workLocation = scrapeWorkLocation(html,'#job-offer-feature > div > dl > dd:nth-child(6)')
	dict[workLocation] = 1
	mainLanguage = scrapeLanguageAndFramework(html,'#job-offer-main-dev-language')
	for i in mainLanguage:
		dict[i] = 1
	subDevLanguage = scrapeLanguageAndFramework(html,'#job-offer-sub-dev-language')
	for i in subDevLanguage:
		dict[i] = 1
	platform = scrapePlatform(html,'#job-offer-feature > div.p-job-offer-summary-area > dl')
	for i in platform:
		dict[i] = 1
	localDict = scrapeNesessaryCondition(html,'#job-offer-recruitement-requirements > dd:nth-child(2)')
	print(localDict)
	for key in localDict:
		dict['nessesary-'+key] = nessesaryConditionValues[localDict[key]]
	rank = getRanks(html,'#main > div.t-two-column.js-toc-content > div.t-two-column__sub-side.u-hidden-on-mobile > div > div.u-mb--20 > div > div > div > div > span')
	dict['rank'] = ranks[rank]
	
	return dict

if __name__ == '__main__':
	main()