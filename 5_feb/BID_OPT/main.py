import streamlit as st
import pandas as pd
import joblib
import pickle
import numpy as np

# Page Configuration
st.set_page_config(page_title="Amazon Bid Optimizer", layout="wide")

st.title("🚀 Amazon Ads: Bid Optimization Tool")
st.markdown("Enter campaign metrics to get the mathematically optimized bid.")

@st.cache_resource 
def load_models():
    # Make sure Model.pkl and scaler.pkl are in the same folder
    model = pickle.load(open("Model.pkl", "rb"))
    scaler = joblib.load("scaler.pkl")
    return model, scaler

try:
    model, scaler = load_models()
    st.success("✅ Model and Scaler successfully loaded")
except Exception as e:
    st.error(f"❌ Error: pkl files not found. Run your notebook first. {e}")

# --- Input Form ---
st.header("📊 Campaign Performance Metrics")

with st.form("prediction_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Core Metrics")
        current_bid = st.number_input("Current Bid ($)", min_value=0.0, value=15.0, step=0.1)
        impressions = st.number_input("Impressions", min_value=0, value=10000)
        clicks = st.number_input("Clicks", min_value=0, value=200)
        actual_acos = st.number_input("Actual ACoS (%)", min_value=0.0, value=50.0)
        target_acos = st.number_input("Target ACoS (%)", min_value=0.0, value=45.0)

    with col2:
        st.subheader("Efficiency")
        cvr = st.number_input("Conversion Rate (CVR %)", min_value=0.0, value=5.0)
        ctr = st.number_input("Click-Through Rate (CTR %)", min_value=0.0, value=1.0)
        cpc_actual = st.number_input("Actual CPC ($)", min_value=0.0, value=12.0)
        organic_rank = st.number_input("Organic Rank (1-20)", min_value=1, max_value=100, value=10)
        competitor_price_gap = st.number_input("Competitor Price Gap", value=0.0)

    with col3:
        st.subheader("Context & Strategy")
        month_index = st.slider("Month Index (1-12)", 1, 12, 1)
        is_winter = st.selectbox("Is Winter Season?", [0, 1], help="1 for Nov-Feb")
        is_weekend = st.selectbox("Is Weekend?", [0, 1])
        match_type = st.selectbox("Match Type (0:Auto, 1:Broad, 2:Phrase, 3:Exact)", [0, 1, 2, 3])
        inv_level = st.selectbox("Inventory Level (0:Low, 1:Med, 2:High)", [0, 1, 2])
        last_delta = st.number_input("Last Bid Change Delta", value=0.0)

    submit = st.form_submit_button("🎯 Predict Optimised Bid")

if submit:
    # 1. Prepare Input Dictionary
    input_dict = {
        'current_bid': current_bid, 'impressions': impressions, 'clicks': clicks, 
        'actual_acos': actual_acos, 'cvr': cvr, 'ctr': ctr, 
        'cpc_actual': cpc_actual, 'month_index': month_index, 
        'is_winter_season': is_winter, 'is_weekend': is_weekend, 
        'organic_rank': organic_rank, 'competitor_price_gap': competitor_price_gap, 
        'target_acos': target_acos, 'match_type_encoded': match_type, 
        'inventory_level': inv_level, 'last_bid_change_delta': last_delta
    }
    
    input_df = pd.DataFrame([input_dict])

    # 2. Scaling (Applying only to features scaled during training)
    sc_cols = ['current_bid','impressions','clicks','actual_acos','cvr','ctr',
               'cpc_actual','organic_rank','competitor_price_gap','last_bid_change_delta']
    
    input_df[sc_cols] = scaler.transform(input_df[sc_cols])

    # 3. Final Prediction
    raw_prediction = model.predict(input_df)[0]
    
    # 4. SAFETY CLIPPING (Crucial step for Linear Regression)
    # Range is 0.10 to 50.0 because your training data was in this range
    final_bid = np.clip(raw_prediction, a_min=0.10, a_max=50.0)

    # 5. Output Display Logic
    st.divider()
    
    # Visual feedback based on prediction vs current bid
    col_res1, col_res2 = st.columns([1, 2])
    
    with col_res1:
        st.metric(label="Recommended Bid", value=f"${round(final_bid, 2)}", 
                  delta=round(final_bid - current_bid, 2))

    with col_res2:
        if raw_prediction > 50.0:
            st.warning(f"⚠️ Model suggested ${round(raw_prediction, 2)}, but it was capped at $50.0 for safety.")
        
        if final_bid < current_bid:
            st.error(f"📉 Action: **Decrease Bid**. Your Actual ACoS ({actual_acos}%) is higher than Target ({target_acos}%).")
        elif final_bid > current_bid:
            st.success(f"📈 Action: **Increase Bid**. Your campaign has room to scale as ACoS is efficient.")
        else:
            st.info("⚖️ Action: **Hold Bid**. The current bid is optimal for the given metrics.")

    # Show data table for transparency
    with st.expander("See Raw Model Input"):
        st.write(input_df)