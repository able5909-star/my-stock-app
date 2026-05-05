import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import requests

# 앱 상단 제목과 아이콘
st.set_page_config(page_title="주식 타점기", page_icon="📈")

st.title("🚀 나만의 주식 매매 타점 앱")

# 사이드바: 설정값 입력
with st.sidebar:
    st.header("설정")
    target_stock = st.text_input("종목코드 (한국은 .KS 붙이기)", "005930.KS")
    token = st.text_input("텔레그램 봇 토큰", type="password")
    chat_id = st.text_input("텔레그램 채팅 ID")
    send_alarm = st.button("🔔 지금 휴대폰으로 알림 전송")

# 데이터 가져오기
df = yf.download(target_stock, period="1y")
df['RSI'] = ta.rsi(df['Close'], length=14)

# 현재 상태 분석
price = df['Close'].iloc[-1]
rsi = df['RSI'].iloc[-1]

# 화면 레이아웃
col1, col2 = st.columns(2)
col1.metric("현재가", f"{price:,.0f}원")
col2.metric("RSI 지표", f"{rsi:.2f}")

# 매수/매도 판단 알람창
if rsi <= 30:
    st.success("✅ 지금은 [매수] 타이밍입니다! (과매도)")
elif rsi >= 70:
    st.error("🚨 지금은 [매도] 타이밍입니다! (과매수)")
else:
    st.info("💎 지금은 [관망] 상태입니다.")

# 주가 차트
fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
fig.update_layout(title=f"{target_stock} 최근 흐름", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# 텔레그램 알림 발송 기능
if send_alarm:
    if token and chat_id:
        status = "매수추천" if rsi <= 30 else "매도추천" if rsi >= 70 else "관망중"
        text = f"[{target_stock}]\n가격: {price:,.0f}원\nRSI: {rsi:.2f}\n결과: {status}"
        url = f"https://telegram.org{token}/sendMessage?chat_id={chat_id}&text={text}"
        requests.get(url)
        st.toast("알림이 전송되었습니다!")
    else:
        st.warning("사이드바에 텔레그램 토큰과 ID를 먼저 입력하세요!")

