import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import requests

# 1. 앱 화면 설정 (예쁜 디자인)
st.set_page_config(page_title="주식 타점 매니저", layout="wide")
st.title("📈 주식 매수/매도 타점 AI 대시보드")

# 사이드바 설정 (종목 선택 및 알림 설정)
with st.sidebar:
    st.header("⚙️ 설정")
    target_stock = st.text_input("종목 코드 입력", "005930.KS") # 삼성전자 기본
    tele_token = st.text_input("텔레그램 토큰", type="password")
    chat_id = st.text_input("채팅 ID")
    btn_notify = st.button("🔔 지금 휴대폰으로 알림 보내기")

# 2. 데이터 불러오기
df = yf.download(target_stock, period="1y")
df['RSI'] = ta.rsi(df['Close'], length=14)

# 3. 메인 화면 - 현재 상태 요약
last_price = df['Close'].iloc[-1]
last_rsi = df['RSI'].iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("현재 주가", f"{last_price:,.0f}원")
col2.metric("RSI 지표", f"{last_rsi:.2f}")

if last_rsi <= 30:
    col3.success("매수 추천: 과매도 구간")
elif last_rsi >= 70:
    col3.error("매도 추천: 과매수 구간")
else:
    col3.warning("관망: 평범한 구간")

# 4. 예쁜 차트 그리기 (Plotly 사용)
fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="주가")])
fig.update_layout(title=f"{target_stock} 주가 흐름", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# 5. 알림 기능 로직
if btn_notify:
    if tele_token and chat_id:
        msg = f"[{target_stock}] 현재가: {last_price:,.0f}원\nRSI: {last_rsi:.2f}\n"
        status = "매수하세요!" if last_rsi <= 30 else "매도하세요!" if last_rsi >= 70 else "관망하세요."
        url = f"https://telegram.org{tele_token}/sendMessage?chat_id={chat_id}&text={msg + status}"
        requests.get(url)
        st.toast("텔레그램으로 알림을 보냈습니다!")
    else:
        st.error("텔레그램 설정값을 입력해주세요
