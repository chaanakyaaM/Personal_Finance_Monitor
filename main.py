import os
import time 
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()

# The URL for the flask server 
API_URL = os.getenv("API_URL")

# --- Streamlit page setup ---
st.set_page_config(page_title="Personal Finance Monitor", layout="wide")

# --- Initialize session state ---
if "admin" not in st.session_state:
    st.session_state["admin"] = None # "user", "admin", or None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False
if "show_register" not in st.session_state:
    st.session_state["show_register"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

# --- Logout Function ---
def logout():
    """Resets the session state for logout."""
    st.session_state["admin"] = None
    st.session_state["username"] = None
    st.session_state["user_id"] = None
    st.session_state["show_login"] = False
    st.session_state["show_register"] = False
    st.rerun() 

# Handle API requests with error handling
def handle_api_request(endpoint, data = None, method = "GET"):
    try:
        if method == "GET":
            res = requests.get(f"{API_URL}{endpoint}")
            return res.json()
        
        elif method == "POST":
            res = requests.post(f"{API_URL}{endpoint}", json=data)
            return res.json()
        
        elif method == "DELETE":
            res = requests.delete(f"{API_URL}{endpoint}")
            return res.json()

        
    except Exception as e:
        st.error(f"API Error: Could not connect to the backend server. ({e})")
        return None

try:
    res = handle_api_request('/', None, 'GET')
except:
    pass

# --- Login Form ---
@st.dialog("Login")
def login_form():
    with st.form("login_form"):
        st.write("Please enter your credentials to log in.")
        username = st.text_input("Username *", key="login_user_input")
        password = st.text_input("Password *", type="password", key="login_pass_input")
        
        submitted = st.form_submit_button("Submit Login")

        if submitted:
            username = username.strip()
            password = password.strip()

            if not username or not password:
                st.error("All fields are required.")
                return
            
            data = handle_api_request("/login", {"username": username, "password_hash": password}, "POST")
            
            if data:
                if data.get("auth"):
                    st.session_state["admin"] = "user"
                    st.session_state["username"] = username
                    st.session_state["show_login"] = False
                    st.session_state["user_id"] = data.get("user_id")
                    st.success(f"Logged in as **{username}**. Redirecting...")
                    time.sleep(1) 
                    st.rerun()
                elif data.get("admin"):
                    st.session_state["admin"] = "admin"
                    st.session_state["username"] = username
                    st.session_state["show_login"] = False
                    st.success(f"Admin **{username}** logged in. Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state["admin"] = None
                    st.session_state["username"] = None
                    st.error(f"Login failed: {data.get('error', 'Invalid credentials.')}")

# --- Register Form ---
@st.dialog("Register")
def register_form():
    with st.form("register_form"):
        st.write("Create a new account.")
        username = st.text_input("Username *", key="reg_user_input")
        password = st.text_input("Password *", type="password", key="reg_pass_input")
        confirm_password = st.text_input("Confirm Password *", type="password", key="reg_confirm_input")

        st.markdown("""
        **Password Requirements**
        - Must be more than 4 characters 
        - Must contain at least one number (0-9) 
        - Must contain at least a single uppercase letter (A-Z)
        """)
        
        submitted = st.form_submit_button("Submit Registration")

        if submitted:
            username = username.strip()
            password = password.strip()
            confirm_password = confirm_password.strip()

            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            if len(password) <= 4:
                st.error("Password must be more than 4 characters.")
                return
            if not any(char.isdigit() for char in password):
                st.error("Password must contain at least one number (0-9).")
                return
            if not any(char.isupper() for char in password):
                st.error("Password must contain at least one uppercase letter (A-Z).")
                return

            data = handle_api_request("/register", {"username": username, "password_hash": password}, "POST")

            try:
                if data.get("auth"):
                    st.success(f"Account created successfully for **{username}**! Please log in.")
                    st.session_state["show_register"] = False # Hide registration form
                    st.session_state["show_login"] = True # Show login form
                    st.rerun()
            except Exception as e:
                st.error(f"Registration failed: {data.get('error', 'Unknown error')}")

# --- New Transaction Form ---
@st.dialog("New Transaction")
def new_transaction_form():
    category = st.selectbox("Category", ["Income", "Expense"])
    if category == "Income":
        type = ["Salary", "Investment", "Side Hustle", "Other"]
    else:
        type = ["Fun", "Rent", "Groceries", "EMI", "Other"]
    with st.form("New_transaction_form"):
        txn_type = st.selectbox("Type", type)
        amount = st.number_input("Amount", format = "%.2f")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Submit")
        if submitted:
            data = {
                "user_id" : st.session_state.get("user_id"),
                "category" : category.lower(),
                "type" : txn_type,
                "amount" : amount,
                "notes" : notes
            }
            res = handle_api_request("/transaction", data, "POST")
            try:
                if res.get("message"):
                    st.success(res.get("message"))
                    st.rerun()
            except Exception as e:
                st.error(res.get("error"))

# --- Delete Transaction ---
@st.dialog("Delete Transaction")
def delete_transaction_form():
    transaction_id = st.number_input("Transaction ID", min_value = 1, step = 1, format = "%d")
    if st.button("Delete"):
        res = handle_api_request(f"/delete_transaction/{st.session_state["user_id"]}/{int(transaction_id)}", None, "DELETE")
        try:
            if res.get("message"):
                st.success(res.get("message"))
                st.rerun()
        except Exception as e:
            st.error(res.get("error"))
            time.sleep(3)
            st.rerun()

# --- Delete User ---
@st.dialog("Delete User")
def delete_user():
    user_id = st.number_input("User ID", min_value = 1, step = 1, format = "%d")
    if st.button("Delete"):
        res = handle_api_request(f"/delete_user/{int(user_id)}", None, "DELETE")
        try:
            if res.get("message"):
                st.success("User deleted successfully.")
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(res.get("error"))

# --- Sidebar Navigation & Status ---   
st.sidebar.title("App Navigation")

if st.session_state["admin"]:
    # User is logged in, show status and logout button
    st.sidebar.info(f"Welcome, **{st.session_state['username']}**")
    st.sidebar.info(f"User ID: {st.session_state['user_id']}")
    if st.sidebar.button("Logout", key="logout_btn", width="stretch"):
        logout()
    if st.sidebar.button("Refresh", key = "refresh_btn", width="stretch"):
        st.rerun()
else:
    # User is not logged in, show Login/Register buttons
    if st.sidebar.button("Login", key="login_btn", width="stretch"):
        st.session_state["show_login"] = True
        st.session_state["show_register"] = False

    if st.sidebar.button("Register", key="register_btn", width="stretch"):
        st.session_state["show_register"] = True
        st.session_state["show_login"] = False

# --- Main Content Rendering ---
st.title("Personal Finance Monitor")
st.markdown("**This is where you can view all of your transactions.**")

if st.session_state["admin"] is None:
    # 1. Show login/register forms if their flags are set
    if st.session_state["show_login"]:
        login_form()
    elif st.session_state["show_register"]:
        register_form()
    # 2. Show a welcome message if no form is open
    else:
        c1,c2 = st.columns(2)
        with c1:
            st.write("Your journey to financial control starts now. This Personal Finance Monitor is designed to help you not just track your money, but understand it. See exactly where your income is going, identify spending trends, and visualize your progress towards savings goals. It's more than just a ledger—it's a tool for building a healthier financial future. ")
            st.markdown("### What You Can Do")
            st.markdown("""
            - **Track Transactions:** Record your incomes and expenses easily.
            - **Visual Analytics:** See where your money is going with charts.
            - **Insights:** Get monthly and daily spending patterns.
            """)
            st.info("Please Login or Register to access your financial dashboard.")
        with c2:
            st.image("https://images.unsplash.com/photo-1579621970795-87facc2f976d?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", width="stretch")

# If admin is logged in
elif st.session_state["admin"] == "admin":
    st.subheader("Admin Panel")
    st.success(f"You are logged in as Admin .")
    st.markdown("Here you can track all user data, manage accounts, and monitor system health.")

    json_data = handle_api_request("/output",None, "GET")
    labels = json_data["labels"]
    values = json_data["values"]

    df_transactions = pd.DataFrame(values["transactions"], columns=labels["transactions"])
    df_users = pd.DataFrame(values["users"], columns=labels["users"])

    st.title("JSON Data Viewer")

    st.subheader("Categories")

    st.subheader("Transactions")
    st.dataframe(df_transactions)

    st.subheader("Users")
    st.dataframe(df_users)

    if st.button("Delete User"):
        delete_user()

# If regular user is logged in   
elif st.session_state["admin"] == "user":
    # Tabs
    tab1, tab2 = st.tabs(["Transactions", "Dashboard"])
    
    # Transactions Tab
    with tab1:
        st.subheader("Transactions Overview")
        st.write("This is where your can view all of your transactions.")
        res = handle_api_request(f"/transaction/{st.session_state['user_id']}", None, "GET")
        columns = ["Transaction ID", "Timestamp", "Category", "Type", "Amount", "Note"]
        df = pd.DataFrame(res, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox("Filter by Category", ["All", "income", "expense"])
        with col2:
            filter_type = st.selectbox("Filter by Type", ["All"] + list(df["Type"].unique()) if not df.empty else ["All"])

        # Apply filters
        filtered_df = df.copy()
        if filter_category != "All":
            filtered_df = filtered_df[filtered_df["Category"] == filter_category]
        if filter_type != "All":
            filtered_df = filtered_df[filtered_df["Type"] == filter_type]

        st.dataframe(filtered_df, width="stretch")

        c1,c2 = st.columns(2)
        with c1:
            if st.button("Add Transaction"):
                new_transaction_form()
        with c2:
            if st.button("Delete Transaction"):
                delete_transaction_form()

    # Dashboard Tab
    with tab2:
        st.header("Dashboard Analytics")
        res = handle_api_request(f"/analytics/{st.session_state['user_id']}", None, "GET")
        if res.get("error"):
            st.error(res.get("error"))
        else:
            try:
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Gross Income", f"${res.get('income',0)}", delta=f"${res.get('income',0)*1}")
                c2.metric("Total Expense", f"${res.get('expense',0)}")
                c3.metric("Net Savings", f"${res.get('net',0):.2f}")
                c4.metric("Total Transactions", res.get('total_transactions',0))

                st.subheader("Income and Expense Distributions")
                c1,c2 = st.columns(2)
                with c1:
                    type = [fir[0] for fir in res.get("income_type_breakdown",[])]
                    amount = [fir[1] for fir in res.get("income_type_breakdown",[])]
                    data = {
                        "Type": type,
                        "Amount": amount
                    }
                    df = pd.DataFrame(data)
                    fig = px.pie(df, names="Type", values="Amount", title="Types of Income Distribution")
                    st.plotly_chart(fig)
                with c2:
                    type = [fir[0] for fir in res.get("expense_type_breakdown",[])]
                    amount = [fir[1] for fir in res.get("expense_type_breakdown",[])]
                    data = {
                        "Type": type,
                        "Amount": amount
                    }
                    df = pd.DataFrame(data)
                    fig = px.pie(df, names="Type", values="Amount", title="Types of Expense Distribution")
                    st.plotly_chart(fig)
            
                df = pd.DataFrame(res.get("category_type_breakdown", []), columns=["Category", "Type", "Amount"])

                category_groups = df.groupby("Category")
                
                expense_indices = category_groups.indices.get("expense") 
                df_expense = df.iloc[expense_indices]

                income_indices = category_groups.indices.get("income")
                df_income = df.iloc[income_indices]

                # Income and Expense Breakdown Tables
                c1,c2 = st.columns(2)
                with c1:
                    st.write("### Income type Breakdown")
                    st.write(df_income)

                with c2:
                    st.write("### Expense type Breakdown")
                    st.write(df_expense)

                # Daily Income and Expense
                data = res.get("daily", [])

                df = pd.DataFrame(data, columns=["Date", "Type", "Amount"])

                df["Date"] = pd.to_datetime(df["Date"])
                df["Amount"] = pd.to_numeric(df["Amount"])

                df.loc[df["Type"] == "expense", "Amount"] *= -1

                pivot_df = df.pivot_table(index="Date", columns="Type", values="Amount", aggfunc="sum").fillna(0)

                fig = go.Figure()

                # Income bar
                fig.add_trace(go.Bar(
                    x=pivot_df.index,
                    y=pivot_df["income"],
                    name="Income",
                    marker_color="green"
                ))

                # Expense bar (already negative)
                fig.add_trace(go.Bar(
                    x=pivot_df.index,
                    y=pivot_df["expense"],
                    name="Expense",
                    marker_color="red"
                ))

                # Layout
                fig.update_layout(
                    title="Daily Income and Expense Insights",
                    barmode="relative",
                    xaxis_title="Date",
                    yaxis_title="Amount",
                    legend=dict(orientation="h"),
                    height=500
                )

                st.plotly_chart(fig, config = {"width":"stretch"})

                # Monthly Income and Expense
                data = res.get("daily", [])

                df = pd.DataFrame(data, columns=["Date", "Type", "Amount"])

                df["Date"] = pd.to_datetime(df["Date"])
                df["Amount"] = pd.to_numeric(df["Amount"])

                df.loc[df["Type"] == "expense", "Amount"] *= -1

                df["Month"] = df["Date"].dt.to_period("M").astype(str)

                monthly_df = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)

                fig = go.Figure()

                # Income bar (positive, green)
                fig.add_trace(go.Bar(
                    x=monthly_df.index,
                    y=monthly_df.get("income", 0),
                    name="Income",
                    marker_color="green"
                ))

                # Expense bar (negative, red)
                fig.add_trace(go.Bar(
                    x=monthly_df.index,
                    y=monthly_df.get("expense", 0),
                    name="Expense",
                    marker_color="red"
                ))

                # Layout
                fig.update_layout(
                    title="Monthly Income and Expense Insights",
                    barmode="relative",
                    xaxis_title="Month",
                    yaxis_title="Amount",
                    legend=dict(orientation="h"),
                    height=500
                )

                st.plotly_chart(fig, config = {"width":"stretch"})

                df = pd.DataFrame(res.get("rows",[]), columns=["day", "category", "total"])

                # Line Chart
                fig = px.line(
                    df, 
                    x="day", 
                    y="total", 
                    color="category", 
                    markers=True,
                    title="Income vs Expense Trend Over Time"
                )
                st.write(fig)
            except Exception as e:
                st.error(f"Error : {e}")
