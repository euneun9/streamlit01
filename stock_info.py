import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO
import plotly.graph_objects as go
import pandas as pd

import matplotlib.font_manager as fm
from datetime import datetime as dt


# caching
# 인자가 바뀌지 않는 함수 실행 결과를 저장 후 크롬의 임시 저장 폴더에 저장 후 재사용
@st.cache_data
def get_stock_info():
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
    method = "download"
    url = "{0}?method={1}".format(base_url, method)   
    df = pd.read_html(url, header=0, encoding='cp949')[0]
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df


def get_ticker_symbol(company_name):     
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values    
    ticker_symbol = code[0]
    return ticker_symbol

def stock_graph2(df):
    x_data = df.index
    fig = go.Figure(data=[go.Candlestick(x=x_data,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    st.plotly_chart(fig)


def stock_graph(df):
    x_data = df.index
    y_data = df['Close']

    # 그래프 생성
    trace = go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines',  
        name='Close Prices'    )

    # 레이아웃 설정
    layout = go.Layout(
        title='Close Prices Over Time',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Close Price')    )

    # Figure 객체 생성
    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig)


# sidebar 만들기
with st.sidebar:
    st.subheader('회사 이름과 기간을 입력하세요')
    stock_name = st.text_input("회사이름", "삼성전자")
    date_range = st.date_input(label='시작일 - 종료일',
                value=(dt(year=2024, month=7, day=1), 
                        dt(year=2024, month=7, day=22)),
                key='#date_range',
                help="The start and end date time")
    button_result = st.button('주가 데이터 확인')


st.markdown('# 무슨 주식을 사야 부자가 되려나...')


if button_result:
    # 코드 조각 추가
    ticker_symbol = get_ticker_symbol(stock_name)     
    start_p = date_range[0]               
    end_p = date_range[1] + datetime.timedelta(days=1) 
    df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p)
    df.index = df.index.date
    st.subheader(f"[{stock_name}] 주가 데이터")
    st.dataframe(df.tail(7))
    ####################################
    stock_graph2(df)
    #####################################

    excel_data = BytesIO()      
    df.to_excel(excel_data)

    st.download_button("엑셀 파일 다운로드", 
            excel_data, file_name='stock_data.xlsx')
    
