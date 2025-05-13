# trends.py
from pytrends.request import TrendReq
import pandas as pd

# Initialize Pytrends connection
def initialize_pytrends(region='IR', hl='fa-IR'):
    pytrends = TrendReq(hl=hl, tz=330)
    return pytrends

# Get trending searches for the region
def get_trending_keywords(region='IR'):
    pytrends = initialize_pytrends(region)
    trending_data = pytrends.trending_searches(pn=region)
    return trending_data.head().values.flatten().tolist()

# Get interest over time for specific keywords
def get_interest_over_time(keywords, region='IR', timeframe='today 1-m'):
    pytrends = initialize_pytrends(region)
    pytrends.build_payload(keywords, geo=region, timeframe=timeframe)
    interest_data = pytrends.interest_over_time()
    if not interest_data.empty:
        return interest_data.drop(labels=['isPartial'], axis='columns')
    return pd.DataFrame()

# Get interest by region for specific keywords
def get_interest_by_region(keywords, region='IR', timeframe='today 1-m'):
    pytrends = initialize_pytrends(region)
    pytrends.build_payload(keywords, geo=region, timeframe=timeframe)
    by_region = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
    return by_region

# Get related queries for specific keywords
def get_related_queries(keyword, region='IR', timeframe='today 1-m'):
    pytrends = initialize_pytrends(region)
    pytrends.build_payload([keyword], geo=region, timeframe=timeframe)
    related_queries = pytrends.related_queries()
    if keyword in related_queries:
        top_queries = related_queries[keyword]['top']
        return top_queries['query'].tolist() if top_queries is not None else []
    return []

# Get keyword suggestions
def get_keyword_suggestions(keyword):
    pytrends = initialize_pytrends()
    suggestions = pytrends.suggestions(keyword=keyword)
    return pd.DataFrame(suggestions)

# Example usage of the functions
if __name__ == "__main__":
    region = 'IR'

    # Get trending keywords
    trending_keywords = get_trending_keywords(region=region)
    print(f"Trending Keywords in {region}: {trending_keywords}")

    # Get interest over time for the first trending keyword
    if trending_keywords:
        interest_data = get_interest_over_time([trending_keywords[0]], region=region)
        print(f"Interest Over Time for '{trending_keywords[0]}':\n{interest_data}")

    # Get related queries for the first trending keyword
    if trending_keywords:
        related_queries = get_related_queries(trending_keywords[0], region=region)
        print(f"Related Queries for '{trending_keywords[0]}': {related_queries}")

    # Get keyword suggestions for a specific keyword
    keyword_suggestions = get_keyword_suggestions('Business Intelligence')
    print(f"Keyword Suggestions for 'Business Intelligence':\n{keyword_suggestions}")
