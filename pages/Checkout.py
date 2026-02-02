# pages/Checkout.py

import streamlit as st
import uuid
from backend import ProductCatalog
from io import BytesIO
import qrcode

st.set_page_config(page_title="Checkout", layout="centered")

# ======================
# SESSION STATE INIT
# ======================
if "step" not in st.session_state:
    st.session_state.step = 1
if "address_info" not in st.session_state:
    st.session_state.address_info = {}
if "payment_method" not in st.session_state:
    st.session_state.payment_method = None
if "product" not in st.session_state:
    st.session_state.product = None
if "card_info" not in st.session_state:
    st.session_state.card_info = {}

# ======================
# GET PRODUCT ID FROM QUERY PARAMS
# ======================
query_params = st.query_params
product_id_list = query_params.get("product_id", [])
if not product_id_list:
    st.warning("No product selected! Go back and select a product.")
    st.stop()
product_id = int(product_id_list[0])

# ======================
# LOAD PRODUCT
# ======================
catalog = ProductCatalog()
catalog.generate_products()
if product_id >= len(catalog.products):
    st.warning("Invalid product selected!")
    st.stop()
    
product = catalog.products[product_id]
st.session_state.product = product

st.header(f"Checkout: {product.name}")
st.write(f"Brand: {product.brand}")
st.write(f"Price: ${product.price}")

# ======================
# STEP 1: ADDRESS DETAILS
# ======================
if st.session_state.step == 1:
    st.subheader("Step 1: Enter Address")
    state = st.text_input("State")
    pin = st.text_input("Pin Code")
    mobile = st.text_input("Mobile Number")
    street = st.text_input("Street / Area / City")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Next →"):
            if not all([state, pin, mobile, street]):
                st.warning("Please fill all fields!")
            else:
                st.session_state.address_info = {
                    "state": state,
                    "pin_code": pin,
                    "mobile": mobile,
                    "street": street
                }
                st.session_state.step = 2

# ======================
# STEP 2: PAYMENT METHOD
# ======================
elif st.session_state.step == 2:
    st.subheader("Step 2: Select Payment Method")
    st.session_state.payment_method = st.radio(
        "Payment Options",
        ["Credit Card", "Debit Card", "Cash on Delivery", "UPI/PhonePe/GPay"]
    )

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 1
    with col2:
        if st.button("Next →"):
            if st.session_state.payment_method in ["Credit Card", "Debit Card"]:
                st.session_state.step = 3
            elif st.session_state.payment_method == "UPI/PhonePe/GPay":
                st.session_state.step = 4
            else:
                st.session_state.step = 5  # COD confirmation

# ======================
# STEP 3: CREDIT/DEBIT CARD PAYMENT
# ======================
elif st.session_state.step == 3:
    st.subheader(f"Step 3: {st.session_state.payment_method} Payment")
    card_number = st.text_input("Card Number")
    card_name = st.text_input("Name on Card")
    expiry = st.text_input("Expiry (MM/YY)")
    cvv = st.text_input("CVV", type="password")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 2
    with col2:
        if st.button("Pay"):
            if not all([card_number, card_name, expiry, cvv]):
                st.warning("Please fill all card details!")
            else:
                st.session_state.card_info = {
                    "card_number": card_number[-4:],  # last 4 digits only
                    "name": card_name,
                    "expiry": expiry
                }
                st.success("Payment Successful ✅")
                st.session_state.step = 5  # Order confirmation

# ======================
# STEP 4: UPI PAYMENT
# ======================
elif st.session_state.step == 4:
    st.subheader("Step 3: Scan QR to Pay (UPI)")
    upi_id = "yourupiid@bank"  # Dummy UPI ID
    qr_data = f"upi://pay?pa={upi_id}&pn=Demo+Store&am={product.price}&cu=INR"
    qr = qrcode.QRCode(box_size=8, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    st.image(buf, width=200, caption="Scan this QR with your UPI app to pay")  # width param used

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Back"):
            st.session_state.step = 2
    with col2:
        if st.button("Payment Done"):
            st.success("Payment confirmed ✅")
            st.session_state.step = 5

# ======================
# STEP 5: ORDER CONFIRMATION
# ======================
elif st.session_state.step == 5:
    st.subheader("Step 4: Confirm Order")
    st.write("**Product:**", product.name)
    st.write("**Price:**", f"${product.price}")
    st.write("**Payment Method:**", st.session_state.payment_method)

    st.write("**Address:**")
    for k, v in st.session_state.address_info.items():
        st.write(f"{k.capitalize()}: {v}")

    # Campaign attribution (for client demo)
    st.info(f"📢 This order was generated via Sponsored Product Campaign – Keyword: {getattr(product, 'campaign_kw', 'Demo')}")

    if st.button("✅ Place Order"):
        order_id = str(uuid.uuid4())[:8]
        st.success(f"🎉 Order Placed Successfully! Order ID: {order_id}")

        # Reset session state for next demo
        st.session_state.step = 1
        st.session_state.address_info = {}
        st.session_state.payment_method = None
        st.session_state.product = None
        st.session_state.card_info = {}
