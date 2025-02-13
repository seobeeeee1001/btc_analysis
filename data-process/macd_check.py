import pandas as pd
import numpy as np

# CSV 파일 읽기 (파일 경로에 맞게 수정)
df = pd.read_csv('data-process/1m_history.csv')

# 'datetime' 컬럼이 Unix timestamp인 경우, 이를 datetime으로 변환
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')  # Unix timestamp (밀리초)로 변환

# 'datetime'을 인덱스로 설정
df.set_index('datetime', inplace=True)

# EMA 계산 함수
def calculate_ema(data, window):
    return data.ewm(span=window, adjust=False).mean()

# MACD 계산 (12, 26, 9일 설정)
df['ema_12'] = calculate_ema(df['close'], 12)
df['ema_26'] = calculate_ema(df['close'], 26)
df['macd'] = df['ema_12'] - df['ema_26']

# Signal Line 계산 (9일 EMA of MACD)
df['signal'] = calculate_ema(df['macd'], 9)

# MACD Histogram 계산
df['macd_hist'] = df['macd'] - df['signal']

# RSI 계산 (14일 설정)
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['rsi'] = calculate_rsi(df['close'])

# Bollinger Bands 계산 (20일 설정, 2배 표준편차)
def calculate_bollinger_bands(data, window=20, num_std=2):
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, lower_band

df['bollinger_upper'], df['bollinger_lower'] = calculate_bollinger_bands(df['close'])

# 지표에 근접한 시점을 찾기 위한 조건 설정
df['macd_near_07'] = (df['macd'] - 0.7).abs() < 0.01
df['rsi_oversold'] = df['rsi'] < 30  # 과매도
df['rsi_overbought'] = df['rsi'] > 70  # 과매수
df['price_near_lower_band'] = (df['close'] - df['bollinger_lower']).abs() < 0.01  # Bollinger 밴드 하단 근접
df['price_near_upper_band'] = (df['close'] - df['bollinger_upper']).abs() < 0.01  # Bollinger 밴드 상단 근접

# 여러 조건을 동시에 만족하는 지표값 찾기
buy_points = df[(df['macd_near_07']) | (df['rsi_oversold']) | (df['price_near_lower_band'])]

# 수익률 계산을 위한 빈 리스트
profits = []

# 매수 시점에 대해 1시간(60분) 이내의 10% 이상 수익률 계산
for idx, buy_point in buy_points.iterrows():
    buy_price = buy_point['close']
    
    # 1시간 이내의 데이터를 가져오기 위해 'idx'가 Timestamp 객체여야 하므로 이를 확인하고 변환
    if isinstance(idx, pd.Timestamp):
        future_data = df.loc[idx:idx + pd.Timedelta(minutes=60)]
    else:
        idx = pd.to_datetime(idx)  # 만약 datetime이 아닌 경우 변환
        future_data = df.loc[idx:idx + pd.Timedelta(minutes=60)]
    
    # 60분 이내의 최고가를 구함
    max_price = future_data['high'].max()
    
    # 최대 수익률 계산
    max_profit = (max_price - buy_price) / buy_price * 100
    
    # 수익률이 10% 이상인 경우에만 기록
    if max_profit >= 10:
        profits.append({
            'buy_time': idx,
            'buy_price': buy_price,
            'max_profit': max_profit,
            'max_price': max_price,
            'condition': 'MACD: Near 0.7' if buy_point['macd_near_07'] else ('RSI: Oversold' if buy_point['rsi_oversold'] else 'Bollinger: Near Lower Band')
        })

# 결과 출력
results = pd.DataFrame(profits)
results.to_csv('results.csv', index=False)

# 결과 출력
print(results)
