import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime, timedelta

# ---------------------------
# 1. Database Connection
# ---------------------------
# Database credentials aapke original code ke hisaab se set hain
engine = create_engine('mysql+pymysql://root:Admin%40123@localhost/amazon_ads_db')

def generate_3_year_realistic_data():
    try:
        # Helper: random date generator for initial creation dates
        def random_date(start_days_ago, end_days_ago):
            return datetime.now() - timedelta(days=np.random.randint(end_days_ago, start_days_ago))

        # ---------------------------
        # 2. Portfolios (4 Main Categories)
        # ---------------------------
        product_lines = ['Premium_Audio', 'Gaming_Accessories', 'Office_Setup', 'Mobile_Gear']
        p_ids = [str(uuid.uuid4()) for _ in range(len(product_lines))]
        df_p = pd.DataFrame({
            'id': p_ids,
            'name': product_lines,
            'budget_amount': np.random.uniform(50000, 100000, len(product_lines)),
            'budget_start': [random_date(1200, 1100).date() for _ in range(len(product_lines))],
            'budget_end': [(datetime.now() + timedelta(days=365)).date() for _ in range(len(product_lines))],
            'status': 'ENABLED',
            'created_at': [random_date(1200, 1100) for _ in range(len(product_lines))]
        })
        df_p.to_sql('portfolios', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 3. Campaigns (5 Sequential Phases over 3 Years)
        # ---------------------------
        c_ids = [str(uuid.uuid4()) for _ in range(5)]
        df_c = pd.DataFrame({
            'id': c_ids,
            'portfolio_id': [np.random.choice(p_ids) for _ in range(5)],
            'name': [f'Growth_Strategy_Phase_{i+1}' for i in range(5)],
            'type': np.random.choice(['SP', 'SB'], 5),
            'status': 'ENABLED',
            'daily_budget': np.random.uniform(400, 1200, 5), # Slightly higher budget for 3 yr scale
            'targeting_type': np.random.choice(['AUTO', 'MANUAL'], 5),
            'bidding_strategy': 'DYNAMIC_DOWN_ONLY',
            'created_at': [random_date(1200, 1100) for _ in range(5)]
        })
        df_c.to_sql('campaigns', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 4. Products
        # ---------------------------
        prod_count = 50
        prod_ids = [str(uuid.uuid4()) for _ in range(prod_count)]
        df_prod = pd.DataFrame({
            'id': prod_ids,
            'asin': [f"B0{uuid.uuid4().hex[:8].upper()}" for _ in range(prod_count)],
            'name': [f'Electronic_Gadget_{i}' for i in range(prod_count)],
            'price': np.round(np.random.uniform(40, 500, prod_count), 2),
            'margin': 0.35,
            'category': 'Electronics',
            'created_at': [random_date(1200, 1100) for _ in range(prod_count)]
        })
        df_prod.to_sql('products', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 5. Campaign Products (Bridge Table)
        # ---------------------------
        df_cp = pd.DataFrame({
            'id': [str(uuid.uuid4()) for _ in range(100)],
            'campaign_id': np.random.choice(c_ids, 100),
            'product_id': np.random.choice(prod_ids, 100),
            'bid': np.round(np.random.uniform(0.8, 3.5, 100), 2),
            'status': 'ENABLED',
            'created_at': [random_date(1100, 1000) for _ in range(100)]
        })
        df_cp.to_sql('campaign_products', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 6. Performance Metrics (1095 Days / 3 Years)
        # ---------------------------
        metrics = []
        total_days = 1095 
        dates = pd.date_range(end=datetime.now(), periods=total_days)
        days_per_phase = total_days // 5

        for i, d in enumerate(dates):
            # Decide which campaign is active based on time
            phase_idx = min(i // days_per_phase, 4) 
            c_id = c_ids[phase_idx]

            # Seasonal & Growth Factors
            is_weekend = 1 if d.weekday() >= 5 else 0
            weekend_boost = 1.30 if is_weekend == 1 else 1.0
            month_end_boost = 1.25 if d.day > 25 else 1.0
            
            # Yearly Growth Factor: Sales improve roughly 10-15% per year
            yearly_growth = 1 + (i / 800) 

            # Core Advertising Logic (Correlated)
            # CPC fluctuates slightly
            cpc = round(np.random.uniform(0.9, 1.8), 2)
            
            # Spend depends on growth and seasonality
            base_spend = np.random.uniform(150, 450)
            spend = round(base_spend * yearly_growth * weekend_boost, 2)
            
            # Clicks = Spend / CPC
            clicks = max(1, int(spend / cpc))
            
            # CTR between 1.5% and 4.5%
            ctr = round(np.random.uniform(0.015, 0.045), 4)
            impressions = int(clicks / ctr)

            # Conversion Rate (CVR) improves with phases (campaign optimization)
            base_cvr = 0.05 + (phase_idx * 0.008)
            cvr = round(np.random.uniform(base_cvr, base_cvr + 0.02) * month_end_boost, 3)
            orders = int(np.round(clicks * cvr))

            # Fetch product price for sales calculation
            product_id = np.random.choice(prod_ids)
            price = df_prod.loc[df_prod['id'] == product_id, 'price'].values[0]
            
            sales = round(orders * price, 2) if orders > 0 else 0.0
            acos = round((spend / sales) * 100, 2) if sales > 0 else 0.0
            roas = round(sales / spend, 2) if spend > 0 else 0.0

            metrics.append({
                'id': str(uuid.uuid4()),
                'campaign_id': c_id,
                'date': d.date(),
                'is_weekend': is_weekend,
                'impressions': impressions,
                'clicks': clicks,
                'spend': spend,
                'sales': sales,
                'orders': orders,
                'acos': acos,
                'roas': roas,
                'ctr': ctr,
                'cpc': cpc,
                'cvr': cvr,
                'product_id': product_id
            })

        # ---------------------------
        # 7. Feature Engineering Layer
        # ---------------------------
        master_df = pd.DataFrame(metrics)
        # Sorting is CRITICAL for Lags
        master_df = master_df.sort_values(by=['campaign_id', 'date'])

        # Create Lags (Previous values for prediction)
        master_df['sales_lag_1'] = master_df.groupby('campaign_id')['sales'].shift(1)
        master_df['sales_lag_7'] = master_df.groupby('campaign_id')['sales'].shift(7)
        master_df['roas_lag_1'] = master_df.groupby('campaign_id')['roas'].shift(1)
        master_df['acos_lag_1'] = master_df.groupby('campaign_id')['acos'].shift(1)

        # Rolling Mean for 7 days trend
        master_df['rolling_mean_7'] = master_df.groupby('campaign_id')['sales'].shift(1).rolling(window=7).mean()

        # Fill first few days NaNs with 0
        master_df.fillna(0, inplace=True)

        # Save to Database
        master_df.to_sql('performance_metrics', con=engine, if_exists='append', index=False)
        
        print(f"✅ Success: Generated {total_days} days (3 Years) of realistic data.")
        print(f"Total Rows in Performance Metrics: {len(master_df)}")

    except Exception as e:
        print(f"❌ ERROR in Data Generation: {e}")

# ---------------------------
# 8. Main Execution Logic
# ---------------------------
if __name__ == "__main__":
    with engine.begin() as conn:
        # Stop constraints to truncate safely
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        tables = ['performance_metrics', 'campaign_products', 'products', 'campaigns', 'portfolios']
        for t in tables:
            conn.execute(text(f"TRUNCATE TABLE {t};"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        print("🗑️ Database Cleared.")

    generate_3_year_realistic_data()