import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime, timedelta

# 1. Database Connection (Naya DB ya Table name bhi change kar sakte hain)
engine = create_engine('mysql+pymysql://root:Admin%40123@localhost/amazon_ads_db')

def generate_bid_data():
    try:
        # Helper: Dates
        def random_date(start_days_ago, end_days_ago):
            return datetime.now() - timedelta(days=np.random.randint(end_days_ago, start_days_ago))

        # --- Reusing IDs and Logic from your core structure ---
        c_ids = [str(uuid.uuid4()) for _ in range(5)]
        prod_ids = [str(uuid.uuid4()) for _ in range(20)]
        
        metrics = []
        dates = pd.date_range(end=datetime.now(), periods=1095) # 3 Years

        for d in dates:
            is_weekend = 1 if d.weekday() >= 5 else 0
            is_salary_day = 1 if (d.day <= 5 or d.day >= 25) else 0
            
            # Priority Boosts (Keeping consistency with your previous model)
            weekend_boost = 2.8 if is_weekend else 1.0
            payday_boost = 1.30 if is_salary_day else 1.0
            
            for c_id in c_ids:
                p_id = np.random.choice(prod_ids)
                daily_budget = np.random.uniform(800, 3000)
                price = np.random.choice([499, 999, 1499, 2499])

                # --- BID OPTIMIZATION SPECIFIC FEATURES ---
                # 1. Current Bid (Current market state)
                current_bid = round(np.random.uniform(1.5, 5.5), 2)
                
                # 2. Competitor Pressure (High pressure = Higher CPC)
                comp_pressure = np.random.uniform(0.5, 1.5)
                
                # 3. Organic Rank (If organic rank is good, we might bid less)
                organic_rank = np.random.randint(1, 50)
                
                # --- IMPACT LOGIC (Relating features) ---
                # Sales depend on Bid Strength + Budget + External factors
                bid_impact = np.log1p(current_bid) * 1.5 
                base_sales = (daily_budget * 0.15) * weekend_boost * payday_boost * bid_impact
                sales = round(base_sales * np.random.normal(1, 0.05), 2)
                
                spend = round(daily_budget * np.random.uniform(0.8, 0.95), 2)
                clicks = max(1, int(spend / (current_bid * comp_pressure)))
                orders = int(sales / price) if sales > price else 0

                # --- Target Label (The "Perfect" Bid for the next day) ---
                # This is what your model will eventually try to predict
                if (orders > 5 and (spend/sales) < 0.20):
                    optimal_bid = current_bid * 1.1 # Performance achha hai, bid badhao
                elif (spend/max(1,sales) > 0.40):
                    optimal_bid = current_bid * 0.9 # ACOS high hai, bid kam karo
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
                    'optimal_bid': round(optimal_bid, 2) # Target Variable
                })

        df = pd.DataFrame(metrics)
        
        # --- Advanced Features (Stable Relationships) ---
        df = df.sort_values(['campaign_id', 'date'])
        df['avg_cvr_7d'] = df.groupby('campaign_id')['cvr'].transform(lambda x: x.shift(1).rolling(7).mean())
        df['spend_velocity'] = df['spend'] / df['daily_budget'] # Budget utilization
        
        df.fillna(0, inplace=True)
        df.to_sql('bid_optimization_metrics', con=engine, if_exists='replace', index=False)
        
        print("✅ Data2.py: Bid Optimization Data Generated successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_bid_data()