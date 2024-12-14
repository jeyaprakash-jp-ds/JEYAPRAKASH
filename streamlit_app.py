import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import plotly.express as px

# Function to connect to the PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(
        host="database-1.c5qcwckke9ox.ap-south-1.rds.amazonaws.com",
        port=5432,
        database="postgres",
        user="postgres",
        password="root1234"
    )
    return conn

# Function to execute a query and return the result as a pandas DataFrame
def run_query(query):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
    finally:
        conn.close()

# Streamlit UI
st.title("Retail Order Dashboard")

# Split queries into two sections
queries_by_guvi = {
    "Top 10 highest revenue generating products": 
        'SELECT P.PRODUCT_ID,SUM(O.SALE_PRICE) AS REVENUE FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID GROUP BY P.PRODUCT_ID ORDER BY REVENUE DESC LIMIT 10;'
    "Top 5 cities with the highest profit margins":
        'SELECT CITY,AVG(CASE WHEN SALE_PRICE= 0 THEN 0 ELSE((PROFIT/SALE_PRICE)*100) END) AS PROFIT_MARGIN FROM ORDER_DATA GROUP BY CITY ORDER BY PROFIT_MARGIN DESC LIMIT 5;'
    "Total discount given for each category": 
        'SELECT P.CATEGORY,SUM(O.DISCOUNT_PRICE) AS TOTAL_DISCOUNT FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID GROUP BY P.CATEGORY;'
    "Average sales price per product category": 
        'SELECT P.CATEGORY,AVG(O.SALE_PRICE) AS AVG_SALE_PRICE FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID GROUP BY P.CATEGORY;'
    "The highest average sale price":
        'SELECT REGION,AVG(SALE_PRICE) AS REGIONAL_SALE_PRICE FROM ORDER_DATA GROUP BY REGION ORDER BY REGIONAL_SALE_PRICE DESC LIMIT 1;'
    "Total profit per category": 
        'SELECT P.CATEGORY,SUM(O.PROFIT) AS PROFIT_PER_CATEGORY FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID GROUP BY P.CATEGORY ORDER BY PROFIT_PER_CATEGORY DESC;' 
    "Top 3 segments with the highest quantity of orders": 
        'SELECT SEGMENT,SUM(QUANTITY) AS ORDER_QUANTITY FROM ORDER_DATA GROUP BY SEGMENT ORDER BY ORDER_QUANTITY DESC LIMIT 3;'
    "Average discount percentage given per region": 
        'SELECT REGION,AVG(DISCOUNT_PERCENT) AS DISCOUNT_PERCENTAGE FROM ORDER_DATA GROUP BY REGION;'
    "Product category with the highest total profit": 
        'SELECT P.CATEGORY,SUM(O.PROFIT) AS TOT_PROFIT FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID GROUP BY P.CATEGORY ORDER BY TOT_PROFIT DESC LIMIT 1;'
    "Total revenue generated per year": 
        'SELECT ORDER_YEAR,SUM(SALE_PRICE) AS REVENUE FROM ORDER_DATA GROUP BY ORDER_YEAR;'
}

my_own_queries = {
    "CATEGORY WITH LEAST AVERAGE DISCOUNT":
        'SELECT P.CATEGORY,AVG(O.DISCOUNT_PRICE) AS AVERAGE_DISCOUNT FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID GROUP BY P.CATEGORY ORDER BY AVERAGE_DISCOUNT ASC LIMIT 1;'
    "PRODUCT WITH LEAST PROFIT MARGIN AND HIGHEST QUANTITY":
        'SELECT P.PRODUCT_ID,AVG(CASE WHEN O.SALE_PRICE=0 THEN 0 ELSE((O.PROFIT/O.SALE_PRICE)*100) END) AS PROFIT_MARGIN,SUM(O.QUANTITY) FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID GROUP BY P.PRODUCT_ID ORDER BY PROFIT_MARGIN ASC, SUM(O.QUANTITY) DESC LIMIT 1;'
    "SUB CATEGORY WITH LEAST SALES QUANTITY":
        'SELECT P.SUB_CATEGORY,SUM(O.QUANTITY) AS SALES FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID GROUP BY P.SUB_CATEGORY ORDER BY SALES ASC  LIMIT 1 ;'
    "10  PRODUCTS LEAST SOLD IN 2022":
        'SELECT P.PRODUCT_ID,SUM(O.QUANTITY) AS YEARLY_SALES FROM ORDER_DATA O JOIN PRODUCT_DATA P ON O.PRODUCT_ID=P.PRODUCT_ID WHERE ORDER_YEAR=2022 GROUP BY P.PRODUCT_ID ORDER BY YEARLY_SALES ASC LIMIT 10;'    
    "WHICH CATEGORY YIELDED HIGHEST PROFIT IN 2023":
        'SELECT P.CATEGORY,SUM(O.PROFIT) AS YIELD FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID WHERE ORDER_YEAR=2022 GROUP BY P.CATEGORY ORDER BY YIELD DESC LIMIT 1;'
    "3 MOST POPULAR PRODUCTS IN EASTERN REGION AND THEIR TOTAL PROFITS":
        'SELECT P.PRODUCT_ID,SUM(O.QUANTITY) AS POPULAR_PRODUCTS,SUM(O.PROFIT) FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID WHERE O.REGION='East' GROUP BY P.PRODUCT_ID ORDER BY POPULAR_PRODUCTS DESC LIMIT 3;'    
    "CITY WITH HIGHEST SALES":
        'SELECT CITY,SUM(QUANTITY) AS SALES FROM ORDER_DATA GROUP BY CITY ORDER BY SALES DESC LIMIT 1;'
    "5 CITIES WITH HIGHEST PROFIT MARGIN":
        'SELECT CITY,AVG(CASE WHEN SALE_PRICE=0 THEN 0 ELSE((PROFIT/SALE_PRICE)*100) END) AS PROFIT_MARGIN FROM ORDER_DATA GROUP BY CITY ORDER BY  PROFIT_MARGIN DESC LIMIT 5;'
    "STATE WITH LEAST SALES IN OFFICE SUPPLIES":
        'SELECT O.STATE,SUM(O.QUANTITY) FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID WHERE P.CATEGORY='Office Supplies' GROUP BY O.STATE ORDER BY SUM(O.QUANTITY) ASC LIMIT 1;'
    "SUB CATEGORY MOST SOLD IN WESTERN REGION":        
        'SELECT P.SUB_CATEGORY,COUNT(P.PRODUCT_ID),SUM(O.QUANTITY) AS SALES1  FROM PRODUCT_DATA P JOIN ORDER_DATA O ON P.PRODUCT_ID=O.PRODUCT_ID WHERE O.REGION='West' GROUP BY P.SUB_CATEGORY ORDER BY SALES1 DESC LIMIT 1  ;
}

# Navigation options
nav = st.radio("Select Query Section", ["Queries by GUVI", "My Own Queries"])

# Query selection based on navigation
if nav == "Queries by GUVI":
    st.subheader("Queries by GUVI")
    query = st.selectbox("Select a query to execute:", list(queries_by_guvi.keys()))
    selected_query_set = queries_by_guvi
elif nav == "My Own Queries":
    st.subheader("My Own Queries")
    query = st.selectbox("Select a query to execute:", list(my_own_queries.keys()))
    selected_query_set = my_own_queries
else:
    query = None

# Execute  selected query
if query:
    result_df = run_query(selected_query_set[query])
    

# Execute the selected query
       
    if query ==    "Top 10 highest revenue generating products": 
        result_df = run_query(queries_by_guvi[query])
       

    elif query == "Top 5 cities with the highest profit margins":
        result_df = run_query(queries_by_guvi[query])
        
    elif query == "Total discount given for each category":
        result_df = run_query(queries_by_guvi[query])
      
    elif query == "Average sales price per product category":
        result_df = run_query(queries_by_guvi[query])
        

    elif query== "Total profit per category":
        result_df = run_query(queries_by_guvi[query])
       

    elif query == "Top 3 segments with the highest quantity of orders":
        result_df = run_query(queries_by_guvi[query])
       

    elif query == "Average discount percentage given per region":
        result_df = run_query(queries_by_guvi[query])
       
    elif query == "Product category with the highest total profit":
        result_df = run_query(queries_by_guvi[query])
       

    elif query == "Total revenue generated per year":
        result_df = run_query(queries_by_guvi[query])
       

    elif query == "CATEGORY WITH LEAST AVERAGE DISCOUNT":
        result_df = run_query(my_own_queries[query])
       
    elif query ==  "PRODUCT WITH LEAST PROFIT MARGIN AND HIGHEST QUANTITY":
        result_df = run_query(my_own_queries[query])
        

    elif query =="SUB CATEGORY WITH LEAST SALES QUANTITY":
        result_df = run_query(my_own_queries[query])
        

    elif query ==    "10  PRODUCTS LEAST SOLD IN 2022" :
        result_df = run_query(my_own_queries[query])
        

    elif query == "WHICH CATEGORY YIELDED HIGHEST PROFIT IN 2023":
        result_df = run_query(my_own_queries[query])
       

    elif query == "3 MOST POPULAR PRODUCTS IN EASTERN REGION AND THEIR TOTAL PROFITS":
        result_df = run_query(my_own_queries[query])
       

    elif query =="CITY WITH HIGHEST SALES" :
        result_df = run_query(my_own_queries[query])
       
    elif query == "5 CITIES WITH HIGHEST PROFIT MARGIN":
        result_df = run_query(my_own_queries[query])
       

    elif query == "STATE WITH LEAST SALES IN OFFICE SUPPLIES":
        result_df = run_query(my_own_queries[query])
        

    elif query =="SUB CATEGORY MOST SOLD IN WESTERN REGION" :
        result_df = run_query(my_own_queries[query])
      
       
else:
    st.warning("Please select a query.")        

st.text("Thank you for using the dashboard!")
