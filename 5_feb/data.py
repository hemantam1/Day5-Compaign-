import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime, timedelta

# ---------------------------
# 1. Database Connection
# ---------------------------
engine = create_engine('mysql+pymysql://root:Admin%40123@localhost/amazon_ads_db')

def generate_full_system_data():
    try:
        # Helper: Random date generator
        def random_date(start_days_ago, end_days_ago):
            return datetime.now() - timedelta(days=np.random.randint(end_days_ago, start_days_ago))

        # ---------------------------
        # 2. Portfolios
        # ---------------------------
        product_lines = ['Premium_Audio', 'Gaming_Accessories', 'Office_Setup', 'Mobile_Gear']
        p_ids = [str(uuid.uuid4()) for _ in range(len(product_lines))]
        df_p = pd.DataFrame({
            'id': p_ids,
            'name': product_lines,
            'budget_amount': np.random.uniform(500000, 1000000, len(product_lines)),
            'budget_start': [random_date(1200, 1100).date() for _ in range(4)],
            'budget_end': [(datetime.now() + timedelta(days=365)).date() for _ in range(4)],
            'status': 'ENABLED',
            'created_at': [random_date(1200, 1100) for _ in range(4)]
        })
        df_p.to_sql('portfolios', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 3. Campaigns
        # ---------------------------
        c_ids = [str(uuid.uuid4()) for _ in range(5)]
        df_c = pd.DataFrame({
            'id': c_ids,
            'portfolio_id': [np.random.choice(p_ids) for _ in range(5)],
            'name': [f'Growth_Strategy_Phase_{i+1}' for i in range(5)],
            'type': 'SP', 
            'status': 'ENABLED',
            'daily_budget': np.random.uniform(500, 3000, 5), # Range widened to show clear priority
            'targeting_type': np.random.choice(['AUTO', 'MANUAL'], 5, p=[0.4, 0.6]),
            'bidding_strategy': 'DYNAMIC_DOWN_ONLY',
            'created_at': [random_date(1200, 1100) for _ in range(5)]
        })
        df_c.to_sql('campaigns', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 4. Products
        # ---------------------------
        prod_count = 20
        prod_ids = [str(uuid.uuid4()) for _ in range(prod_count)]
        df_prod = pd.DataFrame({
            'id': prod_ids,
            'asin': [f"B0{uuid.uuid4().hex[:8].upper()}" for _ in range(prod_count)],
            'name': [f'Gadget_{i}' for i in range(prod_count)],
            'price': np.random.choice([499, 999, 1499, 1999, 2499], prod_count),
            'margin': 0.35,
            'category': 'Electronics',
            'created_at': [random_date(1200, 1100) for _ in range(prod_count)]
        })
        df_prod.to_sql('products', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 5. Campaign Products (Bridge Table)
        # ---------------------------
        df_cp = pd.DataFrame({
            'id': [str(uuid.uuid4()) for _ in range(40)],
            'campaign_id': np.random.choice(c_ids, 40),
            'product_id': np.random.choice(prod_ids, 40),
            'bid': np.round(np.random.uniform(1.5, 4.5, 40), 2),
            'status': 'ENABLED',
            'created_at': [random_date(1100, 1000) for _ in range(40)]
        })
        df_cp.to_sql('campaign_products', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 6. Performance Metrics (PRIORITY LOGIC)
        # ---------------------------
        metrics = []
        total_days = 1095  # 3 Years
        dates = pd.date_range(end=datetime.now(), periods=total_days)

        for i, d in enumerate(dates):
            is_weekend = 1 if d.weekday() >= 5 else 0
            month = d.month
            day_of_month = d.day
            
            # --- HIGH PRIORITY BOOSTS ---
            # Weekend boost increased to 2.8x so model sees it as a major driver
            weekend_boost = 2.8 if is_weekend else 1.0
            payday_boost = 1.30 if (day_of_month <= 5 or day_of_month >= 25) else 1.0
            yearly_growth = 1 + (i / 900)

            c_row = df_c.sample(1).iloc[0]
            p_row = df_prod.sample(1).iloc[0]

            # --- DAILY BUDGET PRIORITY ---
            # Budget ka direct 20% impact sales value par
            daily_budget = c_row['daily_budget']
            price = p_row['price']
            
            # Mathematical Core: Budget and Weekend are now primary multipliers
            base_sales_val = (daily_budget * 0.20) * weekend_boost * payday_boost * yearly_growth
            noise = np.random.normal(1, 0.03) # Low noise means stronger signal
            sales = round(base_sales_val * noise, 2)
            
            orders = int(sales / price) if sales > price else (1 if np.random.random() > 0.8 else 0)
            spend = round(daily_budget * np.random.uniform(0.85, 0.98), 2)
            
            clicks = max(1, int(spend / np.random.uniform(1.5, 3.0)))
            impressions = clicks * np.random.randint(25, 60)
            cpc = round(spend/clicks, 2)
            ctr = round(clicks/impressions, 4)
            cvr = round(orders/clicks, 3) if clicks > 0 else 0

            metrics.append({
                'id': str(uuid.uuid4()),
                'campaign_id': c_row['id'],
                'date': d.date(),
                'is_weekend': is_weekend,
                'month': month,
                'day_of_month': day_of_month,
                'impressions': impressions,
                'clicks': clicks,
                'spend': spend,
                'sales': sales,
                'orders': orders,
                'acos': round((spend/sales)*100, 2) if sales > 0 else 0,
                'roas': round(sales/spend, 2) if spend > 0 else 0,
                'ctr': ctr,
                'cpc': cpc,
                'cvr': cvr,
                'product_id': p_row['id'],
                'daily_budget': daily_budget,
                'price': price
            })

        # ---------------------------
        # 7. Advanced Feature Engineering (Rolling Mean 14 & 30 Integration)
        # ---------------------------
        master_df = pd.DataFrame(metrics)
        master_df = master_df.sort_values(by=['campaign_id', 'date'])

        master_df['sales_lag_1'] = master_df.groupby('campaign_id')['sales'].shift(1)
        master_df['sales_lag_7'] = master_df.groupby('campaign_id')['sales'].shift(7)
        
        master_df['avg_sales_7d'] = master_df.groupby('campaign_id')['sales'].transform(lambda x: x.shift(1).rolling(window=7).mean())
        master_df['avg_spend_7d'] = master_df.groupby('campaign_id')['spend'].transform(lambda x: x.shift(1).rolling(window=7).mean())
        
        master_df['rolling_mean_14'] = master_df.groupby('campaign_id')['sales'].transform(lambda x: x.shift(1).rolling(window=14).mean())
        master_df['rolling_mean_30'] = master_df.groupby('campaign_id')['sales'].transform(lambda x: x.shift(1).rolling(window=30).mean())

        master_df.fillna(0, inplace=True)
        
        # SQL Save
        master_df.to_sql('performance_metrics', con=engine, if_exists='append', index=False)
        
        print(f"✅ Priority Data Generated! Focus: Daily Budget & Weekends. Total: {len(master_df)}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

# ---------------------------
# 8. Main Execution
# ---------------------------
if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        tables = ['performance_metrics', 'campaign_products', 'products', 'campaigns', 'portfolios']
        for t in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {t};"))
            print(f"🗑️ Cleaned: {t}")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    generate_full_system_data()