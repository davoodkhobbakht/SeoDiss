import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import datetime


# Function to fetch competitor data for specific queries
def fetch_competitor_data_from_search(query):
    

    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": query,
    "location": "Iran",
    "google_domain": "google.com",
    "hl": "fa",
    "gl": "ir",
    
    })
    headers = {
    'X-API-KEY': '5b7adffe63039382e349ddb6a6ed799cdeb3e262',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(json.loads(response.content))
    competitor_data =[]

    if response.status_code == 200:
        for r in json.loads(response.content)['organic'] :
            print(r)
            competitor_data.append(analyze_url(r['link']))
        return competitor_data
    else:
        print(f"Failed to retrieve data for query: {query}")
        return None
    

def fetch_competitor_data_for_queries(top_queries):
    competitor_data = {}
    for query in top_queries:
        competitor_data[query] = fetch_competitor_data_from_search(query)
    return competitor_data

# Function to analyze a competitor's URL for SEO data (title, meta tags, headings, etc.)
def analyze_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print(soup.extract)
        # Extract SEO-relevant data
        title = soup.title.string if soup.title else None
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        headings = [heading.get_text() for heading in soup.find_all(['h1', 'h2', 'h3'])]
        internal_links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href']]
        paragraphs = [para.get_text() for para in soup.find_all('p')],
            
        return {
            'url': url,
            'title': title,
            'meta_description': meta_description['content'] if meta_description else None,
            'meta_keywords': meta_keywords['content'] if meta_keywords else None,
            'headings': headings,
            'internal_links': internal_links,
            'paragraphs': paragraphs,
            
        }
    else:
        print(f"Failed to retrieve URL: {url}, Status code: {response.status_code}")
        return None

# Function to create or update the competitor data in SQLite
def store_competitor_data(query, data):
    conn = sqlite3.connect('competitor_data.db')
    cursor = conn.cursor()
    
    # Get current time
    current_time = datetime.datetime.now()

    # Insert or replace the data (with query as the unique key)
    cursor.execute(f'''
        INSERT OR REPLACE INTO competitor_data (query, data, last_updated)
        VALUES (?, ?, ?)
    ''', (query, json.dumps(data), current_time))
    
    conn.commit()
    conn.close()

# Function to retrieve competitor data from the database if it exists and is fresh
def fetch_stored_competitor_data(query):
    conn = sqlite3.connect('competitor_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT data, last_updated FROM competitor_data WHERE query=?', (query,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        data, last_updated = row
        last_updated = datetime.datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S.%f')
        if (datetime.datetime.now() - last_updated).days < 7:
            return json.loads(data)
    
    return None

# Test function to demonstrate data storage and retrieval
def test_competitor_data_storage():
    query = "دوربین سونی"
    
    # Fetch competitor data and store it
    competitor_data = fetch_competitor_data_from_search(query)
    
    if competitor_data:
        print("Competitor data stored and fetched successfully.")
        print("Stored Data:", competitor_data)
        store_competitor_data(query, competitor_data)

    # Retrieve cached data (should return the same data if within 7 days)
    cached_data = fetch_stored_competitor_data(query)
    
    if cached_data:
        print("Cached data retrieved:")
        print(cached_data)
    else:
        print("No fresh cached data available.")

# Initialize database and test storage
def initialize_competitor_db():
    conn = sqlite3.connect('competitor_data.db')
    cursor = conn.cursor()
    
    # Create table to store competitor data (with expiration of 7 days)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competitor_data (
            query TEXT PRIMARY KEY,
            data TEXT,
            last_updated TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database and test
initialize_competitor_db()
test_competitor_data_storage()

