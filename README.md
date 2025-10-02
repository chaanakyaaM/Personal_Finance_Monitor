# Personal Finance Monitor

**Personal Finance Monitor** is a **full-stack application** and a powerful tool designed to help you stay in control of your money. It gives you a clear picture of your income, expenses, and savings, making it easier to understand your financial habits and plan ahead with confidence. Instead of just tracking numbers, it turns your daily transactions into meaningful insights that guide smarter decisions for a healthier financial future.

##  Features / Functionality

-  Register/Login with password hashing  
-  Add, view, and delete transactions  
-  Visual analytics:
    - Income & Expense distribution (pie charts)
    - Daily, monthly spending trends
    - Time Series Analysis and Forecasting
    - Net savings & total transactions
-  Filter transactions by category/type  
-  Admin Panel


##  Tech Stack
- **Backend:** Flask, Flask-CORS, Werkzeug, DAO (custom DB handlers)  
- **Frontend:** Streamlit, Plotly (for charts), Pandas  
- **Database:** Postgres via DAO layer
- **Environment Management:** Python `dotenv`

## Steps to set-up the project locally

## For Frontend:
### 1. Clone the Repository
```bash
git clone https://github.com/chaanakyaaM/Personal_Finance_Monitor.git
cd personal-finance-monitor
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```
or
```bash
uv init
.venv/scripts/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
or
```bash
uv add -r requirements.txt
```

### 4. Configure Environment Variables
```Create a .env file in the project root:
API_URL=http://127.0.0.1:5000
 or your backend server URL
```

### 5. Run Frontend (Streamlit)
```bash
streamlit run app.py
```

## For Backend:
### 1. Clone the Repository
For Frontend:
```bash
git clone hhttps://github.com/chaanakyaaM/Personal_Finance_Monitor_Server.git
cd personal-finance-monitor-server
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```
or
```bash
uv init
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
or
```bash
uv add -r requirements.txt
```

### 4. Configure Environment Variables
```Create a .env file in the project root:
DB_PASSWORD = your_db_password
DB_NAME = your_db_name
DB_USER = your_db_user (mostly postgres)
```
### 5. Run Backend server (Flask)
```bash
python app.py
```

## Project Structure
#### Frontend
```bash
personal-finance-monitor/
├── main.py             
│── .env 
│── requirements.txt       
│── pyproject.toml
│── README.md              

```
#### Backend

```bash
personal-finance-monitor-server/
│── .env                   
│── app.py
│── dao/
│   ├── __init__.py
│   ├── dbconfig.py
│   ├── admin_dao.py
│   ├── analytics_dao.py
│   ├── transactions_dao.py
│   ├── user_dao.py
│── pyproject.toml                
│── requirements.txt       
│── README.md              
```

## API Endpoints

- `POST /register` → Register new user

- `POST /login` → Login existing user

- `POST /transaction` → Add new transaction

- `GET /transaction/<user_id>` → Get user transactions

- `DELETE /delete_transaction/<user_id>/<transaction_id>` → Delete a transaction

- `GET /analytics/<user_id>` → Get analytics for a user

- `GET /output` → Admin panel views
