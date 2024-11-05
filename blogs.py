import json
import os
import random
import requests
from bs4 import BeautifulSoup
from g4f.client import Client
from g4f.Provider import RetryProvider, Liaobots, DDG, ChatGptEs, Pizzagpt
from Main import generate_text_with_g4f, generate_keywords_for_product
import feedparser
from g4f.client import Client

# WooCommerce API credentials (add your credentials here)
wc_api_url =  'https://kafshdoozakmug.com/wp-json/wc/v3'
consumer_key = os.getenv('WC_CONSUMER_KEY')
consumer_secret = os.getenv('WC_CONSUMER_SECRET')

# Function to fetch all categories from WooCommerce
def fetch_categories():
    response = requests.get(
        f"{wc_api_url}/products/categories",
        params={'consumer_key': consumer_key, 'consumer_secret': consumer_secret}
    )
    if response.status_code == 200:
        categories = response.json()
        return [{'name' :category['name'] , 'id' :category['id']} for category in categories]
    else:
        print(f"Failed to fetch categories. Status code: {response.status_code}")
        return []

# Function to fetch products related to a specific category
def fetch_products_in_category(category_id):
    response = requests.get(
        f"{wc_api_url}/products",
        params={
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
            'category': category_id
        }
    )
    if response.status_code == 200:
        products = response.json()
        return products
    else:
        print(f"Failed to fetch products for category ID {category_id}. Status code: {response.status_code}")
        return []

# Function to fetch high search volume topics for a given category
def fetch_high_search_volume_topics(category,post_type):
    # Generate keywords related to the category
    topic = choose_blog_topic(category,post_type)
    high_volume_keywords = find_high_volume_keywords(topic)
    return high_volume_keywords

# Function to get RSS feed URLs using AI
def get_rss_feed_urls(category):
    prompt = (
        f"Please provide a list of 3 reliable RSS feed URLs for the '{category}' category. "
        f"Ensure the sources are reputable and provide up-to-date content. Return the URLs as a JSON array.without extra charecters or explaination"
    )

    
    response = generate_text_with_g4f(prompt, max_tokens=2000).replace('```json','')
    response = response.replace('```','')
    print(response)
    try:
        rss_urls = eval(response)
        if isinstance(rss_urls, list) and rss_urls:
            return rss_urls
        else:
            print(f"Invalid response format for category '{category}'.")
            return []
    except Exception as e:
        print(f"Error parsing AI response for category '{category}': {e}")
        return []

# Function to fetch latest news articles from RSS feeds
def fetch_latest_news(category):
    rss_feed_urls = get_rss_feed_urls(category)

    if not rss_feed_urls:
        print(f"No valid RSS feeds found for category '{category}'.")
        return []

    articles = []
    for feed_url in rss_feed_urls:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            for entry in feed.entries[:3]:  # Limit to top 5 articles per feed
                headline = entry.title if 'title' in entry else 'No headline'
                content = entry.content if 'content' in entry else ''
                published = entry.published if 'published' in entry else 'No publication date'
                
                articles.append({
                    'headline': headline,
                    'content': content,
                    'published': published
                    })
    print("\n\n\n\n"+str(articles)+"\n\n\n\n")
    if not articles:
        print(f"No articles found for category '{category}'.")
    else:
        print(f"Fetched {len(articles)} articles for category '{category}'.")

    return articles


# Function to fetch blog posts and their categories from WordPress using the WordPress REST API
def fetch_existing_blog_posts():
    response = requests.get(
        f"{wp_api_url}/posts",
        params={'per_page': 100},
        auth=(wp_username, wp_password)  # Using HTTP Basic Auth for authentication
    )
    
    if response.status_code == 200:
        posts = response.json()
        # Extract the title and categories for each post
        return [{'title': post['title']['rendered'], 'categories': post['categories']} for post in posts]
    else:
        print(f"Failed to fetch blog posts. Status code: {response.status_code}, Response: {response.text}")
        return []


# Modify load_previous_topics to pull topics from WordPress
def load_previous_topics():
    existing_posts = fetch_existing_blog_posts()
    return [post['title'] for post in existing_posts]


# Step 1: Function to choose a topic related to a category
def choose_blog_topic(category,post_type):
    productnames = fetch_products_in_category(category['name'])
    prompt = (
        f"Suggest one relevant and engaging {post_type} blog topic related to the '{category}' category with these products :\n{productnames}\n."
        f"Ensure the topic is up-to-date, informative, and likely to attract readers."
        f"give me a topic written in Persian."
        'Provide the response in valid json like {"topic":"topic suggestion here"} without any extra characters or explaination.'
        f"exclude these topics: {load_previous_topics()}"
        
    )
    
    response = generate_text_with_g4f(prompt, max_tokens=2000).replace('```json','')

    print(response.replace('```',''))
    response = response.replace('```','')
    topic = eval(response)['topic']
    return topic

# Step 2: Function to find high search volume keywords for the topic
def find_high_volume_keywords(topic):
    prompt = (
        f"List 3 high search volume persian keywords related to the topic '{topic}'. "
        f"Ensure these keywords are relevant and commonly used for SEO. "
        f"Return the output as a JSON list like ['keyword1', 'keyword2', 'keyword3'] withoun any extra charecter or explaination."
    )
    

    response = generate_text_with_g4f(prompt, max_tokens=2000).replace('```json','')
    response = response.replace('```','')
    print()
    try:
        keywords = eval(response)
        if isinstance(keywords, list) and keywords:
            return keywords
        else:
            print("Invalid keyword response format.")
            return []
    except Exception as e:
        print(f"Error parsing AI response for keywords: {e}")
        return []

# Function to generate blog post based on type: informative, marketing, or news
def generate_blog_post(category, post_type, news_article=None, keywords=[]):
    if post_type == 'news' and news_article:
        prompt = (
            f"Write a 300-500 word SEO-optimized blog post based on the following news article:\n"
            f"Headline: {news_article['headline']}\n"
            f"content: {news_article['content']}\n\n"
            f"Write a detailed, engaging post summarizing the news, adding context, and providing insightful commentary.Write in persian"
            f"Structure the article with proper content, including headings like <h2>, <h3>, and tags such as <strong>,<p>,<ul>,<li>. "
            f"Ensure the tone is informative, SEO-optimized, and structured with HTML headers. Include a call-to-action at the end."
        )

    elif post_type == 'informative':

        prompt = (
        f"Write a 300-500 word SEO-optimized blog post about '{category}'. using the following keywords: {', '.join(keywords)}. "
        f"Structure the article with proper structure,using headings like <h2>, <h3>, and tags such as <strong>,<p>,<ul>,<li>. "
        f"Highlight unique features and benefits clearly, ensuring the text provides real value to the reader. "
        f"Optimize the content for Yoast SEO without sacrificing readability. Write in Persian"
        "Ensure the output is clean HTML with no extra characters, symbols, explanations, or blank lines."
    )

    elif post_type == 'marketing':
        prompt = (
            f"Write a 500-700 word marketing blog post that highlights the benefits and unique selling points of products in the "
            f"'{category}' category. Include keywords like {', '.join(keywords)} to optimize for SEO. Create a persuasive and "
            f"engaging tone with a strong call-to-action. Use HTML structure for formatting."
        )

    response = generate_text_with_g4f(prompt, max_tokens=1500)
    return response.strip()


# WordPress API credentials
wp_api_url = 'https://kafshdoozakmug.com/wp-json/wp/v2'
wp_username = os.getenv('WP_USERNAME')
wp_password = os.getenv('WP_PASSWORD') 


def post_blog_to_wordpress(title, content, categories, focus_keyword, meta_description):
    try:
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish',  # Change to 'draft' if you want to review before publishing
            'categories': categories[0],  # IDs of categories
        }

        # Post the blog content to WordPress
        response = requests.post(
            f"{wp_api_url}/posts",
            json=post_data,
            auth=(wp_username, wp_password)
        )

        if response.status_code == 201:
            post_id = response.json()['id']
            print(f"Blog post '{title}' published successfully. Post ID: {post_id}")

            # Set SEO metadata using Yoast SEO if supported
            seo_data = {
                'meta': {
                    '_yoast_wpseo_focuskw': focus_keyword,
                    '_yoast_wpseo_metadesc': meta_description
                }
            }

            seo_response = requests.post(
                f"{wp_api_url}/posts/{post_id}",
                json=seo_data,
                auth=(wp_username, wp_password)
            )

            if seo_response.status_code == 200:
                print("SEO metadata set successfully.")
            else:
                print(f"Failed to set SEO metadata. Status code: {seo_response.status_code}, Response: {seo_response.text}")
        else:
            print(f"Failed to publish blog post. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"An error occurred while posting to WordPress: {e}")



def create_blog_posts(categories, post_type='informative'):
    for category in categories:
        print(f"Fetching latest news and generating {post_type} blog for category: {category['name']}")
        
        if post_type == 'news':
            news_articles = fetch_latest_news(category['name'])
            if news_articles:
                for article in news_articles:
                    post_content = generate_blog_post(category['name'], 'news', news_article=article, keywords=[])
                    title = article['headline']
                    focus_keyword = generate_keywords_for_product(category['name'])[0]  # First keyword as focus
                    meta_description = f"An update on {category['name']}: {title}"
                    print(f"Generated blog post for news article: {title}\n")
                    print(post_content)
                    post_blog_to_wordpress(title, post_content, [category['id']], focus_keyword, meta_description)
            else:
                print(f"No news articles found for category '{category['name']}'. Skipping to next.")
        else:
            keywords = fetch_high_search_volume_topics(category, post_type)
            post_content = generate_blog_post(category, post_type, keywords=keywords)
            title = choose_blog_topic(category, post_type)
            focus_keyword = keywords[0] if keywords else category  # Fallback if no keywords
            meta_description = f"Learn more about {category} in our latest blog post."
            print(f"Generated {post_type} blog post for category: {category}\n")
            print(post_content)
            post_blog_to_wordpress(title, post_content, [category['id']], focus_keyword, meta_description)


# Main function to generate blog posts using dynamically fetched categories
def main():
    # Fetch categories from WooCommerce API
    product_categories = fetch_categories()
    if not product_categories:
        print("No categories found or failed to fetch categories. Exiting.")
        return
    
    # Log the categories that will be used for blog post generation
    print(f"Fetched categories: {product_categories}")
    
    # Set the type of blog post generation
    post_type = 'informative'  # Can be changed to 'news', 'marketing', etc.
    
    # Create blog posts for each category
    create_blog_posts(product_categories, post_type)

if __name__ == "__main__":
    main()
