"""Test ML Features Demo"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pylint: disable=wrong-import-position
from django.db import connection  # noqa: E402
# pylint: enable=wrong-import-position

print('='*65)
print('       MACHINE LEARNING FEATURES DEMONSTRATION')
print('='*65)

with connection.cursor() as cursor:
    # 1. Content-Based Recommendations
    print('\n1. CONTENT-BASED RECOMMENDATIONS (Product ID: 10):')
    cursor.execute('SELECT * FROM ml_content_based_recommendations(10, 4);')
    for r in cursor.fetchall():
        print(f'   -> {r[1][:40]} (Score: {r[2]}, {r[3]})')

    # 2. Demand Forecasting
    print('\n2. DEMAND FORECAST (Product ID: 5, Next 5 Days):')
    cursor.execute('SELECT * FROM ml_demand_forecast(5, 5);')
    for r in cursor.fetchall():
        print(f'   {r[0]}: Predicted {r[1]} units (Range: {r[2]}-{r[3]}) - {r[4]}')

    # 3. Customer Clustering
    print('\n3. CUSTOMER CLUSTERS (Top 5):')
    cursor.execute('SELECT * FROM ml_customer_clusters() LIMIT 5;')
    for r in cursor.fetchall():
        print(f'   {r[1]}: {r[2]} | Orders: {r[3]} | Spent: Rs.{r[4]:.0f} | Category: {r[6]}')

    # 4. Review Sentiment Analysis
    print('\n4. REVIEW SENTIMENT ANALYSIS:')
    reviews = [
        'Excellent quality product! Best purchase ever. Highly recommended.',
        'Product was average, nothing special.',
        'Worst product. Fake and damaged. Waste of money.'
    ]
    for review in reviews:
        cursor.execute('SELECT * FROM ml_review_sentiment(%s);', [review])
        r = cursor.fetchone()
        short_review = review[:40] + '...' if len(review) > 40 else review
        print(f'   "{short_review}"')
        print(f'      -> Score: {r[0]}% | Sentiment: {r[1]} | Pos:{r[2]} Neg:{r[3]}')

    # 5. Product Performance Prediction
    print('\n5. PRODUCT PERFORMANCE (Product ID: 5):')
    cursor.execute('SELECT * FROM ml_predict_product_performance(5);')
    r = cursor.fetchone()
    print(f'   Performance Score: {r[0]} (Grade: {r[1]})')
    print(f'   Sales Velocity: {r[2]} per week')
    print(f'   Review Quality: {r[3]}/5')
    print(f'   Stock Health: {r[4]}')
    print(f'   Recommendation: {r[5]}')

    # 6. Dynamic Pricing Analysis
    print('\n6. DYNAMIC PRICING ANALYSIS (Product ID: 10):')
    cursor.execute('SELECT * FROM ml_dynamic_pricing_analysis(10);')
    r = cursor.fetchone()
    print(f'   Current Price: Rs.{r[0]:.2f}')
    print(f'   Market Position: {r[1]}')
    print(f'   Category Avg: Rs.{r[2]:.2f}')
    print(f'   Demand Level: {r[3]}')
    print(f'   Analysis: {r[4]}')

    # 7. ML Views Summary
    print('\n7. ML VIEWS SUMMARY:')
    cursor.execute('SELECT COUNT(*) FROM ml_product_recommendations_summary;')
    print(f'   Product Recommendations: {cursor.fetchone()[0]} products analyzed')
    cursor.execute('SELECT COUNT(*) FROM ml_customer_ltv_summary;')
    print(f'   Customer LTV: {cursor.fetchone()[0]} customers analyzed')
    cursor.execute('SELECT COUNT(*) FROM ml_category_performance;')
    print(f'   Category Performance: {cursor.fetchone()[0]} categories analyzed')
    cursor.execute('SELECT COUNT(*) FROM ml_vendor_intelligence;')
    print(f'   Vendor Intelligence: {cursor.fetchone()[0]} vendors analyzed')

print('\n' + '='*65)
print('       ML FEATURES WORKING SUCCESSFULLY!')
print('='*65)
