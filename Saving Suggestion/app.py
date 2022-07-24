# Importing library
from flask import Flask,  request
from bs4 import BeautifulSoup as bs
import requests, re, json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Flipkart function to extract details of products
def Flipkart(item, rate):
    headers = ({ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                 'Accept-Language': 'en-US, en;q=0.5'})
    link = 'https://www.flipkart.com/search?q='+item.replace(' ', '_')+'&as=on&as-show=on&otracker=AS_Query_TrendingAutoSuggest_1_0_na_na_na&otracker1=AS_Query_TrendingAutoSuggest_1_0_na_na_na&as-pos=1&as-type=TRENDING&suggestionId=mobiles&requestId=5fd7da90-d9a3-487d-9401-6914adb29bd8&as-backfill=on'
    
    page = requests.get(link, headers = headers)
    soup = bs(page.content, 'html.parser')
    
    # Product details
    Flipkart_products = {}

    if soup.find('div',class_='_3pLy-c row'):
        for data in soup.findAll('div', class_ = '_2kHMtA'):
            name = data.find('div', attrs = {'class':'_4rR01T'})
            image = data.find('img', attrs = {'class' : '_396cs4 _3exPp9'})
            price = data.find('div', attrs = {'class':'_30jeq3 _1_WHN1'})
            rating = data.find('div', attrs = {'class':'_3LWZlK'})
            product_link = data.find('a', attrs = {'class':'_1fQZEK'})
            
            if name != None and price != None:
                if rating == None:
                    rating = 'No ratings yet'
                    Flipkart_products[name.text] = ['Flipkart', price.text, image['src'], 'https://www.flipkart.com' + product_link['href'], rating]
                else:
                    Flipkart_products[name.text] = ['Flipkart', price.text, image['src'], 'https://www.flipkart.com' + product_link['href'], rating.text]
    
    elif soup.find('div',class_='_4ddWXP'):
        for data in soup.findAll('div',class_='_4ddWXP'):
            name = data.find('a', attrs = {'class':'s1Q9rs'})
            image = data.find('img', attrs = {'class' : '_396cs4 _3exPp9'})
            price = data.find('div', attrs = {'class':'_30jeq3'})
            rating = data.find('a', attrs = {'class':'_3LWZlK'})
            product_link = data.find('a', attrs = {'class':'_2rpwqI'})

            if name != None and price != None:
                if rating == None:
                    rating = 'No ratings yet'
                    Flipkart_products[name.text] = ['Flipkart', price.text, image['src'], rating, 'https://www.flipkart.com' + product_link['href'], rating]
                else:
                    Flipkart_products[name.text] = ['Flipkart', price.text, image['src'], rating.text, 'https://www.flipkart.com' + product_link['href'], rating.text]
                    
    else:
        for data in soup.findAll('div',class_='_1xHGtK _373qXS'):
            brand = data.find('div', attrs={'class':'_2WkVRV'})
            item_name = data.find('a', attrs={'class':'IRpwTa'})
            image = data.find('img', attrs = {'class' : '_2r_T1I'})
            price = data.find('div', attrs={'class':'_30jeq3'})
            product_link = data.find('a', attrs = {'class':'IRpwTa'})
            
            name = brand.text + ' ' + item_name.text
            if name != None and price != None:
                Flipkart_products[name] = ['Flipkart', price.text, image['src'], 'https://www.flipkart.com' + product_link['href']]
    
    
    # Removing unwanted products
    for key, val in list(Flipkart_products.items()):
        if False in [i in key.lower() for i in item.lower().split()]:
            Flipkart_products.pop(key)
        else:
            pat = r'₹|,'
            val[1] = re.sub(pat, '', val[1])
    
    # Removing over-priced
    for key, val in list(Flipkart_products.items()):
        if int(rate) < int(float(val[1])):
            Flipkart_products.pop(key)
    
    # Sorting in ascending order of price
    Flipkart_products = dict(sorted(Flipkart_products.items(), key = lambda x: int(x[1][1])))

    return Flipkart_products

# Amazon function to extract details of products
def Amazon(item, rate):
    headers = ({ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                 'Accept-Language': 'en-US, en;q=0.5'})
    link = 'https://www.amazon.in/s?k='+item.replace(' ', '+')
    
    page = requests.get(link, headers = headers)
    soup = bs(page.content, 'html.parser')
    
    Amazon_products = {}

    if soup.find('div', class_= 'a-section a-spacing-small a-spacing-top-small') and soup.find('div', class_ = 'a-section aok-relative s-image-fixed-height'):
        for data, link in zip(soup.findAll('div', class_= 'a-section a-spacing-small a-spacing-top-small'), soup.findAll('div', class_ = 'a-section aok-relative s-image-fixed-height')):
            name = data.find('span', attrs = {'class':'a-size-medium a-color-base a-text-normal'})
            image = link.find('img', attrs = {'class' : 's-image'})
            price = data.find('span', attrs = {'class':'a-offscreen'})
            rating = data.find('span', attrs = {'class':'a-icon-alt'})
            product_link = data.find('a', attrs = {'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
           
            if name != None and price != None:
                if rating == None:
                    rating = 'No ratings yet'
                    Amazon_products[name.text] = ['Amazon', price.text, image['src'], 'https://www.amazon.in' + product_link['href'], rating]
                else:
                    Amazon_products[name.text] = ['Amazon', price.text, image['src'], 'https://www.amazon.in' + product_link['href'], rating.text]

    else:
        for data, link in zip(soup.findAll('div', class_= 'a-section a-spacing-small s-padding-left-micro s-padding-right-micro'), soup.findAll('div', class_ = 's-image-padding')):
            brand = data.find('span', attrs = {'class':'a-size-base-plus a-color-base'})
            item_name = data.find('span', attrs = {'class' : 'a-size-base-plus a-color-base a-text-normal'})
            image = link.find('img', attrs = {'class' : 's-image'})
            price = data.find('span', attrs = {'class':'a-offscreen'})
            rating = data.find('span', attrs = {'class':'a-icon-alt'})
            product_link = link.find('a', attrs = {'class':'a-link-normal s-no-outline'})
            
            name = brand.text + ' ' + item_name.text
            if name != None and price != None:
                if rating == None:
                    rating = 'No ratings yet'
                    Amazon_products[name] = ['Amazon', price.text, image['src'], 'https://www.amazon.in' + product_link['href'], rating]
                else:
                    Amazon_products[name] = ['Amazon', price.text, image['src'], 'https://www.amazon.in' + product_link['href'], rating.text]
                    
    
    # Removing unwanted products
    for key, val in list(Amazon_products.items()):
        if False in [i in key.lower() for i in item.lower().split()] or 'renewed' in key.lower():
            Amazon_products.pop(key)
        else:
            pat = r'₹|,'
            val[1] = re.sub(pat, '', val[1])
            
    # Removing over-priced
    for key, val in list(Amazon_products.items()):
        if int(rate) < int(float(val[1])):
            Amazon_products.pop(key)
    
    # Sorting in ascending order of price
    Amazon_products = dict(sorted(Amazon_products.items(), key = lambda x: int(float(x[1][1]))))

    return Amazon_products
    

# Combining all products and ordering in ascending
@app.route('/saving_suggestions/<string:item>/<string:price>', methods = ['GET', 'POST'])
def saving(item, price):
    if request.method == 'GET':
        flipkart = Flipkart(item, price)
        amazon  = Amazon(item, price)

        # Combined product details
        products = {**flipkart, **amazon}

        # Sorting in ascending order
        products = dict(sorted(products.items(), key = lambda x: int(float(x[1][1]))))

        # Response to the frontend
        response = app.response_class(
            response = json.dumps(products),
            status = 200,
            mimetype = 'application/json'
        )

        return response

    else:
        response = app.response_class(status=400)
        return response

# Main Function
if __name__ == '__main__':
    app.run()