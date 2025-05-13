# تحلیل کامل متن و تکمیل بخش‌های ناقص
import json

from SeoThisApi.SeoThisApi.main.utils import generate_text_with_g4f, get_all_products
from maintanance import get_gsc_data, initialize_gsc_service


def analyze_full_text(product_name, current_description):
    prompt = (
    f"current_description:'{current_description}'\n\n"
    f"Analyze structure of current_description for any abruptly unfinished sentences or incomplete paragraphs, especially toward the end of description. "
    f"Only write new text where there is an obvious cutoff or incomplete sentence, without adding extra information or modifying sections that appear complete. "
    f"Write the text in Persian, matching the tone and style. "
    f"Return the response in JSON format with each detected incomplete section as a dictionary containing:"
    f" - 'new_text': the missing text to complete the section"
    f" - 'insertion_index': the starting index in current_description (using Python string indexing) for where new_text should be inserted."
    f"Return an empty JSON list if all sections appear complete."
)
    response = generate_text_with_g4f(prompt, max_tokens=3000).replace('```json', '').replace('```', '')
    print('analyze_full_text response : '+response)
    return response

# تحلیل و بهبود تیترها (H tags) با داده‌های سرچ کنسول
def analyze_headings(product_name, current_description, search_queries):
    prompt = (
        f"Analyze and improve upto 2 headings (H tags) (if needed) in the product description for '{product_name}':\n\n"
        f"current_description:'{current_description}'\n\n"
        f"Based on the top search queries: {search_queries}, improve the headings to optimize for SEO including incorporating relevant keywords, improving readability, and increasing engagement.  "
        f"Ensure proper structure (H1, H2, H3) is maintained for content hierarchy.Write in persian"
        f"Only return the improved headings, without any extra words or characters, in a valid JSON format with 'new_text', 'start_pos_old_text', and 'end_pos_old_text'.if headings don't need optimization just answer with empty json "
    )
    response = generate_text_with_g4f(prompt, max_tokens=2000).replace('```json', '').replace('```', '')
    print('analyze_headings response : '+response)
    return response

# تحلیل پاراگراف‌ها و جایگزینی جملات با بهینه‌سازی SEO
def analyze_paragraphs(product_name, current_description):
    prompt = (
        f"Analyze the paragraphs in the product description for '{product_name}':\n\n"
        f"current_description:'{current_description}'\n\n"
        f"Identify upto 2 low-quality sentences and suggest SEO-optimized alternatives including incorporating relevant keywords, improving readability, and increasing engagement .Write it in Persian with same tone as discription is written. "
        f"Return the improved sentences, preserving the meaning and structure, with no extra characters or explanations. "
        f"seeReturn a valid JSON list with 'new_text', 'start_pos_old_text', and 'end_pos_old_text' for each sentence that needs improvement."
    )
    response = generate_text_with_g4f(prompt, max_tokens=2000).replace('```json', '').replace('```', '')
    print('analyze_paragraphs response : '+response)
    return response

# جایگزینی دقیق متن با استفاده از موقعیت‌ها
def replace_text_with_positions(description, updates):
    updates = sorted(updates, key=lambda x: x['start_pos_old_text'], reverse=True)

    for update in updates:
        new_text = update['new_text']
        start_pos = int(update['start_pos_old_text'])
        end_pos = int(update['end_pos_old_text'])

        description = description[:start_pos] + new_text + description[end_pos:]

    return description

# تابع اصلی برای مدیریت مراحل مختلف
def update_product_content(product_name, current_description, product_url, site_url, update_type, search_queries=None):
    if update_type == 'full_text':
        updates = json.loads(analyze_full_text(product_name, current_description))
        for update in updates:
            new_text = update['new_text']
            start_pos = int(update['insertion_index'])
            end_pos = int(update['insertion_index'])+len(new_text)
            updated_description = current_description[:start_pos] + new_text + current_description[end_pos:]
            
    elif update_type == 'headings':
        updates = json.loads(analyze_headings(product_name, current_description, search_queries))
        updated_description = replace_text_with_positions(current_description, updates)
    elif update_type == 'paragraphs':
        updates = json.loads(analyze_paragraphs(product_name, current_description))
        updated_description = replace_text_with_positions(current_description, updates)
    return updated_description





'''
site_url = 'https://kafshdoozakmug.com'
products = get_all_products()

for product in products:
    product_name = product['name']
    product_url = product['permalink']
    current_description = product['description']
    print('\n\n\n'+current_description+'\n\n\n\n')
    print(f"Processing '{product_name}'...")

    # Update content based on GSC data
    #updated_content = update_product_content(product_name, current_description, product_url, site_url)
    
    # Analyze and update internal links based on related products
    search_queries = get_gsc_data(initialize_gsc_service(), site_url, product_url)

    updated_content = update_product_content(product_name, current_description, product_url, site_url, "full_text", search_queries)
    print('updated content:'+updated_content)'''



current_description = '''
updated content:<p><strong><a href="https://kafshdoozakmug.com/product-category/%d9%87%d9%85%d9%87-%d9%85%d8%ad%d8%b5%d9%88%d9%84%d8%a7%d8%aa/%d9%85%d8%a7%da%af/%d9%85%d8%a7%da%af-%d8%b4%db%8c%d8%b4%d9%87-%d8%a7%db%8c/">فنجان قهوه خوری</a></strong> مجموعه 2 عددی یک مجموعه از دو فنجان قهوه است که به طور معمول برای سرو قهوه در خانه یا محل کار استفاده می‌شود. در زیر به برخی از ویژگی‌های فنجان قهوه‌خوری مجموعه 2 عددی اشاره می‌کنم:</p>
<p><strong>جنس و طراحی:</strong></p>
<ul>
<li>جنس: فنجان‌های قهوه‌خدر دمای مناسب برای مدت زمان طولانی‌تر فراهم می‌کند.، از جمله سرامیک، پرچین یا شیشه. هر جنس ممکن است ویژگی‌های منحصر به فردی را در ارائه حفظ حرارت و ظاهر فنجان داشته باشد.</li>
<li>طراحی: فنجان‌های قهوه‌خوری معمولاً دارای طراحی زیبا و جذابی هستند. طرح‌ها و الگوهای مختلفی می‌توانند بر روی آنها قرار گیرند، از جمله رنگارنگ، ساده، مینیمالیستی و یا با الهام از فرهنگ‌ها و سبک‌های خاص.</li>
</ul>
<p><strong>ظرفیت و اندازه:</strong></p>
<ul>
<li>ظرفیت: فنجان‌های قهوه‌خوری معمولاً برای سرو یک فنجان قهوه طراحی شده‌اند. ظرفیت استاندارد برای یک فنجان قهوه معمولاً حدود 150 تا 250 میلی‌لیتر است، اما ممکن است بسته به طراحی و سبک فنجان، ظرفیتی متفاوت داشته باشند.</li>
<li>اندازه: فنجان‌های قهوه‌خوری ممکن است اندازه‌های مختلفی داشته باشند. برخی از آنها بزرگتر و سبک‌تر هستند و برخی دیگر کوچکتر و جمع و جورتر. انتخاب اندازه بستگی به ترجیح شخصی شما دارد و می‌توانید بر اساس نیازهای خود اندازه مورد نظر را انتخاب کنید.</li>
</ul>
<h3>برخی ویژگی‌های فنجان قهوه خوری</h3>
<ul>
<li>دستگیره: برخی از فنجان‌های قهوه‌خوری دارای دستگیره هستند که راحتی در نگهداری و حمل آنها را افزایش می‌دهد. دستگیره‌ها می‌توانند از جنس مشابه فنجان یا جنس دیگری ساخته شوند.</li>
<li>نگهداری حرارت: برخی از فنجان‌های قهوه‌خوری دارای ویژگی نگهداری حرارت هستند که امکان حفظ دمای قهویگاهای درست استفاده از اطلاعات برای مقصود مشتری را فراهم می کند. همچنین، برخی فنجان‌های قهوه‌خوری مجموعه 2 عددی قابلیت استفاده در ماشین‌های قهوه‌ساز نیز دارند.</li>
</ul>
<p><strong>نتیجه گیری</strong></p>'''

site_url = 'https://kafshdoozakmug.com'
products = get_all_products()
for i in range(1,5):
    product_name = 'name'
    product_url = 'link'
    print('\n\n\n'+current_description+'\n\n\n\n')
    print(f"Processing '{product_name}'...")

    # Update content based on GSC data
    # updated_content = update_product_content(product_name, current_description, product_url, site_url)
    
    # Analyze and update internal links based on related products
    #search_queries = get_gsc_data(initialize_gsc_service(), site_url, product_url)
    updated_content = update_product_content(product_name, current_description, product_url, site_url, "full_text",)
    print('updated content:'+updated_content)