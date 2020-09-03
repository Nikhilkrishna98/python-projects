from urllib.request import urlopen as ureq
import pymongo
import requests
from bs4 import BeautifulSoup as bs
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin

app = Flask(__name__)

@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')

@app.route('/review', methods=['POST'])
@cross_origin()
def result():
    search_product = request.form['content'].replace(" ", "")
    try:
        dbconn = pymongo.MongoClient("mongodb://localhost:27017/")
        db = dbconn['crawlerDB']
        reviews = db[search_product].find({})
        if reviews.count() > 0:
            return render_template('results.html', reviews=reviews)
        else:
            search_url = "https://www.flipkart.com/search?q=" + search_product
            client_url = ureq(search_url)
            flipkart_page = client_url.read()
            client_url.close()
            flipkart_webpage = bs(flipkart_page, 'html.parser')
            bigboxes = flipkart_webpage.findAll('div', {'class': 'bhgxx2 col-12-12'})
            del bigboxes[0:3]
            box = bigboxes[0]
            product_url = "https://www.flipkart.com"+box.div.div.div.a['href']
            product_results = requests.get(product_url)
            product_results.encoding = 'utf-8'
            product_html = bs(product_results.text, 'html.parser')
            commentboxes = product_html.findAll('div', {'class': '_3nrCtb'})

            table = db[search_product]
            reviews=[]

            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSis'})[0].text

                except:
                    name = 'No name'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No rating'

                try:
                    commenthead = commentbox.div.div.div.p.text

                except:
                    commenthead = 'No comment heading'

                try:
                    comment = commentbox.div.div.find_all('div', {'class': ''})
                    customercomment = comment[0].div.text

                except:
                    customercomment = 'No comments'

                my_dict ={"Product":search_product, "Name":name,"Rating":rating,"CommentHead":commenthead,"Comment":customercomment}

                x = table.insert_one(my_dict)
                reviews.append(my_dict)
            return render_template('results.html', reviews = reviews)
    except:
        return 'something is wrong'
if __name__== "__main__":
    app.run(port=8000, debug=True)

