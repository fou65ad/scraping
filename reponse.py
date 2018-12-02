
from bs4 import BeautifulSoup
import pandas as pd
import requests
import unicodedata

BASE_URL = "http://books.toscrape.com/"

response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "lxml")

number_of_results = len(soup.find_all(class_ = 'col-xs-6 col-sm-4 col-md-3 col-lg-3'))

print(number_of_results)

ul = soup.find(class_ = 'nav nav-list')
cats = ul.select("li ul li a")
noms = [cat.text.strip() for cat in cats]
urls = ["http://books.toscrape.com/"+cat["href"] for cat in cats ]
categories =zip(noms,urls)

#print(categories)

nonfiction_category_url = list([item for item in categories if item[0] == "Nonfiction"])[0][1]
print(nonfiction_category_url)

def get_number_pages(category_url):
    response = requests.get(category_url)
    soup = BeautifulSoup(response.text, "lxml")
    current = soup.find(class_ = 'current')
    if current is not None:
      return int(current.text.strip()[-1])
    else:
      return 0

#print(get_number_pages(nonfiction_category_url))

def get_books(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "lxml")
    bo = soup.find_all(class_ = 'col-xs-6 col-sm-4 col-md-3 col-lg-3')
    #titles = [title.h3.a["title"] for title in bo]
    #urls = ["http://books.toscrape.com/catalogue"+title.h3.a["href"][8:] for title in bo]
    #im = ["http://books.toscrape.com"+title.img["src"][11:] for title in bo]
    pr = soup.find_all(class_= 'product_price')
    prices = [unicodedata.normalize('NFKD', price.p.text ).encode('ascii','ignore')[1:] for price in pr]
    ratings= []

    for rat in bo:
      ratTMP = rat.p["class"][1]
      if ratTMP == 'One':
        ratings.append(1)
      if ratTMP == 'Two':
        ratings.append(2)
      if ratTMP == 'Three':
        ratings.append(3)
      if ratTMP == 'Four':
        ratings.append(4)
      if ratTMP == 'Five':
        ratings.append(5)
    books = []
    i = 0
    for b in bo:
      info={
        "title" : b.h3.a["title"],
        "price" : prices[i],
        "url" : "http://books.toscrape.com/catalogue"+b.h3.a["href"][8:],
        "image_url" : "http://books.toscrape.com"+b.img["src"][11:],
        "rating" : ratings[i]
      }
      books.append(info)
      i = i+1

    #books = None
    return books

#print(get_books("http://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html"))
def get_all_books(category_url):
    books = []
    books = get_books(category_url)
    nbr = get_number_pages(category_url)
    #print("ffff "+str(nbr))
    for i in range(1,nbr) :
      url = category_url.split('/')
      le = len(url)
      ur = "/".join(url[:le-1])+"/page-"+str(i+1)+".html"
      books = books + get_books(ur)
      
    return books

#print(get_all_books("http://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"))

nonfiction_books = pd.DataFrame(get_all_books(nonfiction_category_url))

average_rating = nonfiction_books["rating"].mean()

maximum_price = nonfiction_books["price"].max()

orders = pd.read_csv("orders.csv")

print (orders.info())