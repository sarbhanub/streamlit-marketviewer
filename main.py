# author: sarbhanub
# link: github.com/sarbhanub
# date: 04.01.2022

# imports
import streamlit as st
st.set_page_config(page_title='Market Viewer', layout = 'wide', initial_sidebar_state = 'auto')
import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta
import plotly.express as px
import requests


# hide decoration bar
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden}
        footer {visibility: hidden}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

if __name__ == "__main__":
    # inputs
    ticker = st.text_input('Ticker Symbol (For non-US markets, add the market extension. Eg. For NSE, enter ".NS")', 'AAPL') # Ticker value input
    interval = st.radio("Interval", ["Every minute", "Daily"], horizontal=True)
    intervals = {"Every minute": "1m", "Daily": "1d"}

    if interval == "Every minute":
        range = st.radio("Range", ["1D", "7D"], index=0, horizontal=True)
    else:
        range = st.radio("Range", ["7D", "1M", "6M", "1Y", "5Y", "MAX"], index=1, horizontal=True)

    ranges = {"1D": 1, "7D": 7, "1M": 31, "6M": 183, "1Y": 366, "5Y": 1825, "MAX": 9999}
    values = st.radio("Values", ["Close", "Open", "High", "Low", "Volume"], horizontal=True)

    # exception handling
    try:
        tic = yf.Ticker(ticker)
        infodict = tic.info
        df = tic.history(interval=intervals.get(interval), start=date.today() - relativedelta(days=ranges.get(range)), end=date.today())

        def human_format(num):
            magnitude = 0
            while abs(num) >= 1000:
                magnitude += 1
                num /= 1000.0
            return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

        with st.sidebar:
            st.write("**At a Glance**")
            st.write("**Name:** "+str(infodict.get('longName')))
            st.write("**Symbol:** "+str(infodict.get('symbol')))
            st.write("**Currency:** "+str(infodict.get('currency')))
            st.write("**Range:** "+str(infodict.get('regularMarketDayRange')))
            st.write("**Analyst Rating:** "+str(infodict.get('averageAnalystRating')))
            st.write("**Market Cap:** "+str(human_format(infodict.get('marketCap'))))
            st.write("**Exchange:** "+str(infodict.get('exchange')))
            st.write("**Market State:** "+str(infodict.get('marketState')))
            # st.write("**:** "+str(infodict.get('')))

        # values
        curr_price = round(df['Close'].iloc[-1], 2)
        price_change = round((((curr_price - df['Close'].iloc[0])/df['Close'].iloc[0])*100), 2)
        vol_sold = human_format(df['Volume'].iloc[-1])
        avg_vol = df['Volume'].mean()
        vol_change = round((((avg_vol-df['Volume'].iloc[-1])/avg_vol)*100), 2)

        # cols
        if (str(infodict.get('marketState'))=='CLOSED'):
            met1_show = "Last Price"
        else:
            met1_show = "Current Price"

        met1, met2 = st.columns(2)
        met1.metric(met1_show, str(curr_price)+str(infodict.get('currency')), str(price_change)+"%")
        met2.metric("Trade Volume", str(vol_sold), str(vol_change)+"%")
        config = {'displayModeBar': False}

        if(values == 'Volume'):
            if (vol_change < 0):
                plot1_c = 'red'
            else:
                plot1_c = 'green'

            plot1 = px.bar(df, x=df.index, y=values)
            plot1.update_traces(marker_color=plot1_c)

        else:
            if (price_change < 0):
                plot1_c = 'red'
            else:
                plot1_c = 'green'

            plot1 = px.line(df, x=df.index, y=values, labels=None)
            plot1.update_traces(line_color=plot1_c, line_width=2)

        st.plotly_chart(plot1, theme="streamlit", use_container_width=True, config=config)
        
    except(requests.exceptions.HTTPError, TypeError, AttributeError):
        if (len(ticker)==0):
            st.write("Enter ticker name")
        else:
            st.write("Invalid ticker")