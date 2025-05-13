import json
import random
import time
import requests
from g4f.client import Client
import os.path
from g4f.cookies import set_cookies_dir, read_cookie_files
from g4f.Provider import RetryProvider,PollinationsAI,Yqcloud
import g4f.debug
g4f.debug.logging = True
import csv


# WooCommerce API credentials


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
# WooCommerce authentication parameters
wc_auth_params = {
    'consumer_key': consumer_key,
    'consumer_secret': consumer_secret
}

client = Client(
    provider=RetryProvider([PollinationsAI,Yqcloud]),
    #proxies="http://127.0.0.1:10809",
)


# Function to generate text using GPT-4Free (g4f)
def generate_text_with_g4f(prompt, max_tokens=4000):

   
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature = 0.1
        
        
    )
    
    return response.choices[0].message.content

# Function to retrieve all products from WooCommerce
def get_all_products():
    page = 1
    products = []
    while True:
        response = requests.get(f"{wc_api_url}", params={**wc_auth_params, 'page': page, 'per_page': 100})
        if response.status_code == 200:
            current_products = response.json()
            if not current_products:
                break
            products.extend(current_products)
            page += 1
        else:
            print(f"Failed to retrieve products: {response.text}")
            break
    return products

# Function to generate or update article for a WooCommerce product
def generate_article_for_product(product, update=False):
    product_id = product['id']
    product_name = product['name']
    existing_description = product.get('description', '').strip()

    if existing_description and update:
        # Append new content, asking explicitly for a continuation of the existing description
        prompt = (
    f"توضیحات محصول '{product_name}' را به زبان فارسی گسترش و به‌روزرسانی کنید و اطلاعات دقیق‌تری درباره ویژگی‌ها، مزایا و مشخصات فنی آن اضافه کنید. تمرکز بر نقاط قوت منحصر به فرد محصول داشته باشید. ویژگی‌های کلیدی را به صورت فهرست‌وار با استفاده از فرمت HTML (<ul><li>) ارائه دهید. متن باید به طور طبیعی از توضیحات موجود زیر استفاده کند و از تگ‌های <li> استفاده کند. از درج هر گونه متن غیرضروری یا نامرتبط خودداری کنید و به طور کامل بهینه‌سازی شده برای SEO و بازاریابی باشد."
)



    else:
        # Generate a completely new description along with an SEO-optimized title
       prompt = (f"یک توضیحات ۳۰۰ کلمه‌ای بهینه‌سازی شده برای SEO به زبان فارسی برای '{product_name}' بنویسید که بر روی کاربردها، مصارف و هدف مخاطبان آن تمرکز کند. توضیحات باید محصول را به طور طبیعی و قابل خواندن برای مشتریان بالقوه معرفی کند. از ساختار HTML مناسب با عناوین (H2 و H3) استفاده کنید و یک پاراگراف کوتاه در انتها با یک دعوت به عمل برای خرید محصول قرار دهید. مطمئن شوید که کد HTML تمیز و بهینه‌سازی شده برای SEO است. از درج هر گونه متن غیرضروری یا نامرتبط خودداری کنید.")



    # Get additional text or a new description from GPT-4Free
    article_content = generate_text_with_g4f(prompt, max_tokens=600).replace("```html" , "")
    article_content = article_content.replace("```" ,"")
    print('\n\n\n')
    print(article_content)
    print('\n\n\n')
    # Combine the old description and the new content, if necessary
    new_description = existing_description + " " + article_content if update and existing_description else article_content
    
    # Update the product description via the WooCommerce API
    update_data = {"description": new_description}
    update_response = requests.put(f"{wc_api_url}/{product_id}", json=update_data, params=wc_auth_params)
    
    if update_response.status_code == 200:
        print(f"Product '{product_name}' updated successfully.")
    else:
        print(f"Failed to update product '{product_name}': {update_response.text}")


# Function to generate a user question for a product
def generate_question_for_product(product_name):
    prompt = (
        f"Imagine you are a potential customer interested in '{product_name}'. "
        f"Ask a question about its features or uses or any specific details you want to know before buying. "
        f"The question should be natural, informative, and encourage the admin to give helpful advice.Write it in persian.Do not include any unnecessary or unrelated text."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    
    question = response.choices[0].message.content
    return question

# Function to generate an admin reply to a user question
def generate_reply_for_question(question, product_name):
    prompt = (
        f"You're an admin for a product called '{product_name}'. Respond to the following user question in a helpful and "
        f"marketing-focused manner. Address the user's concerns, provide additional benefits and features of the product, "
        f"and encourage the user to make a purchase.Write it in persian.Do not include any unnecessary or unrelated text. The question is: '{question}'"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    
    reply = response.choices[0].message.content
    return reply

# Function to post both the user question and admin reply as comments
def post_comment_and_reply(product_id, question, reply):
    # Posting the user question
    question_data = {
        "post": product_id,
        "author_name": "User",
        "author_email": "user@example.com",
        "content": question,
        "status": "publish"  # Automatically approve the comment
    }

    question_response = requests.post(wc_api_url, json=question_data, params=wc_auth_params)

    if question_response.status_code == 201:
        question_id = question_response.json().get('id')

        # Posting the admin reply
        reply_data = {
            "post": product_id,
            "author_name": "Admin",
            "author_email": "admin@example.com",
            "content": reply,
            "status": "publish",  # Automatically approve the reply
            "parent": question_id  # Link the reply to the original question
        }

        reply_response = requests.post(wc_api_url, json=reply_data, params=wc_auth_params)

        if reply_response.status_code == 201:
            print(f"Comment and reply posted successfully for product ID {product_id}")
        else:
            print(f"Failed to post admin reply: {reply_response.text}")
    else:
        print(f"Failed to post user question: {question_response.text}")

# Example usage
def generate_and_post_comments_for_product(product_id, product_name):
    question = generate_question_for_product(product_name)
    print(question)
    reply = generate_reply_for_question(question, product_name)
    print(reply)
    post_comment_and_reply(product_id, question, reply)

#Generate SEO keywords for each product based on its name
def generate_keywords_for_product(product_name):
    
    prompt = (
    f"Generate exactly 3 highly relevant Persian SEO keywords for '{product_name}' that have high search volume. "
    f"The list should include both short and long-tail keywords, ordered by importance, with the most important keyword first. "
    f"Return the output as a clean, plain list with no extra characters, symbols, explanations, or blank lines. "
    f"Ensure the output is formatted as a valid JSON list in the form: ['keyword1', 'keyword2', 'keyword3'].Write in Persian."
)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Get the response content
    keywords_response = response.choices[0].message.content.strip().replace("```python" , "").replace("```" , "")
    print(keywords_response)
    # Parse the response as a JSON list
    try:
        keywords_list =eval(keywords_response)
        if isinstance(keywords_list, list) and len(keywords_list) == 3:
            return keywords_list
        else:
            raise ValueError("The response is not a valid list of 3 keywords.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from AI response: {str(e)}")
        # Return default keywords if there is an error
        return [f"{product_name} محصول", f"خرید {product_name}", f"بررسی {product_name}"]


def generate_dynamic_tone_for_article(product_name,):
    personalities = [
    "ENFP", "INFP", "ENTP", "INTP", "ENFJ", "INFJ", "ENTJ", "INTJ",
    "ESFP", "ISFP", "ESTP", "ISTP", "ESFJ", "ISFJ", "ESTJ", "ISTJ"
    ]
    selected_personality = random.choice(personalities)
    # AI prompt for generating the tone
    prompt = (
        f"Generate a clean and concise tone for writing an engaging product description for the product '{product_name}'. "
        f"The tone should evoke emotions and create a personal connection with the reader.suitable for personality type '{selected_personality}'. "
        f"For this product, imagine the target audience and write the tone part that reflects their emotions and desires. "
        f"Use informal language, include human-like anecdotes,idioms, rhetorical phrases and questions, and emotional language. "
        f"Ensure the tone is persuasive.the answer should be an optimized prompt to gpt4 to specify tone of an article. Avoid extra characters or explanations in the output."
    )

    # Get dynamic tone and content style from AI
    dynamic_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )

    # Ensure the output is clean and only contains the tone part
    dynamic_tone = dynamic_response.choices[0].message.content.strip()

    return dynamic_tone


# Step 3: Write an article optimized for SEO using the detected keywords
def generate_article_with_keywords(product, keywords, internal_links):
    product_name = product['name']
    keyword_str = ", ".join(keywords)
    internal_links_str = ", ".join([f"<a href='{link['url']}'>{link['name']}</a>" for link in internal_links])

    ''' # Optimized GPT-4 prompt for generating the article
    prompt = (
    f"Write a 300-500 word SEO-optimized product description for '{product_name}' using the following keywords: {keyword_str}. "
    f"Begin with a short personal anecdote or story related to the product to create a genuine connection. "
    f"Use informal language and colloquialisms to make the tone feel casual and friendly. "
    f"Ask rhetorical questions to engage the reader and make the text conversational. "
    f"Incorporate emotional and sensory words to evoke a stronger connection with the product. "
    f"Mix up sentence lengths and use fragments where appropriate for emphasis. "
    f"Talk directly to the reader as if having a conversation, making the content feel more personalized. "
    f"Vary sentence structure to avoid repetition and make the text flow naturally, without keyword stuffing. "
    f"Use a broader range of transition words to keep the flow smooth and cohesive. "
    f"Structure the article with proper HTML, including headings like <h2>, <h3>, and tags such as <strong>, <p>, and <ul>. "
    f"Highlight unique features and benefits clearly, ensuring the text provides real value to the reader. "
    f"Include a genuine call to action and naturally recommend related products using internal links: {internal_links_str}. "
    f"Optimize the content for Yoast SEO without sacrificing readability. "
    "Write in Persian, keeping the tone casual and relatable, avoiding overly formal language unless necessary.output clean HTML with no extra characters, symbols, explanations, or blank lines"
)'''
    
    # Part 1: Static structure for SEO and marketing optimization (remains constant across articles)
    structure_prompt = (
        f"Write a 300-500 word SEO-optimized product description for '{product_name}' using the following keywords: {keyword_str}. "
        f"Structure the article with proper HTML, including headings like <h2>, <h3>, and tags such as <strong>, <p>, and <ul>. "
        f"Highlight unique features and benefits clearly, ensuring the text provides real value to the reader. "
        f"Include a call to action and naturally recommend related products using internal links: {internal_links_str}. "
        f"Optimize the content for Yoast SEO without sacrificing readability. Write in Persian"
        "Ensure the output is clean HTML with no extra characters, symbols, explanations, or blank lines."
    )

    # Part 2: Dynamic tone and emotional engagement (customized for each product, generated by AI)
    dynamic_tone = generate_dynamic_tone_for_article(product_name)
    print('\ndynamic tone :'+dynamic_tone)

    # Combine the structure and the dynamic tone
    final_prompt = structure_prompt + "\n" + dynamic_tone



    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": final_prompt}],
        max_tokens=3000
    )

    article_content = response.choices[0].message.content
    return article_content

# Step 4: Automatically generate internal links based on product categories
def related_products(product, all_products):
    related_products = []
    category_ids = product.get('categories', [])
    
    for other_product in all_products:
        if other_product['id'] != product['id'] and any(cat in category_ids for cat in other_product.get('categories', [])):
            related_products.append({
                'name': other_product['name'],
                'url': other_product['permalink']
            })

    return related_products

# Function to post the generated article and Yoast SEO metadata to WooCommerce
def post_article_to_product(product_id, article_content, seo_title, meta_description, focus_keyword):
    # Data to update the product description and Yoast SEO fields
    update_data = {
        "description": article_content,
        "meta_data": [
            {
                "key": "_yoast_wpseo_title",
                "value": seo_title  # Setting the SEO Title
            },
            {
                "key": "_yoast_wpseo_metadesc",
                "value": meta_description  # Setting the Meta Description
            },
            {
                "key": "_yoast_wpseo_focuskw",
                "value": focus_keyword # Setting the Focus Keyword
            }
        ]
    }

    # Update the product via WooCommerce API
    update_response = requests.put(f"{wc_api_url}/{product_id}", json=update_data, params=wc_auth_params)
    
    if update_response.status_code == 200:
        print(f"Product {product_id} updated successfully with SEO data.")
    else:
        print(f"Failed to update product {product_id}: {update_response.text}")

# Function to generate SEO metadata using GPT, ensuring only a dictionary output
def generate_seo_metadata(product_name, product_description, keywords):
    # Join the keywords into a string for the prompt
    keywords_str = ", ".join(keywords)

    # AI prompt for generating SEO metadata
    prompt = (
        f"Generate SEO metadata for the product '{product_name}' using the following keywords: {keywords_str}. "
        f"Here is the product description: '{product_description}'. "
        f"Create a SEO-optimized title that encourages potential customers to click on the link. "
        f"Create a meta description between 121 and 156 characters that summarizes the product in an enticing way, "
        f"encouraging users to learn more and possibly make a purchase.Write it in Persian "
        f"Return the output as a clean Python dictionary with the keys 'seo_title', 'meta_description', and 'focus_keyword'. "
        f"Do not include any other text or characters in the output."
    )

    # Send the request to GPT
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    print("generated seo data :" +response.choices[0].message.content.replace("```python" , "").replace("```" , ""))
    # Get the response content
    metadata_response = response.choices[0].message.content.replace("```python" , "").replace("```" , "")

    # Try to parse the response as JSON
    try:
        metadata_dict = json.loads(metadata_response)  # Convert the response string to a Python dictionary
        if isinstance(metadata_dict, dict):
            return metadata_dict
        else:
            raise ValueError("The response is not a valid dictionary.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from AI response: {str(e)}")
        # Return default metadata if there is an error in parsing
        return {
            "seo_title": f"Buy {product_name} Online",
            "meta_description": f"Learn more about {product_name}. {', '.join(keywords[:3])} and more.",
            "focus_keyword": keywords[0] if keywords else product_name
        }

# Main function to handle product updates and review generation
def main():
    # Step 1: Retrieve all products
    products = get_all_products()

    #discription to woocommerce
    '''
    for product in products :
        product_name = product['name']
        product_id = product['id']
        print(product_id,product_name)
        generate_and_post_comments_for_product(product_id, product_name)
    '''
    #discription to woocommerce
    ''' # Step 2: Process each product
    for product in products:
        product_name = product['name']
        existing_description = product.get('description', '').strip()

        if existing_description:
            # Step 3: Append additional text if description exists
            print(f"Appending to description for product '{product_name}'...")
            generate_article_for_product(product, update=True)
        else:
            # Step 3: Add a new description if none exists
            print(f"Adding new description for product '{product_name}'...")
            generate_article_for_product(product, update=False)'''
    

    #generate to csv
    '''input_file_path = 'products.csv'
    output_file_path = 'updated_file.csv'

    # Read the existing CSV data
    with open(input_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Create a list to hold the updated rows
        updated_rows = []
        
        # Iterate over each row in the CSV
        for row in reader:
            # Add the new description column
            
            print('\n\n\n\n\n -----------------------------------------------------------------')
            print(f'product id {row['ID']} is processing\n\n\n\n')
            prompt = (f"برای محصول {row['post_title']} یک عنوان کوتاه و پربازده برای SEO در داخل پرانتز بنویس. سپس یک توضیحات بین 300 تا 500 کلمه با رعایت اصول SEO از نظر پلاگین Yoast بنویس. توضیحات باید شامل تگ‌های HTML مناسب مثل <h1>، <h2>، <strong> و <p> باشد. هیچ کاراکتر اضافی یا توضیحات خارج از این موارد در خروجی ننویس.")
            article_content = generate_text_with_g4f(prompt, max_tokens=1500)
           
            print('\n\n\n\n\n -----------------------------------------------------------------')
            print(article_content)
            print('\n\n\n\n\n -----------------------------------------------------------------')
            time.sleep(2)
            row['description'] = article_content
            updated_rows.append(row)

    # Write the updated data to a new CSV file
    with open(output_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = reader.fieldnames + ['description']  # Add new column to fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header
        writer.writeheader()
        
        # Write the updated rows
        writer.writerows(updated_rows)

    print(f'Updated CSV file saved as {output_file_path}')'''
    
    products = get_all_products()
    for product in products:
        product_name = product['name']
        product_id = product['id']

        # Step 1: Generate SEO keywords for the product
        keywords = generate_keywords_for_product(product_name)
        print(f"Keywords for {product_name}: {keywords}")

        # Step 2: Generate internal links for the product
        internal_links = related_products(product, products)
        print(f"Internal links for {product_name}: {internal_links}")

        # Step 3: Write an article using the keywords and internal links
        article_content = generate_article_with_keywords(product, keywords, internal_links).replace("```html" , "")
        article_content = article_content.replace("```" , "")
        print(f"Generated article for {product_name}:\n{article_content}")
        # Step 4: create seo metadate
        seo_metadata = generate_seo_metadata(product_name,article_content,keywords)
        # Step 5 : Post the generated article back to WooCommerce
        post_article_to_product(product_id, article_content,seo_metadata['seo_title'],seo_metadata['meta_description'],focus_keyword= keywords[0])
if __name__ == "__main__":
    main()


