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
    deleting_all_rows="""truncate table predicted_datafile""" 
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
                
#Data Predictions
#Preparing training_data
if selected == "Predictions":
    SQL_Query = pd.read_sql_query('''select id,Year,Week,Date,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,num_orders,city_code,region_code,center_type,op_area,category,cuisine from train_data''', connection)
    train_data = pd.DataFrame(SQL_Query, columns=['id','Year','Week','Date','center_id','meal_id','checkout_price','base_price','emailer_for_promotion','homepage_featured','num_orders','city_code','region_code','center_type','op_area','category','cuisine'])
    encoder=LabelEncoder()
    encoder2=LabelEncoder()
    encoder3=LabelEncoder()
    train_data['category']=encoder.fit_transform(train_data['category'])
    train_data['center_type']=encoder2.fit_transform(train_data['center_type'])
    train_data['cuisine']=encoder3.fit_transform(train_data['cuisine'])
    outlier_index = train_data[(train_data['num_orders']>15000)].index
    train_data.drop(outlier_index,inplace = True)

    #correlation
    train_data1= train_data.drop(['id'], axis=1)
    correlation = train_data1.corr(method='pearson')
    columns = correlation.nlargest(8, 'num_orders').index

    #Randomforest model
    features = columns.drop(['num_orders'])
    main_data2 = train_data[features]
    X = main_data2
    y = train_data['num_orders']
    from sklearn.model_selection import train_test_split
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.25,random_state=0)

    RF = RandomForestRegressor()
    RF.fit(x_train, y_train)
    y_pred = RF.predict(x_test)
    y_pred[y_pred<0] = 0
    RMSEL=mean_squared_log_error(y_test, y_pred)
    RMSEL=np.sqrt(RMSEL)

    #preparing test_data
    SQL_Query = pd.read_sql_query('''select id,Year,Week,Date,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,city_code,region_code,center_type,op_area,category,cuisine from test_data''', connection)
    test_data = pd.DataFrame(SQL_Query, columns=['id','Year','Week','Date','center_id','meal_id','checkout_price','base_price','emailer_for_promotion','homepage_featured','city_code','region_code','center_type','op_area','category','cuisine'])
    test_df=test_data.copy()
    test_data['category']=encoder.fit_transform(test_data['category'])
    test_data['center_type']=encoder2.fit_transform(test_data['center_type'])
    test_data['cuisine']=encoder3.fit_transform(test_data['cuisine'])
    test_data_final=test_data[['homepage_featured','emailer_for_promotion','op_area','cuisine','city_code','region_code','category']]
    pred_test_data= RF.predict(test_data_final)
    pred_test_data[pred_test_data<0] = 0
    submit = pd.DataFrame({'id' :test_data['id'],'num_orders' : pred_test_data})
    Predicted_datafile= pd.merge(test_df,submit, on='id')
    #st.write(Predicted_datafile)

    #Inserting the predicted file to SQL and PowerBI
    sql = "INSERT INTO predicted_datafile (id,Year,Week,Date,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,city_code,region_code,center_type,op_area,category,cuisine,num_orders) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    sql_cols = ['id','Year','Week','Date','center_id','meal_id','checkout_price','base_price','emailer_for_promotion','homepage_featured','city_code','region_code','center_type','op_area','category','cuisine','num_orders']
    #Insert Dataframe into SQL Server
    cursor.executemany(sql,Predicted_datafile[sql_cols].values.tolist())
    connection.commit()
    #st.write(cursor.rowcount, "Record inserted successfully into Predicted_datafile table")
    cursor.close()
    @st.cache
    def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    csv = convert_df(Predicted_datafile)

    #st.download_button(
        #label="DOWNLOAD THE DATA",
        #data=csv,
        #file_name='Predicted_data.csv',
        #mime='text/csv',
    #)
    SQL_Query = pd.read_sql_query('''select id,Year,Week,Date,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,city_code,region_code,center_type,op_area,category,cuisine,num_orders from Predicted_datafile''', connection)
    Predicted_datafile = pd.DataFrame(SQL_Query, columns=['id','Year','Week','Date','center_id','meal_id','checkout_price','base_price','emailer_for_promotion','homepage_featured','city_code','region_code','center_type','op_area','category','cuisine','num_orders'])
    st.subheader("Sum of Orders on weekly basis")
    Predicted_datafile['Date']=Predicted_datafile['Date'].dt.date
    weeklywise_orders_info=Predicted_datafile.groupby('Date')['num_orders'].agg(['sum'])
    df = weeklywise_orders_info.sort_values(by=['Date'])
    st.markdown("""The below chart shows *predicted number of orders* for the desired following weeks""")
    st.bar_chart(df)
    if st.button('Show Dashboard'):
        js = "window.open('https://app.powerbi.com/groups/me/reports/f837e5e9-9ab9-42a0-8a9a-731338def630/ReportSection')"  # New tab or window
        html = '<img src onerror="{}">'.format(js)
        div = Div(text=html)
        st.bokeh_chart(div)
