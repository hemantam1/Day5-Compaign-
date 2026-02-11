import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime, timedelta

# 1. Database Connection
engine = create_engine('mysql+pymysql://root:Admin%40123@localhost/amazon_ads_db')

def generate_bid_data():
    try:
        # Reusing your core structure
        c_ids = [str(uuid.uuid4()) for _ in range(5)]
        prod_ids = [str(uuid.uuid4()) for _ in range(20)]
        
        metrics = []
        dates = pd.date_range(end=datetime.now(), periods=1095) # 3 Years

        for d in dates:
            is_weekend = 1 if d.weekday() >= 5 else 0
            is_salary_day = 1 if (d.day <= 5 or d.day >= 25) else 0
            
            weekend_boost = 2.8 if is_weekend else 1.0
            payday_boost = 1.30 if is_salary_day else 1.0
            
            for c_id in c_ids:
                p_id = np.random.choice(prod_ids)
                daily_budget = np.random.uniform(800, 3000)
                price = np.random.choice([499, 999, 1499, 2499])

                # Current Bid & Market State
                current_bid = round(np.random.uniform(1.5, 5.5), 2)
                comp_pressure = np.random.uniform(0.5, 1.5)
                organic_rank = np.random.randint(1, 50)
                
                # Impact Logic (Sales depend on Bid Strength)
                bid_impact = np.log1p(current_bid) * 1.5 
                base_sales = (daily_budget * 0.15) * weekend_boost * payday_boost * bid_impact
                sales = round(base_sales * np.random.normal(1, 0.05), 2)
                
                spend = round(daily_budget * np.random.uniform(0.8, 0.95), 2)
                clicks = max(1, int(spend / (current_bid * comp_pressure)))
                orders = int(sales / price) if sales > price else 0

                # Target Label (The "Optimal" Bid for training)
                if (orders > 5 and (spend/sales) < 0.20):
                    optimal_bid = current_bid * 1.1 
                elif (spend/max(1,sales) > 0.40):
                    optimal_bid = current_bid * 0.9 
                else:
                    optimal_bid = current_bid

                metrics.append({
                    'date': d.date(),
                    'campaign_id': c_id,
                    'product_id': p_id,
                    'is_weekend': is_weekend,
                    'is_salary_day': is_salary_day,
                    'daily_budget': daily_budget,
                    'current_bid': current_bid,
                    'organic_rank': organic_rank,
                    'competitor_pressure': round(comp_pressure, 2),
                    'clicks': clicks,
                    'spend': spend,
                    'sales': sales,
                    'orders': orders,
                    'cvr': round(orders/clicks, 4) if clicks > 0 else 0,
                    'acos': round((spend/sales)*100, 2) if sales > 0 else 0,
                    'optimal_bid': round(optimal_bid, 2)
                })

        df = pd.DataFrame(metrics)
        df = df.sort_values(['campaign_id', 'date'])

        # --- 🚀 ADVANCED FEATURE ENGINEERING START ---
        
        # 1. Performance Lags (Kal ki performance dekh kar aaj bid change hogi)
        # Shift(1) ensures no data leakage
        df['sales_lag_1'] = df.groupby('campaign_id')['sales'].shift(1)
        df['acos_lag_1'] = df.groupby('campaign_id')['acos'].shift(1)
        df['spend_lag_1'] = df.groupby('campaign_id')['spend'].shift(1)
        
        # 2. Efficiency Ratios
        df['bid_budget_ratio'] = df['current_bid'] / df['daily_budget']
        df['roas_lag_1'] = (df['sales_lag_1'] / (df['spend_lag_1'] + 1)).round(2)
        
        # 3. Market Intensity Index (Rank and Competition together)
        df['ad_intensity_index'] = (df['competitor_pressure'] * df['organic_rank']).round(2)
        
        # 4. Moving Averages (7-day trends)
        df['avg_cvr_7d'] = df.groupby('campaign_id')['cvr'].transform(lambda x: x.shift(1).rolling(7).mean())
        df['avg_acos_7d'] = df.groupby('campaign_id')['acos'].transform(lambda x: x.shift(1).rolling(7).mean())
        
        # 5. Budget Utilization (Spend velocity)
        df['spend_velocity'] = df['spend_lag_1'] / df['daily_budget']

        # --- ADVANCED FEATURE ENGINEERING END ---
        
        df.fillna(0, inplace=True)
        df.to_sql('bid_optimization_metrics', con=engine, if_exists='replace', index=False)
        
        print("✅ Data2.py: Advanced Bid Optimization Data Generated!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_bid_data()