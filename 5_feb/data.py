import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime, timedelta

# ---------------------------
# Database Connection
# ---------------------------
# Note: switched to pymysql for better compatibility with MySQL 8.0 auth
# Ensure you run: pip install pymysql
engine = create_engine('mysql+pymysql://root:Admin%40123@localhost/amazon_ads_db')

# ---------------------------
# Data Generation Function
# ---------------------------
def generate_realistic_company_data():
    try:
        # Helper: random date generator
        def random_date(start_days_ago, end_days_ago):
            return datetime.now() - timedelta(days=np.random.randint(end_days_ago, start_days_ago))

        # ---------------------------
        # 1. Portfolios
        # ---------------------------
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

        # ---------------------------
        # 2. Campaigns (5 Sequential Campaigns)
        # ---------------------------
        c_ids = [str(uuid.uuid4()) for _ in range(5)]
        df_c = pd.DataFrame({
            'id': c_ids,
            'portfolio_id': [np.random.choice(p_ids) for _ in range(5)],
            'name': [f'Growth_Strategy_Phase_{i+1}' for i in range(5)],
            'type': np.random.choice(['SP', 'SB'], 5),
            'status': 'ENABLED',
            'daily_budget': np.random.uniform(200, 800, 5),
            'targeting_type': np.random.choice(['AUTO', 'MANUAL'], 5),
            'bidding_strategy': 'DYNAMIC_DOWN_ONLY',
            'created_at': [random_date(400, 380) for _ in range(5)]
        })
        df_c.to_sql('campaigns', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 3. Products
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
            'created_at': [random_date(400, 365) for _ in range(prod_count)]
        })
        df_prod.to_sql('products', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 4. Campaign Products
        # ---------------------------
        df_cp = pd.DataFrame({
            'id': [str(uuid.uuid4()) for _ in range(100)],
            'campaign_id': np.random.choice(c_ids, 100),
            'product_id': np.random.choice(prod_ids, 100),
            'bid': np.round(np.random.uniform(0.8, 3.5, 100), 2),
            'status': 'ENABLED',
            'created_at': [random_date(350, 300) for _ in range(100)]
        })
        df_cp.to_sql('campaign_products', con=engine, if_exists='append', index=False)

        # ---------------------------
        # 5. Performance Metrics
        # ---------------------------
        metrics = []
        dates = pd.date_range(end=datetime.now(), periods=365)
        days_per_phase = 365 // 5

        for i, d in enumerate(dates):
            phase_idx = min(i // days_per_phase, 4) 
            c_id = c_ids[phase_idx]

            # Seasonal Factors
            is_weekend = 1 if d.weekday() >= 5 else 0
            weekend_boost = 1.25 if is_weekend == 1 else 1.0
            month_end_boost = 1.15 if d.day > 25 else 1.0
            growth_factor = 1 + (i / 400) 

            # Base Logic
            cpc = round(np.random.uniform(0.8, 1.6), 2)
            spend = np.random.uniform(100, 300) * growth_factor * weekend_boost
            clicks = max(1, int(spend / cpc))
            
            # Impressions (Calculated from CTR)
            ctr = round(np.random.uniform(0.015, 0.04), 4)
            impressions = int(clicks / ctr)

            # Orders (Rounded to ensure low click days still get sales)
            base_cvr = 0.05 + (phase_idx * 0.01)
            cvr = round(np.random.uniform(base_cvr, base_cvr + 0.02) * month_end_boost, 3)
            orders = int(np.round(clicks * cvr))

            # Sales & Product Assignment
            product_id = np.random.choice(prod_ids)
            price = df_prod.loc[df_prod['id'] == product_id, 'price'].values[0]
            
            sales = round(orders * price, 2) if orders > 0 else 0.0

            # ACOS & ROAS (Safe calculation)
            acos = round((spend / sales) * 100, 2) if sales > 0 else 0.0
            roas = round(sales / spend, 2) if spend > 0 else 0.0

            metrics.append({
                'id': str(uuid.uuid4()),
                'campaign_id': c_id,
                'date': d.date(),
                'is_weekend': is_weekend,
                'impressions': impressions,
                'clicks': clicks,
                'spend': round(spend, 2),
                'sales': sales,
                'orders': orders,
                'acos': acos,
                'roas': roas,
                'ctr': ctr,
                'cpc': cpc,
                'cvr': cvr,
                'product_id': product_id
            })

        pd.DataFrame(metrics).to_sql('performance_metrics', con=engine, if_exists='append', index=False)
        print(f"✅ Success: Generated 365 sequential rows with realistic sales.")

    except Exception as e:
        print(f"❌ ERROR: {e}")

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        tables = ['performance_metrics', 'campaign_products', 'products', 'campaigns', 'portfolios']
        for t in tables:
            conn.execute(text(f"TRUNCATE TABLE {t};"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    generate_realistic_company_data()