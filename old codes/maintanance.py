import json
import requests
from google.oauth2 import service_account
import googleapiclient.discovery
import datetime
from g4f.client import Client

from g4f.Provider import RetryProvider,Allyfy,Liaobots,DDG,ChatGptEs,Pizzagpt
from SeoThisApi.SeoThisApi.main.utils import generate_text_with_g4f,related_products,get_all_products

# Google Search Console configurations
SERVICE_ACCOUNT_FILE = 'kafshdoozakmug-83f06edd9e2d.json'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def initialize_gsc_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    webmasters_service = googleapiclient.discovery.build('webmasters', 'v3', credentials=credentials)
    return webmasters_service

# Function to get top queries from Google Search Console for a given product URL
def get_gsc_data(service, site_url, product_url, days_ago=30):
    # Calculate dynamic date range
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days_ago)

    request = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['query'],
        'dimensionFilterGroups': [{
            'filters': [{
                'dimension': 'page',
                'operator': 'contains',
                'expression': product_url
            }]
        }],
        'rowLimit': 10
    }
    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
    #print(f'search queries :{response}')
    search_queries = [row['keys'][0] for row in response.get('rows', [])]
    return search_queries

    

# Analyze and improve content with headings and SEO considerations
def analyze_and_improve_content(product_name, current_description, search_queries,r_products):
    """prompt = (
    f"Analyze the following product description for '{product_name}':\n\n"
    f"'{current_description}'\n\n"
    f"The top search queries for this product are: {search_queries}. "
    f"Identify up to four low-quality sentences that could be improved to enhance SEO optimization, including incorporating relevant keywords, improving readability, and increasing engagement.Write it in persian. "
    f"Improve the description by replacing low-quality sentences or headings with SEO-optimized ones, "
    f"preserving headings and SEO tags such as <h2>, <h3>, <ul>, <li>, and <strong>. "
    f"For each identified sentence, provide its original text and the improved version of the sentence.Add any missing sentences to compelete incompelete parts.And expand where necessary. "
    f"Ensure that the improved sentences naturally incorporate relevant keywords from the top search queries where appropriate, without keyword stuffing. "
    f"Return the output as a valid JSON list of dictionaries in the exact format:\n"
    f"[{{'old_sentence': X, 'new_sentence': 'Updated text here'}}, ...]\n"
    f"Do not include any other characters, explanations, or text in your response."
    )"""

    prompt = (
         f"Analyze and improve the following product description for '{product_name}':\n\n"
        f"'with current_description (see it as python str):{current_description}'\n\n"
        f"The top search queries for this product are: {search_queries}. "
        f"related products for this product name: {r_products}. "
        f"Rewrite 2 low-quality text or heading or link  as old_text ,Include relevant keywords naturally, improve readability, enhance SEO optimization, and apply completion for incomplete sections . "
        f"Make sure to preserve HTML structure, including <h2>, <h3>, <ul>, <a>, <li>, and <strong> tags. "
        f"Provide suggestions in this format:\n"
        f"[{{'type': 'heading' or 'text' or 'completion' or 'link', 'new_text': 'Updated text here', 'old_text_index_range' : 'this is 'start ,end' index of the old_text indexing like python_str[index]'}}]\n"
        f"give up to 2 improvements Focus on clear, concise, and structured output without any extra charecter.Write in Persian"
    )
    response = generate_text_with_g4f(prompt, max_tokens=2000).replace('```json','')
    return response.replace('```','')

# Function to update product content
def update_product_content(product_name, current_description, product_url, site_url,r_products):
    gsc_service = initialize_gsc_service()
    search_queries = get_gsc_data(gsc_service, site_url, product_url)
    #competitor_data = fetch_competitor_data_for_queries(search_queries) if search_queries != [] else None
    improved_content_response = analyze_and_improve_content(product_name, current_description, search_queries,r_products)
    print(improved_content_response)
    # Parse and replace low-quality sentences
    #try:
    improvements = eval(improved_content_response)
    updated_description = apply_updates_to_description(current_description, improvements)
    #except Exception as e:
    #print(f"Error parsing AI response: {e}")
    #updated_description = current_description

    return updated_description


def apply_updates_to_description(description, updates):
    
    # Traverse through the updates
    for update in updates:
        suggestion_type = update.get('type')
        start,end = update['old_text_index_range'].split(',')
        new_text = update.get('new_text')
        if suggestion_type == 'text' or suggestion_type == 'heading':
            description = description[:int(start)] + new_text + description[int(end):]
           
        elif suggestion_type == 'completion':  # For expanding content (like completing a section)
            description = description[:int(start)] + new_text + description[int(end):]
    print("\n\n\n************"+description+"\n\n\n************")
                
    # Rebuild and return the updated HTML content
    return description



# Recognize existing links in product description
def get_existing_links(description):
    import re
    url_pattern = re.compile(r'(https?://\S+)')
    return url_pattern.findall(description)

# Analyze internal links and update SEO content
def analyze_and_update_links(description, product_name, related_products, search_queries):
    client = Client(provider=RetryProvider([Liaobots, DDG, ChatGptEs, Pizzagpt]))
    links = get_existing_links(description)
    
    prompt = (
        f"Here is the current product description for '{product_name}':\n\n'{description}'\n\n"
        f"Related products: {[prod['name'] for prod in related_products]}.\n"
        f"Top search queries: {search_queries}.\n"
        f"Analyze the sentences with links: {links}. "
        f"Suggest improved sentences with SEO-optimized internal links, ensuring clarity and engagement."
    )
    response = client.chat.completions.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}], max_tokens=1500
    )
    return response.choices[0].message.content

# Update product description with internal links
def update_internal_links(product_description, updated_description, r_products):
    for product in r_products:
        product_link = f"<a href='{product['url']}'>{product['name']}</a>"
        if product['name'] in updated_description:
            updated_description = updated_description.replace(product['name'], product_link)
    return updated_description

# Main function to iterate over WooCommerce products and update them
def main():
    site_url = 'https://kafshdoozakmug.com'
    products = get_all_products()
   
    for product in products:
        product_name = product['name']
        product_url = product['permalink']
        current_description = product['description']
        #print('\n\n\ncurrent_description:\n' + current_description +'\n\n\n')
        print(f"Processing '{product_name}'...")

        # Update content based on GSC data
        #updated_content = update_product_content(product_name, current_description, product_url, site_url,related_products(product, products))
        
        # Analyze and update internal links based on related products
        search_queries = get_gsc_data(initialize_gsc_service(), site_url, product_url)
        print(search_queries)
        #updated_description_with_links = analyze_and_update_links(updated_content, product_name, related_products(product, products), search_queries if search_queries!= [] else product["meta_data"])

        # Insert optimized internal links into the description
        #final_description = update_internal_links(current_description, updated_description_with_links, related_products(product,products))

        #print(f"Final Updated Description for '{product_name}':\n{final_description}\n")

if __name__ == "__main__":
    main()
