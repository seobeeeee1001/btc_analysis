# btc_analysis

## 컴퓨터 네트워크 Term Project

## BTC 매수 추천 시스템

**프로젝트 주제** : BTC(비트코인)의 매수 시점을 추천하는 서비스

**프로젝트 개요 **: Binance 거래소의 웹소켓 api를 활용하여 실시간으로 BTC의 ohlcv (open,high,low,close,volume) 값을 가져와서 MACD 지표를 계산한 뒤, 매수 시점을 추천해주는 기능을 구현하였다.

**개발 환경 :** Python(fast-api), uvicorn(웹서버 게이트웨이 인터페이스), cctx (binance api 기반 라이브러리), HTML , JS

**주제선정이유 :** 
소켓 프로그래밍은 실시간성을 보장해야하는 앱에서 사용하기 바람직하다. 하지만, 실시간성을 보장하는 앱은 채팅과 증권 차트에 국한되어 있다. 채팅 보다는 핀테크에 조금 더 관심이 있어서 해당 분야로 프로젝트 주제를 정했다. 또한, 실시간으로 데이터를 받아서 처리하는 과정에서 프로그래밍 역량을 키울 수 있을 것이라 판단하였다.

**개발 일정 : **
10월 – 데이터 수집 (binance public data 활용)
11월 –
-	데이터 분석 : 지표 선정 (MACD)
-	실시간 데이터 수집 : CCTX(Binance websocket api)
-	매수 추천 시점 알고리즘 구현 ( 0.7 – MACD <= 0.05 )
12월 
-	웹 페이지 모니터링 기능 구현
-	매수 추천 표시

## 프로젝트 결과물	

일단 매수 추천 알고리즘을 구현하기 위해, 바이낸스 거래소의 차트의 4년 간의 ohlcv 데이터를 다운로드 하였다. (시가,고가,저가,종가,거래량을 뜻하는 데이터이다.) 이 과정에서 오픈 소스인 binance public data 서비스를 사용하였다. Download.py 파일을 통해 데이터를 다운로드 받고 단일 파일인 1m_history.csv로 데이터를 정리하였다. 

![image](https://github.com/user-attachments/assets/8c630966-c7f4-4a8e-b662-2a82d9b2e902)
그림 1 1m_history.csv 파일의 20행까지의 데이터


그 후 해당 csv파일을 anaylze.py 파일로 분석하여 3시간 후에 가격이 8% 이상 증가한 행 번호의 집합을 찾아냈다. 각 행 번호를 시그널 행이라고 부르겠다.



![image](https://github.com/user-attachments/assets/6591f76e-1a9f-4f21-a0a5-475d5d382a87)

그림 2 analyze 파일로 시그널 행 출력

calculate.py 파일에서 시그널 행 이전 30개의 행들의 데이터들로 MovingAvg', 'Volatility', 'RSI', 'EMA', 'MACD', 'Signal_Line', 'Upper_BB', 'Lower_BB', 'Stochastic' 와 같은 지표들을 계산하였다.
시그널 행들 간의 가장 유사한 지표를 뽑아내기 위해, 각 지표값들을 정규화한 후에 표준 편차들을 구하였고, 표준 편차가 가장 낮은 지표는 ‘MACD’ 값이었다. 또한, ‘MACD’ 값의 평균 값은 0.692588 였다.


![image](https://github.com/user-attachments/assets/8f3fedc6-1798-4f36-809c-cbfdf9094d75)
그림 3 정규화된 지표값의 표준편차 및 평균

따라서 이 MACD 값을 이용하여 매수 추천 알고리즘을 구현하였다. 
일단 ccxt라는 코인 거래 라이브러리를 이용하여 바이낸스 웹소켓 api로부터 서버에 데이터를 실시간으로 받아왔다. 받아온 데이터를 통해 macd값을 계산하였다. MACD 값은 적어도 27개의 데이터가 필요하기 때문에, 그 전까진 로딩 중이라고 표시해주었다. 계산되고 난 후에는 현재 BTC 가격과 함께 MACD 값을 웹 페이지에 표시해준다. 


![image](https://github.com/user-attachments/assets/78ba88f9-08c6-4648-af6a-e8940a638d9c)
그림 4 macd 값 계산되기 전
![image](https://github.com/user-attachments/assets/f15ed888-05bb-45d4-ac50-07f7c9ca1531)
그림 5 macd값 계산 후

MACD 값이 0.7에 근접할 때, “recommendation : 아직 거래하지 마세요.. “ 라는 텍스트가“recommendation : 매수 추천” 이라는 텍스트로 바뀌고 3초간 유지한다. 그 후 원래 텍스트로 돌아간다. 




