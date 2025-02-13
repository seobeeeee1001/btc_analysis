from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import ccxt.pro as ccxtpro
import numpy as np

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

async def calculate_macd(prices, short_period=12, long_period=26, signal_period=9):
    short_ema = np.mean(prices[-short_period:])
    long_ema = np.mean(prices[-long_period:])
    macd = short_ema - long_ema
    signal = np.mean(prices[-signal_period:])
    histogram = macd - signal
    return macd, signal, histogram

# Binance API keys
with open("binance_api_key", encoding="utf-8") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()

# Binance exchange instance 생성
exchange = ccxtpro.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

# 웹소켓 연결 시, index.html 파일로 응답
@app.get("/")
async def root():
    """Serve the index.html page."""
    return HTMLResponse(content=open("static/index.html", encoding="utf-8").read(), status_code=200)

# index.html 파일의 js 부분으로 server.py의 웹소켓과 연결
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    ohlcv_list = []

    try:
        while True:
            ohlcv = await exchange.watch_ohlcv(symbol="BTC/USDT", timeframe='5m') # 5분을 윈도우로 하여 ohlcv 데이터 수신
            print(ohlcv)
            close_prices = [candle[4] for candle in ohlcv] # 종가 설정
            # 최신 30개의 데이터를 반영하기 위해 30개 이상일 시, 리스트에서 pop하고, 다시 최신의 데이터 삽입
            
            if len(ohlcv_list) >= 30: 
                ohlcv_list.pop(0)
                ohlcv_list.append(close_prices[-1])

            # 데이터가 26개 이상일 때만 macd 값 계산하여 오류 최소화
            if len(ohlcv_list) >= 27:
                macd, signal, histogram = await calculate_macd(ohlcv_list)
                print(f"MACD: {macd}")

                # 웹소켓에 연결된 클라이언트에게 데이터 전송
                try:
                    await websocket.send_json({
                        "macd": macd,
                        "price": close_prices[-1],
                        "recommendation": "아직 거래하지 마세요.."
                    })

                    # macd값이 0.7에 근접할 때 매수추천 시그널 보내기
                    if abs(macd - 0.7) <= 0.05:
                        print("Sending buy recommendation message")
                        await websocket.send_json({
                            "recommendation": "매수추천"
                        })
                        await asyncio.sleep(3)
                        # 3초 후에 복원하기
                        await websocket.send_json({
                            "recommendation": "아직 거래하지 마세요.."
                        })
                except Exception as send_error:
                    print(f"WebSocket send error: {send_error}")
    except Exception as e:
        print(f"Error: {e}")
        await exchange.close()
        await websocket.close()
