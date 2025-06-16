import streamlit as st
import numpy as np
import yfinance as yf
import pandas as pd
import plotly.express as px
st.title("Stock Dashboard")
# Sidebar inputs
ticker = st.sidebar.text_input('Ticker Symbol', 'AAPL').upper()
start_date = st.sidebar.date_input('Start Date', pd.to_datetime('2023-01-01'))
end_date = st.sidebar.date_input('End Date', pd.to_datetime('2024-01-01'))

# Only run if ticker is entered and date range is valid
if ticker and start_date < end_date:
    st.write(f"Fetching data for **{ticker}** from {start_date} to {end_date}...")

    data = yf.download(ticker, start=start_date, end=end_date, group_by='ticker')

if isinstance(data.columns, pd.MultiIndex):
    data.columns = ['_'.join(col) for col in data.columns]

if data.empty:
    st.error(f"No data found for '{ticker}' between {start_date} and {end_date}.")
else:
    st.success(f"Data loaded successfully for {ticker}")
    st.dataframe(data)

    # Adjust the y value in the plot accordingly
    close_col = f"{ticker}_Close" if isinstance(data.columns, pd.Index) else 'Close'
    fig = px.line(data, x=data.index, y=close_col, title=f'{ticker} Closing Price')
    st.plotly_chart(fig)

    pricing_data, fundamental_data, news = st.tabs(['Pricing Data', 'Fundamental Data', 'Top 10 News'])
    with pricing_data:
        st.header('Price Movements')
        data2 =data 
        data2['% Change'] = data['AAPL_Volume'] / data['AAPL_Volume'].shift(1) -1
        data2.dropna(inplace=True)
        st.write(data2)
        annual_return = data2['% Change'].mean()*252*100
        st.write('Annual Return is', annual_return,'%')
        stdev=np.std(data2['% Change'])*np.sqrt(252)
        st.write('Standard Deviation is ',stdev*100,'%')
        st.write('Risk Adj. Return is ',annual_return/(stdev*100))
    
    from alpha_vantage.fundamentaldata import FundamentalData
    with fundamental_data:
        key= 'ABDOENXXWYII4766'
        fd=FundamentalData(key,output_format = 'pandas')
        st.subheader('Balance Sheet')
        balance_sheet=fd.get_balance_sheet_annual(ticker)[0]
        bs=balance_sheet.T[2:]
        bs.columns=list(balance_sheet.T.iloc[0])
        st.write(bs)
        st.subheader('Income Statement')
        income_statement=fd.get_income_statement_annual(ticker)[0]
        is1=income_statement.T[2:]
        is1.columns=list(income_statement.T.iloc[0])
        st.write(is1)
        st.subheader('Cash Flow Statement')
        cash_flow=fd.get_cash_flow_annual(ticker)[0]
        cf=cash_flow.T[2:]
        st.write(cf)
    

    
    from stocknews import StockNews
    with news:
        st.header(f'News of {ticker}')
        sn=StockNews(ticker, save_news=False)
        df_news = sn.read_rss()
        for i in range(10):
            st.subheader(f'News {i+1}')
            st.write(df_news['published'][i])
            st.write(df_news['title'][i])
            st.write(df_news['summary'][i])
            title_sentiment=df_news['sentiment_title'][i]
            st.write(f'Title Sentiment {title_sentiment}')
            news_sentiment = df_news['sentiment_summary'][i]
            st.write(f'News Sentiment {news_sentiment}')