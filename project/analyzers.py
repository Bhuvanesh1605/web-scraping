import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse
import time

def get_website_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the website: {e}")
        return None

def extract_product_info(soup):
    products = []
    product_containers = soup.find_all(['div', 'li'], class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower()))
    
    if not product_containers:
        product_containers = soup.find_all('div', id=lambda x: x and ('product' in x.lower() or 'item' in x.lower()))

    for container in product_containers:
        product = {}
        
        name_tag = container.find(['h2', 'h3', 'h4', 'a'], class_=lambda x: x and 'title' in x.lower())
        if name_tag:
            product['name'] = name_tag.text.strip()
        else:
            name_tag = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
            if name_tag:
                product['name'] = name_tag.text.strip()
        
        price_tag = container.find(['span', 'div'], class_=lambda x: x and 'price' in x.lower())
        if price_tag:
            price_text = price_tag.text.strip()
            price_match = re.search(r'\d+(\.\d+)?', price_text.replace(',', ''))
            if price_match:
                product['price'] = float(price_match.group())
        
        rating_tag = container.find(['div', 'span'], class_=lambda x: x and 'rating' in x.lower())
        if rating_tag:
            rating_text = rating_tag.text.strip()
            rating_match = re.search(r'\d+(\.\d+)?', rating_text)
            if rating_match:
                product['rating'] = float(rating_match.group())
        
        reviews_tag = container.find(['div', 'span'], class_=lambda x: x and 'review' in x.lower())
        if reviews_tag:
            reviews_text = reviews_tag.text.strip()
            reviews_match = re.search(r'\d+', reviews_text)
            if reviews_match:
                product['reviews'] = int(reviews_match.group())
        
        if product:
            products.append(product)
    
    return products

def analyze_common_words(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    words = re.findall(r'\w+', text.lower())
    word_counts = Counter(words).most_common(10)
    return word_counts if word_counts else None

def analyze_product_popularity(html):
    soup = BeautifulSoup(html, 'html.parser')
    products = extract_product_info(soup)
    
    if not products:
        return None
    
    sorted_products = sorted(products, key=lambda x: x.get('reviews', 0) or x.get('name', ''), reverse=True)
    
    return [(p.get('name', 'Unknown'), p.get('reviews', 0) or 'N/A') for p in sorted_products[:10]]

def analyze_price_range(html):
    soup = BeautifulSoup(html, 'html.parser')
    products = extract_product_info(soup)
    
    if not products:
        return None
    
    prices = [p['price'] for p in products if 'price' in p]
    
    if not prices:
        return None

    price_ranges = ['0-50', '51-100', '101-200', '201-500', '500+']
    
    def count_prices_in_range(range_str):
        if '+' in range_str:
            min_price = float(range_str.replace('+', ''))
            return sum(1 for p in prices if p > min_price)
        else:
            min_price, max_price = map(float, range_str.split('-'))
            return sum(1 for p in prices if min_price <= p < max_price)
    
    price_counts = [count_prices_in_range(r) for r in price_ranges]
    return list(zip(price_ranges, price_counts)) if any(price_counts) else None

def analyze_best_selling_products(html):
    soup = BeautifulSoup(html, 'html.parser')
    products = extract_product_info(soup)
    
    if not products:
        return None
    
    for product in products:
        score = 0
        if 'reviews' in product:
            score += min(product['reviews'], 100)
        if 'rating' in product:
            score += product['rating'] * 20
        product['score'] = score
    
    sorted_products = sorted(products, key=lambda x: x['score'], reverse=True)
    
    return [(p.get('name', 'Unknown'), p['score']) for p in sorted_products[:10]]

def analyze_meta_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    meta_tags = soup.find_all('meta')
    meta_data = []
    for tag in meta_tags:
        if 'name' in tag.attrs and 'content' in tag.attrs:
            meta_data.append((tag['name'], tag['content']))
    return meta_data if meta_data else None

def analyze_headings(html):
    soup = BeautifulSoup(html, 'html.parser')
    headings = []
    for i in range(1, 7):
        h_tags = soup.find_all(f'h{i}')
        if h_tags:
            headings.append((f'h{i}', len(h_tags)))
    return headings if headings else None

def analyze_links(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
    internal_links = 0
    external_links = 0
    for link in soup.find_all('a', href=True):
        if link['href'].startswith(base_url) or link['href'].startswith('/'):
            internal_links += 1
        else:
            external_links += 1
    return [('Internal Links', internal_links), ('External Links', external_links)]

def analyze_images(html):
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img')
    with_alt = sum(1 for img in images if img.get('alt'))
    without_alt = len(images) - with_alt
    return [('Images with alt text', with_alt), ('Images without alt text', without_alt)]

def analyze_page_load_time(url):
    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        load_time = end_time - start_time
        return [('Page Load Time (seconds)', round(load_time, 2))]
    except requests.RequestException:
        return None

def analyze_word_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    words = re.findall(r'\w+', text)
    return [('Total Word Count', len(words))]

def analyze_keyword_density(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text().lower()
    words = re.findall(r'\w+', text)
    word_count = len(words)
    word_freq = Counter(words)
    keyword_density = [(word, count / word_count * 100) for word, count in word_freq.most_common(10)]
    return keyword_density