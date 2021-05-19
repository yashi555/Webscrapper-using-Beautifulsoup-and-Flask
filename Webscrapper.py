from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
import pymongo

app = Flask(__name__)  # initialising the flask app with the name 'app'


@app.route('/',methods=['POST','GET']) # route with allowed methods as POST and GET
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","") # obtaining the search string entered in the form
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
            db = dbConn['scrapperDB'] # connecting to the database called scrapperDB
            ratings = db[searchString].find({}) # searching the collection with the name same as the keyword
            if ratings.count() > 0: # if there is a collection with searched keyword and it has records in it
                return render_template('results.html',ratings=ratings) # show the results to user
            else:

                #pages = list(range(1,6))
                #for page in pages:
                my_url = "https://www.flipkart.com/mobiles/pr?sid=tyy%2C4io&q="+searchString#+"&otracker=categorytree&page={}".format(page)
                uClient = urlopen(my_url)
                html_page = uClient.read()
                uClient.close()
                page_html = BeautifulSoup(html_page, "html.parser")
                table = db[searchString]

                ratings = []

                outputs = page_html.findAll('div', {'class': '_2kHMtA'})
                #print(outputs)
                for output in outputs:
                    #print(output)
                    product_name = output.div.img['alt']


                    price_output = output.findAll('div', {'class': 'col col-5-12 nlI3QM'})
                    price = price_output[0].text.strip()

                    rating_output = output.findAll('div', {'class': '_3LWZlK'})
                    final_rating = rating_output[0].text


                    trim_price = ''.join(price.split(','))
                    price_val = trim_price.split("₹")
                    split_price = price_val[1].split('N')
                    final_price = split_price[0]


                    mydict = {"Product": searchString, "Name": product_name, "Price": final_price, "Rating": final_rating}  # saving that detail to a dictionary
                    x = table.insert_one(mydict)  # inserting the dictionary containing the rating comments to the collection
                    ratings.append(mydict)  # appending the comments to the review list


                return render_template('results.html', ratings=ratings)

        except:
            return 'something is wrong'
            # return render_template('results.html')
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000, debug=True)  # running the app on the local machine on port 8000
