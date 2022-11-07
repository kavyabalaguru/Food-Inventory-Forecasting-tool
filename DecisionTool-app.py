from fileinput import close
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_log_error
from bokeh.models.widgets import Div

#creating connection
st.set_page_config(page_title="Inventory Demand Forecasting Tool",page_icon="🧊",layout="wide",initial_sidebar_state="expanded")
connection = mysql.connector.connect(**st.secrets["mysql"])
if connection.is_connected():
    db_Info = connection.get_server_info()
    cursor = connection.cursor()
    cursor.execute("select database();")
    record = cursor.fetchone()

#page navigation
with st.sidebar:
        selected = option_menu("MENU", ["Home","Upload Data","Predictions"], 
        icons=['house','cloud-upload','activity'], menu_icon="cast", default_index=0)


if selected == "Home":
    st.header('Welcome to Food Inventory Forecasting Tool!')
    # UI Works
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"] {
    background-image: url("https://wallpaperaccess.com/full/1916250.jpg");
    background-repeat: no-repeat;
    background-size: cover;
    }

    [data-testid="stHeader"] {
    background: rgba(0,0,0,0);
    }
    [data-testid="stToolbar"] {{
    right: 2rem;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)


#Updating data file
if selected == "Upload Data":
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"] {
    background-image: url("https://thumbs.dreamstime.com/z/fresh-food-ingredients-vegetarian-kitchen-white-background-top-view-mock-up-raw-vegetable-143656296.jpg");
    background-repeat: no-repeat;
    background-size: cover;
    }

    [data-testid="stHeader"] {
    background: rgba(0,0,0,0);
    }
    [data-testid="stToolbar"] {{
    right: 2rem;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    deleting_all_rows="""truncate table test_data""" 
    cursor.execute(deleting_all_rows)
    connection.commit()
    deleting_all_rows="""truncate table Predicted_datafile""" 
    cursor.execute(deleting_all_rows)
    connection.commit()
    tab1, tab2 = st.tabs(["Upload the file", "enter the data here"])
    #Uploading the file
    with tab1:
        st.subheader("Dataset")
        data_file = st.file_uploader("Upload CSV",type=["csv"])
        if data_file is not None:
            if data_file.size!=2:
                df = pd.read_csv(data_file)
                sql = "INSERT INTO test_data (id,Year,Week,Date,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,city_code,region_code,center_type,op_area,category,cuisine) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                sql_cols = ['id','Year','Week','Date','center_id','meal_id','checkout_price','base_price','emailer_for_promotion','homepage_featured','city_code','region_code','center_type','op_area','category','cuisine']
                # Insert Dataframe into SQL Server:
                cursor.executemany(sql, df[sql_cols].values.tolist())
                connection.commit()
                st.write(cursor.rowcount, " records inserted successfully into test_data table")
                cursor.close()
            else:
                st.warning('This file does not have any data', icon="⚠️")

    #entering data
    with tab2:
        id=st.number_input("Enter the id:", format="%0.0f")
        Year=st.number_input("Enter the Year:", format="%0.0f")
        Week=st.number_input("Enter the Week:", format="%0.0f")
        Date=st.date_input("Enter the Date:")
        center_id=st.number_input("Enter the center_id:", format="%0.0f")
        meal_id=st.number_input("Enter the meal_id:", format="%0.0f")
        checkout_price=st.number_input("Enter the checkout_price:", format="%0.2f")
        base_price=st.number_input("Enter the base_price:", format="%0.2f")
        emailer_for_promotion=st.number_input("Enter the emailer_for_promotion:", format="%0.0f")
        homepage_featured=st.number_input("Enter the homepage_featured:", format="%0.0f")
        city_code=st.number_input("Enter the city_code:", format="%0.0f")
        region_code=st.number_input("Enter the region_code:", format="%0.0f")
        center_type=st.text_input("Enter the center_type:")
        op_area=st.number_input("Enter the op_area:", format="%0.1f")
        category=st.text_input("Enter the category:") 
        cuisine=st.text_input("Enter the cuisine:")
        if st.button("SUBMIT"):
            if center_type!="" and category!="" and cuisine!="":
                if (id!=0 and Year!=0 and Week!=0 and center_id!=0 and meal_id!=0 and city_code!=0 and region_code!=0):
                    if (checkout_price!=0.00 and base_price!=0.00 and op_area!=0.00):
                        sql = "INSERT INTO test_data (id,Year,Week,Date,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,city_code,region_code,center_type,op_area,category,cuisine) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        record=(id,Year,Week,Date,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,city_code,region_code,center_type,op_area,category,cuisine)            
                        cursor.execute(sql,record)
                        connection.commit()
                        st.success('Record inserted successfully!', icon="✅")
                        cursor.close()
                    else:
                        st.warning('Enter the missing details', icon="⚠️")
                else:
                    st.warning('User missed an input', icon="⚠️")
            else:
                st.warning('User missed an input', icon="⚠️")
                
