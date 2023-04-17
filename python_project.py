import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# set page layout
st.set_page_config(
   page_title='Global Commodity Prices - Analytical Report',
   page_icon='🌎',
   layout='wide',
   initial_sidebar_state='expanded')

# utility function
def load_data():
    """Load the cleaned data"""
    # get your data; read with pandas and store in a variable
    df= "datasets/global_food_prices.csv"
    prices_table=pd.read_csv(df)
    
    # remove unwanted columns
    prices_table.drop('mp_commoditysource', axis=1, inplace=True)
    prices_table.drop('cur_id', axis=1, inplace=True)
    
    # rename the columns
    prices_table.rename(columns={
        prices_table.columns[0]:'Country ID',
        prices_table.columns[1]:'Country Name',
        prices_table.columns[2]:'Locality ID',
        prices_table.columns[3]:'Locality Name',
        prices_table.columns[4]:'Market ID',
        prices_table.columns[5]:'Market Name',
        prices_table.columns[6]:'Commodity Purchased ID',
        prices_table.columns[7]:'Commodity Purchased',
        prices_table.columns[8]:'Name Of Currency',
        prices_table.columns[9]:'Market Type ID',
        prices_table.columns[10]:'Market Type',
        prices_table.columns[11]:'Measurement ID',
        prices_table.columns[12]:'Unit Of Goods Measurement',
        prices_table.columns[13]:'Month',
        prices_table.columns[14]:'Year',
        prices_table.columns[15]:'Price Paid'
                                },inplace=True)
    
    # split commodity column to retain only the commodity name
    goods=[]
    for good in prices_table['Commodity Purchased'].str.split(' - '):
        goods.append(good[0])
    # overwrite the commodity column
    prices_table['Commodity Purchased']=goods
    
    # define each month number in a dictionary with its month number as key
    month_name={
        1:'January',
        2:'February',
        3:'March',
        4:'April',
        5:'May',
        6:'June',
        7:'July',
        8:'August',
        9:'September',
        10:'October',
        11:'November',
        12:'December'
    }
    
    # change the month number to its month name
    prices_table.Month=prices_table.Month.map(month_name)
    
    return prices_table

prices_table=load_data()
# store the minimum and maximum years in a variable
min_year=prices_table['Year'][prices_table['Year'].idxmin()]
max_year=prices_table['Year'][prices_table['Year'].idxmax()]
st.title(f'Global Food Prices ({min_year} - {max_year}) - Analytical Report')

# utility variables
countrygrp=prices_table.groupby('Country Name')
yeargrp=prices_table.groupby('Year')
total_food_purchases=prices_table['Commodity Purchased'].count()

# sidebar to select a country and year to filter the charts
with st.sidebar:
    st.subheader('Pick a country to view more details')
    selected_country=st.selectbox('Select a Country', list(prices_table['Country Name'].unique()))
    selected_country_details=countrygrp.get_group(selected_country)
with st.sidebar:
    st.subheader('Pick a Year to view more details')
    selected_year=st.selectbox('Select a Year', list(selected_country_details['Year'].unique()))
    selected_year_details=yeargrp.get_group(selected_year)
# checkbox in sidebar to choose what chart category to display
lct=st.sidebar.checkbox("Location Info")
cmd_prch=st.sidebar.checkbox("Commodity Purchases Info")
mrk_typ=st.sidebar.checkbox("Market Type Info")
prices=st.sidebar.checkbox("Prices Info")

#utility variables
food_purchases=selected_year_details['Commodity Purchased'].count()
number_of_countries=len(prices_table['Country Name'].unique())
number_of_commodities=len(prices_table['Commodity Purchased'].unique())

st.write(f'This global report shows the overview of food purchases in {number_of_countries} countries between the years {min_year} and {max_year}. This report displays data on the countries involved, locality names, market names, commodity names, currencies used, market types, unit of measurements, month names, years and purchase prices.')

# display broad information about the data 
st.header('Overview')
col0,col1,col2,col3=st.columns(4)
with col0:
    st.subheader(total_food_purchases)
    st.caption('Number of Purchases')
with col1:
    st.subheader(number_of_commodities)
    st.caption('Number of Commodities')
with col2:
    st.subheader(number_of_countries)
    st.caption('Number of Countries')
with col3:
    st.subheader(len(prices_table['Year'].unique()))
    st.caption('Number of Years')
    
st.write(f'There were a total of {food_purchases} commodity purchases in {selected_year}')

# if location info is selected from the sidebar, show this location group
if lct:
    st.header('Locations')
    col4,col5=st.columns(2)
    with col4:
        # table of number of purchases per locality in selected country for a year
        st.subheader(f'Localities in {selected_country} ({selected_year})')
        table_data1=prices_table.groupby(['Country Name','Year']).get_group((selected_country,selected_year))[['Locality ID', 'Locality Name']].value_counts().rename('Number of Purchases')
        st.write(table_data1)
    with col5:
        # table of number of purchases per market in selected country for a year
        st.subheader(f'Markets in {selected_country} ({selected_year})')
        table_data2=prices_table.groupby(['Country Name','Year']).get_group((selected_country,selected_year))[['Market ID', 'Market Name']].value_counts().rename('Number of Purchases')
        st.write(table_data2)
    
# if commodity purchases info is selected from the sidebar, show this purchases group
if cmd_prch:
    st.header('Commodity Purchases')
    col6,col7=st.columns(2)
    with col6:
        # line chart of number of purchases per year
        st.subheader(f'{min_year} - {max_year}')
        line_data=prices_table.groupby('Year')['Commodity Purchased'].count()
        st.line_chart(line_data)
        mean_purchases=yeargrp['Commodity Purchased'].count().mean()
        st.write(f'On average, the yearly goods purchased amounted to {mean_purchases}')
    with col7:
        # table of number of purchases of each commodity by selected country in selected year by the unit measurement
        st.subheader(f'{selected_country} ({min_year} - {max_year})')
        st.write(selected_country_details[['Commodity Purchased','Unit Of Goods Measurement']].value_counts().rename('Total Purchases'))
    col8,col9=st.columns(2)
    with col8:
        # bar chart of commodities in a selected year by a selected country
        st.subheader(f'{selected_country} ({selected_year})')
        bar_data1=prices_table.groupby(['Year','Country Name']).get_group((selected_year, selected_country))['Commodity Purchased']
        st.bar_chart(bar_data1.value_counts())
        st.write(f'There were a total of {bar_data1.count()} commodity purchases in {selected_year} by {selected_country}')
    with col9:
        # pie chart of total purchases per month in a selected year
        st.subheader(f'Per Month ({selected_year})')
        pie_data1=selected_year_details['Month'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(pie_data1, labels=pie_data1.index, autopct='%1.2f%%')
        # display the figure
        st.pyplot(fig1)

# if Market type info is selected from the sidebar, show this market group
if mrk_typ:
    st.header('Market Type')
    col10,col11=st.columns(2)
    with col10:
        st.subheader(f'{min_year} - {max_year}')
        fig2, ax1=plt.subplots()
        pie_data2=prices_table['Market Type'].value_counts()
        ax1.pie(pie_data2, labels=pie_data2.index, autopct='%1.1f%%')
        st.pyplot(fig2)
    with col11:
        st.subheader(f'{selected_year}')
        bar_data2=prices_table.groupby('Year').get_group(selected_year)['Market Type'].value_counts()
        st.bar_chart(bar_data2)

# if Prices info is selected from the sidebar, show this prices group
if prices:
    st.header(f'Prices ({selected_country})')
    col12,col13=st.columns(2)
    with col12:
        st.subheader(f'Average Prices ({min_year} - {max_year})')
        table_data3=prices_table.groupby('Country Name').get_group(selected_country)[["Year","Commodity Purchased","Price Paid"]].groupby(['Commodity Purchased','Year']).mean()
        table_data3.rename({table_data3.columns[0]:'Average Price Paid'}, axis=1, inplace=True)
        st.write(table_data3)
    with col13:
        st.subheader(f'Average Prices ({selected_year})')
        line_data2=prices_table.groupby(['Year','Country Name']).get_group((selected_year,selected_country))[["Commodity Purchased","Price Paid"]].groupby('Commodity Purchased').mean()
        st.line_chart(line_data2)



