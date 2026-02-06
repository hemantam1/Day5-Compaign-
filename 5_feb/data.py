import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime, timedelta
import json

# Database Connection
engine = create_engine('mysql+mysqlconnector://root:Admin%40123@localhost/amazon_ads_db')

def generate_realistic_company_data():
    try:
        
        def random_date(start_days_ago, end_days_ago):
            return datetime.now() - timedelta(days=np.random.randint(end_days_ago, start_days_ago))

        # 1. Portfolios
        product_lines = ['Premium_Audio', 'Gaming_Accessories', 'Office_Setup', 'Mobile_Gear']
        p_ids = [str(uuid.uuid4()) for _ in range(len(product_lines))]
        df_p = pd.DataFrame({
            'id': p_ids,
            'name': product_lines,
            'budget_amount': np.random.uniform(20000, 50000, len(product_lines)),
            'budget_start': [random_date(400, 365).date() for _ in range(len(product_lines))],
            'budget_end': [(datetime.now() + timedelta(days=120)).date() for _ in range(len(product_lines))],
            'status': 'ENABLED',
            'created_at': [random_date(400, 365) for _ in range(len(product_lines))]
        })
        df_p.to_sql('portfolios', con=engine, if_exists='append', index=False)

        # 2. Campaigns
        c_ids = [str(uuid.uuid4()) for _ in range(40)]
        df_c = pd.DataFrame({
            'id': c_ids,
            'portfolio_id': np.random.choice(p_ids, 40),
            'name': [f'Electronics_Campaign_{i}' for i in range(40)],
            'type': np.random.choice(['SP', 'SB', 'SV'], 40, p=[0.6, 0.3, 0.1]),
            'status': np.random.choice(['ENABLED', 'PAUSED'], 40, p=[0.85, 0.15]),
            'daily_budget': np.random.uniform(100, 1000, 40),
            'targeting_type': np.random.choice(['AUTO', 'MANUAL'], 40),
            'bidding_strategy': 'DYNAMIC_DOWN_ONLY',
            'created_at': [random_date(365, 350) for _ in range(40)]
        })
        df_c.to_sql('campaigns', con=engine, if_exists='append', index=False)

        # 3. Products
        prod_count = 50
        prod_ids = [str(uuid.uuid4()) for _ in range(prod_count)]
        df_prod = pd.DataFrame({
            'id': prod_ids,
            'asin': [f"B0{uuid.uuid4().hex[:8].upper()}" for _ in range(prod_count)],
            'name': [f'Electronic_Gadget_{i}' for i in range(prod_count)],
            'price': np.random.uniform(40, 500, prod_count),
            'margin': 0.35,
            'category': 'Electronics',
            'created_at': [random_date(400, 365) for _ in range(prod_count)]
        })
        df_prod.to_sql('products', con=engine, if_exists='append', index=False)

        # 4. Campaign Products
        df_cp = pd.DataFrame({
            'id': [str(uuid.uuid4()) for _ in range(100)],
            'campaign_id': np.random.choice(c_ids, 100),
            'product_id': np.random.choice(prod_ids, 100),
            'bid': np.random.uniform(0.8, 3.5, 100),
            'status': 'ENABLED',
            'created_at': [random_date(350, 300) for _ in range(100)]
        })
        df_cp.to_sql('campaign_products', con=engine, if_exists='append', index=False)

        # 5. Performance Metrics (With Real Correlations)
        metrics = []
        dates = pd.date_range(end=datetime.now(), periods=365)
        
        
        for i, d in enumerate(dates):
            # Seasonality: Weekends pe sales 20% badh jati hai
            weekend_boost = 1.2 if d.weekday() >= 5 else 1.0
            # Monthly Trend: Month end mein sales thodi uptick hoti hai
            month_end_boost = 1.15 if d.day > 25 else 1.0
            # Yearly Growth: Brand purana hote hi trust badhta hai (Growth Factor)
            growth_factor = 1 + (i / 400) 

            for _ in range(100): 
                c_id = np.random.choice(c_ids)
                
                # BASE LOGIC:
                # 1. CPC varies daily ($0.7 to $2.2)
                cpc = round(np.random.uniform(0.7, 2.2), 2)
                
                # 2. Spend depends on budget + growth
                spend = np.random.uniform(20, 150) * growth_factor * weekend_boost
                
                # 3. Clicks = Spend / CPC
                clicks = max(1, int(spend / cpc))
                
                # 4. CTR depends on Clicks (usually 0.5% to 4%)
                ctr = round(np.random.uniform(0.008, 0.04), 4)
                impressions = int(clicks / ctr) if ctr > 0 else clicks * 50
                
                # 5. CVR (Conversion Rate) - Real companies have 3% to 12%
                cvr = round(np.random.uniform(0.03, 0.10) * month_end_boost, 3)
                
                # 6. Sales & Orders (Strongly Correlated to Clicks & CVR)
                orders = int(clicks * cvr)
                avg_order_value = np.random.uniform(50, 150)
                sales = round(orders * avg_order_value, 2)
                
                # Avoid zero division
                acos = round((spend / sales) * 100, 2) if sales > 0 else 0
                roas = round(sales / spend, 2) if spend > 0 else 0

                metrics.append({
                    'id': str(uuid.uuid4()),
                    'campaign_id': c_id,
                    'date': d.date(),
                    'impressions': impressions,
                    'clicks': clicks,
                    'spend': round(spend, 2),
                    'sales': sales,
                    'orders': orders,
                    'acos': acos,
                    'roas': roas,
                    'ctr': ctr,
                    'cpc': cpc,
                    'cvr': cvr
                })
        
        pd.DataFrame(metrics).to_sql('performance_metrics', con=engine, if_exists='append', index=False)
       

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        tables = ['performance_metrics', 'campaign_products', 'products', 'campaigns', 'portfolios', 'ai_recommendations', 'automation_rules']
        for t in tables:
            conn.execute(text(f"TRUNCATE TABLE {t};"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    generate_realistic_company_data()