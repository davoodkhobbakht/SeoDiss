import json
import os
import random
import requests
from bs4 import BeautifulSoup
from g4f.client import Client
from g4f.Provider import RetryProvider, Liaobots, DDG, ChatGptEs, Pizzagpt
from SeoThisApi.SeoThisApi.main.utils import generate_text_with_g4f, generate_keywords_for_product
import feedparser
from g4f.client import Client


# Load configuration from a JSON file
def load_config(config_file="config.json"):
    try:
        with open(config_file, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file '{config_file}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Configuration file '{config_file}' is not a valid JSON file.")
        exit(1)



config = load_config()
wc_api_url =config['wc_api_url']
consumer_key=config['consumer_key']
consumer_secret=config['consumer_secret']
wp_api_url =config['wp_api_url']
wp_username = config['wp_username']
wp_password = config['wp_password']

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



# Function to get RSS feed URLs using AI
def get_rss_feed_urls(category):
    prompt = (
        f"Please provide a list of 3 reliable RSS feed URLs for the '{category}' category in English. "
        f"Ensure the sources are reputable and provide up-to-date content. Return the URLs as a JSON array.without extra charecters or explaination"
    )

    
    response = generate_text_with_g4f(prompt, max_tokens=4000).replace('```json','')
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
    if post_type == 'informative':
        productnames = fetch_products_in_category(category['name'])
        prompt = (
            f"Suggest one relevant and engaging {post_type} blog topic related to the '{category}' category with these products :\n{productnames}\n."
            f"Ensure the topic is up-to-date, informative, and likely to attract readers."
            f"give me a topic written in Persian."
            'Provide the response in valid json like {"topic":"topic suggestion here"} without any extra characters or explaination.'
            f"exclude these topics: {load_previous_topics()}"
            
        )
    else:
         prompt = (
            f"Suggest one relevant and engaging {post_type} blog topic related to the '{category}' ."
            f"Ensure the topic is up-to-date, informative, and likely to attract readers."
            f"give me a topic written in Persian."
            'Provide the response in valid json like {"topic":"topic suggestion here"} without any extra characters or explaination.'
            f"exclude these topics: {load_previous_topics()}"
            
        )
    response = generate_text_with_g4f(prompt, max_tokens=4000).replace('```json','')

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
    

    response = generate_text_with_g4f(prompt, max_tokens=4000).replace('```json','')
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
            f"Write a 666 word SEO-optimized blog post based on the following news article:\n"
            f"Headline: {news_article['headline']}\n"
            f"Write a detailed, engaging post summarizing the news, adding context, and providing insightful commentary."
            f"Structure the article with proper content, including headings like <h2>, <h3>, and tags such as <strong>,<p>,<ul>,<li>. "
            f"Ensure the tone is informative, SEO-optimized, and structured with HTML headers.Write in Persian "
        )

    elif post_type == 'informative':

        prompt = (
        f"Write a 666 word SEO-optimized blog post about '{category}'. using the following keywords: {', '.join(keywords)}. "
        f"Structure the article with proper structure,using headings like <h2>, <h3>, and tags such as <strong>,<p>,<ul>,<li>. "
        f"Highlight unique features and benefits clearly, ensuring the text provides real value to the reader. "
        f"Optimize the content for Yoast SEO without sacrificing readability. Write in Persian"
        "Ensure the output is clean HTML with no extra characters, symbols, explanations, or blank lines."
    )

    elif post_type == 'marketing':
        prompt = (
            f"Write a 666 word marketing blog post that highlights the benefits and unique selling points of products in the "
            f"'{category}'. Include keywords like {', '.join(keywords)} to optimize for SEO. Create a persuasive and "
            f"engaging tone with a strong call-to-action. Use HTML structure for formatting.Write in Persian"
        )

    response = generate_text_with_g4f(prompt, max_tokens=4000).replace('```html','').replace('```','')
    return response.strip()




def post_blog_to_wordpress(title, content, categories, focus_keyword, meta_description):
    try:
        post_data = {
            'title': title,
            'content': content,
            'status': 'draft',  # Change to 'draft' if you want to review before publishing
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
                    '_yoast_wpseo_focuskw': focus_keyword[0],
                    '_yoast_wpseo_metadesc': meta_description
                }
            }

            seo_response = requests.put(
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
                article = random.choice(news_articles)
                focus_keyword = generate_keywords_for_product(article['headline'])[0]  # First keyword as focus
                title =  choose_blog_topic(focus_keyword,'news')
                post_content = generate_blog_post(title, 'news', news_article=article, keywords=[focus_keyword])
                
                meta_description = f"An update on {category['name']}: {title}"
                print(f"Generated blog post for news article: {title}\n")
                print(post_content)
                post_blog_to_wordpress(title, post_content, [category['id']], focus_keyword, meta_description)
            else:
                print(f"No news articles found for category '{category['name']}'. Skipping to next.")
        else:
            
            title = choose_blog_topic(category, post_type)
            keywords = generate_keywords_for_product(title,)
            focus_keyword = keywords[0] if keywords else category  
            post_content = generate_blog_post(title, post_type, keywords=keywords)
            
            # Fallback if no keywords
            print(f'focus keyword :  {focus_keyword}')
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
    post_type = ['news','informative','marketing',]  # Can be changed to 'news', 'marketing', etc.

    # Create one blog post for the first available category and stop
    category =random.choice(product_categories)
    for post_t in post_type :
    
        print(f"Creating a blog post for category: {category}")
        create_blog_posts([category], post_t)  # Pass a single category
        print(f"Blog post for category '{category}' created. Exiting after one post.")
        # Stop after creating the first post
    print(f"End")
if __name__ == "__main__":
    main()
