''' from bs4 import BeautifulSoup

# متن HTML که شامل تگ‌های div است
html_content = '''       '''

# استفاده از BeautifulSoup برای تجزیه متن HTML
soup = BeautifulSoup(html_content, 'html.parser')

# حذف تمامی تگ‌های div
for div in soup.find_all('div'):
    div.unwrap()

# خروجی متن بدون تگ‌های div
cleaned_text = soup.extract()

print(cleaned_text)
print('hello world') '''


import pandas as pd
from bs4 import BeautifulSoup

# Function to clean descriptions by removing div tags
def remove_div_tags(description):
    if pd.isna(description):
        return description  # If the description is NaN, return it as is
    soup = BeautifulSoup(description, 'html.parser')
    for div in soup.find_all('div'):
        div.unwrap()  # Remove only the div tags, keep the inner content
    return soup.extract()

# Load the CSV file (replace 'your_file.csv' with the actual file name)
df = pd.read_csv('your_file.csv')

# Assuming the product descriptions are in a column named 'description'
# If the column has a different name, change 'description' to the correct one
df['description'] = df['description'].apply(remove_div_tags)

# Save the cleaned data to a new CSV file
df.to_csv('cleaned_products.csv', index=False)

print("Div tags removed and cleaned data saved to 'cleaned_products.csv'.")
