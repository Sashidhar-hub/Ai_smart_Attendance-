import streamlit as st

st.title("Test App - Fresh Start")
st.write("If you see this, your Streamlit is working.")

# Create Account Form
with st.form("create_account_test"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Create Account - TEST BUTTON")
    
    if submit:
        st.success(f"Account created for {name} ({email}) - TEST SUCCESS!")