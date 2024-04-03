from bs4 import BeautifulSoup
import requests

#html as file 
with open('home.html', 'r') as html_file:
    content = html_file.read()

    soup = BeautifulSoup(content,  'html.parser')
    products = soup.find_all('li', class_ = 'product')
    for product in products:
            product_name = product.span.text
            product_price = product.a.text
            print(product_name)
            print(product_price)


#html from url
html_form = requests.get("https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=python&txtLocation=")
soup = BeautifulSoup(html_form.text, 'html.parser')
jobs = soup.find('div', class_ = "clearfix job-bx wht-shd-bx")
print(jobs)





            
   