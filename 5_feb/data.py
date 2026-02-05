import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import uuid
from datetime import datetime, timedelta
import json

# Database Connection
engine = create_engine('mysql+mysqlconnector://root:Admin%40123@localhost/amazon_ads_db')

def generate_final_ml_data():
    try:
        

        # 1. Portfolios
        p_ids = [str(uuid.uuid4()) for _ in range(10)]
        df_p = pd.DataFrame({
            'id': p_ids,
            'name': [f'Portfolio_{i}' for i in range(10)],
            'budget_amount': np.random.uniform(10000, 50000, 10),
            'budget_start': datetime.now().date() - timedelta(days=365),
            'budget_end': datetime.now().date() + timedelta(days=30),
            'status': 'ENABLED',
            'created_at': datetime.now()
        })
        df_p.to_sql('portfolios', con=engine, if_exists='append', index=False)

        # 2. Campaigns
        c_ids = [str(uuid.uuid4()) for _ in range(50)]
        df_c = pd.DataFrame({
            'id': c_ids,
            'portfolio_id': np.random.choice(p_ids, 50),
            'name': [f'Campaign_{i}' for i in range(50)],
            'type': np.random.choice(['SP', 'SB', 'SV'], 50),
            'status': 'ENABLED',
            'daily_budget': np.random.uniform(100, 500, 50),
            'targeting_type': 'AUTO',
            'bidding_strategy': 'DYNAMIC_UP_AND_DOWN',
            'created_at': datetime.now()
        })
        df_c.to_sql('campaigns', con=engine, if_exists='append', index=False)

        # 3. Products
        prod_ids = [str(uuid.uuid4()) for _ in range(100)]
        df_prod = pd.DataFrame({
            'id': prod_ids,
            'asin': [f'B07{str(uuid.uuid4())[:7].upper()}' for _ in range(100)],
            'name': [f'Product_{i}' for i in range(100)],
            'price': np.random.uniform(50, 1000, 100),
            'margin': np.random.uniform(0.15, 0.40, 100),
            'category': 'Electronics',
            'created_at': datetime.now()
        })
        df_prod.to_sql('products', con=engine, if_exists='append', index=False)

        # 4. Campaign Products
        df_cp = pd.DataFrame({
            'id': [str(uuid.uuid4()) for _ in range(100)],
            'campaign_id': c_ids * 2,
            'product_id': np.random.choice(prod_ids, 100),
            'bid': 1.0, 'status': 'ENABLED', 'created_at': datetime.now()
        })
        df_cp.to_sql('campaign_products', con=engine, if_exists='append', index=False)

        # 5. Performance Metrics (With ACOS Capping)

        metrics = []
        dates = pd.date_range(end=datetime.now(), periods=365)
        
        for c_id in c_ids:
            base_cvr = np.random.uniform(0.02, 0.08)
            for d in dates:
                day_effect = 1.2 if d.weekday() >= 5 else 1.0
                spend = np.random.uniform(20, 100) * day_effect
                clicks = int(spend / np.random.uniform(0.5, 2.0))
                
                is_anomaly = np.random.random() < 0.02
                if is_anomaly:
                    sales = spend * np.random.uniform(0.01, 0.05)
                else:
                    sales = spend * np.random.uniform(4, 10)
                
                orders = int(clicks * base_cvr)
                
                raw_acos = (spend/sales)*100 if sales > 0 else 999.99
                safe_acos = min(raw_acos, 999.99)
                
                metrics.append({
                    'id': str(uuid.uuid4()),
                    'campaign_id': c_id,
                    'date': d,
                    'impressions': clicks * 50,
                    'clicks': clicks,
                    'spend': round(spend, 2),
                    'sales': round(sales, 2),
                    'orders': orders,
                    'acos': round(safe_acos, 2),
                    'roas': round(sales/spend, 2) if spend > 0 else 0,
                    'ctr': 0.02, 
                    'cpc': round(spend/clicks, 2) if clicks > 0 else 0,
                    'cvr': base_cvr
                })

        # CHANGE HERE: replace=True taaki 50,000 rows mil jayein
        df_metrics = pd.DataFrame(metrics).sample(n=50000, replace=True)
        # Nayi UUIDs dena zaroori hai kyunki replace=True se IDs repeat ho jayengi
        df_metrics['id'] = [str(uuid.uuid4()) for _ in range(50000)]
        
        df_metrics.to_sql('performance_metrics', con=engine, if_exists='append', index=False)

        # 6. AI Recommendations
        df_ai = pd.DataFrame({
            'id': [str(uuid.uuid4()) for _ in range(50)],
            'entity_type': 'campaign',
            'entity_id': np.random.choice(c_ids, 50),
            'recommendation_type': 'BID_UP',
            'current_value': '1.5', 'suggested_value': '2.0',
            'expected_impact': json.dumps({"sales_up": "10%"}),
            'confidence_score': 0.85,
            'status': 'pending',
            'created_at': datetime.now()
        })
        df_ai.to_sql('ai_recommendations', con=engine, if_exists='append', index=False)

        # 7. Automation Rules
        df_rules = pd.DataFrame({
            'id': [str(uuid.uuid4()) for _ in range(10)],
            'name': 'High ACOS Rule',
            'condition': 'acos > 40%',
            'action': 'PAUSE',
            'priority': 'HIGH',
            'enabled': True,
            'created_at': datetime.now()
        })
        df_rules.to_sql('automation_rules', con=engine, if_exists='append', index=False)

        print("\n" + "="*50)
        print("Done")
        print("="*50)

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    generate_final_ml_data()