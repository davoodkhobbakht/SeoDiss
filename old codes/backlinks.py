# backlinks.py
import requests

# SEMrush API configuration
SEMRUSH_API_KEY = 'your_semrush_api_key'
SEMRUSH_API_URL = 'https://api.semrush.com/analytics/v1/'

# Get backlinks for a specific product URL
def get_backlinks_for_product(product_url):
    params = {
        'type': 'backlinks',
        'target': product_url,
        'export_columns': 'source_url, anchor, backlinks',
        'key': SEMRUSH_API_KEY
    }
    response = requests.get(SEMRUSH_API_URL, params=params)
    if response.status_code == 200:
        return [line.split(',') for line in response.text.splitlines()]
    else:
        print(f"Failed to get backlinks for {product_url}: {response.text}")
        return []

# Analyze backlink quality (simple version based on number of backlinks and domain authority)
def analyze_backlink_quality(backlinks):
    high_quality = []
    low_quality = []

    for backlink in backlinks:
        source_url = backlink[0]
        anchor_text = backlink[1]
        num_backlinks = int(backlink[2])

        # Simple rule: backlinks with more than 5 links are considered high-quality (can be extended)
        if num_backlinks > 5:
            high_quality.append((source_url, anchor_text))
        else:
            low_quality.append((source_url, anchor_text))

    return high_quality, low_quality

# Example usage of the functions
if __name__ == "__main__":
    product_url = 'https://example.com/product-a'

    # Get backlinks for the product
    backlinks = get_backlinks_for_product(product_url)
    print(f"Backlinks for {product_url}:\n{backlinks}")

    # Analyze the quality of the backlinks
    high_quality_backlinks, low_quality_backlinks = analyze_backlink_quality(backlinks)
    print(f"High-quality Backlinks:\n{high_quality_backlinks}")
    print(f"Low-quality Backlinks:\n{low_quality_backlinks}")
