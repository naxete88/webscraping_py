#!/usr/bin/env python
# coding: utf-8

# In[3]:


# importem biblioteques
get_ipython().system('pip install jovian --upgrade --quiet')
import requests
from bs4 import BeautifulSoup
import jovian
import pandas as pd
import numpy as np
import scrapy
import logging
import json
import sys
import re
from scrapy.http import TextResponse
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# # Tasca M10 T01

# **EXERCICI 1**
# 
# **Realitza web scraping de dues de les tres pàgines web proposades utilitzant BeautifulSoup primer i selenium després**
# 
# - http://quotes.toscrape.com
# 
# - https://www.bolsamadrid.es
# 
# - www.wikipedia.es (fes alguna cerca primer i escrapeja algun contingut)

# ## Beautiful Soup amb quotes.toscrape.com

# In[4]:


# descarreguem la pàgina
url = "http://quotes.toscrape.com"
page = requests.get(url)

print(page.text)


# In[5]:


# mirem si la pàgina s'ha descarregat correctament, si el resultat es troba
# entre 200 y 209 voldrà dir que s'ha descarregat correctament.
page.status_code


# In[6]:


# per extraure informació del codi font HTML mitjançant programació
doc = BeautifulSoup(page.text, 'html.parser')
type(doc)


# In[7]:


# si mirem el cuadro de desenvolupadors a chrome veiem una etiqueta div amb la
# classe establerta en quote. busquem totes les etiquetes div que tinguin
# la clase quote.b
div_tags = doc.find_all('div', class_ = 'quote')
len(div_tags)


# In[8]:


# cada pàgina té 10 cites, per tant el length de div_tags és 10. 
# div_tags conté informació de la cita, el nom de l'autor, enllaços a la 
# bibliografía de l'autor
def get_quotes(div_tags):
# d'aquesta manera obtenim la llista de cites per una pàgina
    quotes = []
    for tag in div_tags:
        quote = tag.find('span', class_ = 'text').text
        quotes.append(quote)
    return quotes


# In[9]:


get_quotes(div_tags)


# In[10]:


# ara extraiem els noms dels autors que es troba dins de small tag
def get_author_name(div_tags):
    authors = []
    for tag in div_tags:
        span_tag = tag.find('span', class_ = None)
        author = span_tag.find('small', class_ = 'author').text
        authors.append(author)
    return authors


# In[11]:


get_author_name(div_tags)


# In[12]:


# extreiem
def get_quote_tag(div_tags):
    name_tags = []
    for tag in div_tags:
        name_tag = tag.find('div', class_ = 'tags').meta['content']
        name_tags.append(name_tag)
    return name_tags


# In[13]:


get_quote_tag(div_tags)


# In[14]:


# extreiem els enllaços de la biografia de l'autor.
def get_author_urls(div_tags):
    author_links = []
    for tag in div_tags:
        span_tag = tag.find('span', class_ = None)
        author_link = 'http://quotes.toscrape.com'+span_tag.find('a')['href']
        author_links.append(author_link)
    return author_links


# In[15]:


get_author_urls(div_tags)


# In[16]:


author_names = get_author_name(div_tags)
quotes_list =  get_quotes(div_tags)
urls = get_author_urls(div_tags)
subject_names = get_quote_tag(div_tags)


# In[17]:


# fem un diccionari combinant tota la llista obtinguda al analitzar el lloc web.
def list_of_dict(quotes_list, author_names, urls, subject_names):
    return[{'Quotes' : quotes_list[i],
            'Author' : author_names[i],
            'Tags' : subject_names[i],
            'Link' : urls[i]} for i in range(len(quotes_list))]


# In[18]:


quotes_dict = list_of_dict(quotes_list,author_names,urls,subject_names)


# In[19]:


# convertim l'arxiu en csv
df = pd.DataFrame(quotes_dict)
df.to_csv('cites.csv', index = None)


# In[20]:


# mirem l'arxiu
pd.read_csv('cites.csv')


# ## Selenium amb quotes.to.scrape.com

# In[21]:


# opcions de navegació
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--distable-extensions')
driver_path = 'C:\\chromedriver.exe'
driver = webdriver.Chrome(driver_path, chrome_options = options)
# així s'obrirà el navegador
driver.get('http://quotes.toscrape.com')

total = []

cites = driver.find_elements(By.CLASS_NAME,"quote")

for quote in cites:
    cita = quote.find_element(By.CLASS_NAME,'text').text[1:-2]
    autor = quote.find_element(By.CLASS_NAME,'author').text
    tags = quote.find_element(By.CLASS_NAME,'tags').text[6:]
    new = ((cita, autor, tags))
    total.append(new)

'''for x in range (len(cites)):
    print(cites[x].text)'''

driver.quit()

df = pd.DataFrame(total, columns=['cita','autor','tags'])
df.to_csv('cites_selenium.csv', index = None)
df.head(10)


# **Amb l'exercici de wikipedia vaig a obtenir el resultat final de la classificació del mundial d'aquest any de Formula 1**

# ## Beautiful Soup amb wikipedia

# In[22]:


# descarreguem la pàgina
url = "https://es.wikipedia.org/wiki/Temporada_2022_de_F%C3%B3rmula_1"
page = requests.get(url)
page.status_code
page_text = page.text
# demanem que ens digui si l'extracció del text s'ha fet correctament, si recordem
# de 200 a 208 s'ha fet correctament
print(page.status_code)


# In[23]:


soup = BeautifulSoup(page_text,'html.parser')
print(soup.prettify())


# In[24]:


#demanem que ens retorni totes les taules
soup.find_all('table')


# In[25]:


# demanem quantes taules hi ha a l'article
len(soup.find_all('table'))


# In[26]:


# segons les característiques hi ha dues possibles taules.
print('Clases de cada taula:')
for table in soup.find_all('table'):
    print(table.get('class'))


# In[27]:


# busco la taula de classificació
right_table = soup.find_all('table', class_= 'wikitable sortable')
# mirem les taules i selecciono la taula [0] que és la que vull
right_table = right_table[0]
right_table


# In[28]:


# llegim l'html
df = pd.read_html(str(right_table))
df= pd.DataFrame(df[0])
# elimino les columnes que no vull
df_1 = df.drop(['Victorias','Podios','Poles','Vueltas rápidas', 'Vueltas lideradas'], axis = 1)
# converteixo en csv
df_1.to_csv('classificacio.csv', index = None)
# llegeixo el cs
pd.read_csv('classificacio.csv')


# ## Selenium amb wikipedia

# In[29]:


# opcions de navegació
dfbase = pd.DataFrame()
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--distable-extensions')
driver_path = 'C:\\chromedriver.exe'
driver = webdriver.Chrome(driver_path, chrome_options = options)
# així s'obrirà el navegador
driver.get('https://es.wikipedia.org/wiki/Temporada_2022_de_F%C3%B3rmula_1')
# extrec la taula
item = driver.find_elements(By.XPATH, '//*[@id="mw-content-text"]/div[1]/table[14]')
# extrec les dades de la taula
for table in item:
    data = [item.text for item in table.find_elements(By.XPATH, ".//*[self::td or self::th]")]
    print(data)
# així es tancarà el navegador
driver.quit()


# In[30]:


columns = ['Pos',
           'Piloto',
           'Escuderia',
           'Grandes Premios',
           'Victorias',
           'Podios',
           'Poles',
           'Vueltas Rapidas',
           'Vueltas lideradas',
           'Puntos']
columnes = len(columns)
print(columnes)


# In[31]:


nnn = []
for i in range(0, len(data), columnes):
    nnn.append(data[i:i + columnes])
    
df_selenium = pd.DataFrame(nnn, columns = columns)
# converteixo en csv
df_selenium.to_csv('classificacio_selenium.csv', index = None)
# llegeixo el cs
pd.read_csv('classificacio_selenium.csv')
# elimino les columnes que no vull
df_1_selenium = df_selenium.drop(columns = ['Victorias','Podios','Poles','Vueltas Rapidas','Vueltas lideradas'])
# elimino la primera fila que son les columnes duplicades
df_2_selenium = df_1_selenium.drop(0) 
# imprimeixo
df_2_selenium


# **EXERCICI 3**
# 
# **Tria una pàgina web que tu vulguis i realitza web scraping mitjançant la llibreria Selenium primer i Scrapy després.**

# ## Selenium

# In[32]:


# opcions de navegació
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--distable-extensions')
driver_path = 'C:\\chromedriver.exe'
driver = webdriver.Chrome(driver_path, chrome_options = options)
# així s'obrirà el navegador
driver.get('https://datosmacro.expansion.com/materias-primas/petroleo')# opcions de navegació
# accepto cookies
element = driver.find_element(By.XPATH,'//*[@id="didomi-notice-agree-button"]')
element.click()
# extrec la informació:
nom = driver.find_element(By.XPATH,'//*[@id="tb1_43803"]/tbody/tr[1]/td[1]').text[:-3]
cotització = driver.find_element(By.XPATH,'//*[@id="tb1_43803"]/tbody/tr[1]/td[3]').text
data = driver.find_element(By.XPATH,'//*[@id="tb1_43803"]/tbody/tr[1]/td[2]').text
print('el',nom,'cotitza a',cotització,'amb data',data)
# així es tancarà el navegador
driver.quit()


# ## Scrapy

# In[41]:


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('resultados.jl','w')
    def close_spider(self,spider):
        self.file.close()
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


# In[42]:


# defineixo l'spider
class BrentSpider(scrapy.Spider):
# nom de l'spider
    name = "Brent"
# url que buscarà
    start_urls = [
        'https://datosmacro.expansion.com/materias-primas/petroleo',
    ]
    custom_settings = { # com es guardarà l'arxiu
        'LOG_LEVEL' : logging.WARNING,
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'brent.csv'
    }
# defineixo lo que vull extreure, en format text dins de la taula
    def parse(self,response):
        for row in response.xpath('//*[@id="tb1_43803"]'):
            yield{
                'nom' : row.xpath('//*[@id="tb1_43803"]/tbody/tr[1]/td[1]/a//text()').extract_first(),
                'cotització' : row.xpath('//*[@id="tb1_43803"]/tbody/tr[1]/td[3]//text()').extract_first(),
                'data' : row.xpath('//*[@id="tb1_43803"]/tbody/tr[1]/td[2]//text()').extract_first(),
            }
    


# In[43]:


# si no introdueixo aquest condicional surt un missatge d'error on diu que ja s'ha creat el procediment
if "twisted.internet.reactor" in sys.modules:
    del sys.modules["twisted.internet.reactor"]
# executo l'spider    
process = CrawlerProcess()
process.crawl(BrentSpider)
process.start()


# In[45]:


# un cop s'ha executat l'spider tindré un arxiu .csv al ordinador, si el converteixo en DataFrame, haig d'eliminar la segona
# fila que són els headers i la primera que inclou llenguatge html.
# llegeido l'arxiu.
df = pd.read_csv('C:\Brent.csv')
df1 = df.drop([0,1], axis = 0)
df1.head()

