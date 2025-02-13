import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Load the CSV file
df = pd.read_csv("data-process/1m_history.csv", parse_dates=['datetime'])

# Provided indices
indices = [103701, 103703, 103724, 103731, 103733, 103756, 103759, 103791, 103832, 103971, 103973, 103987, 
           104042, 104086, 104089, 104101, 104103, 104132, 104793, 104816, 104852, 104859, 104861, 107696, 
           108694, 108699, 108701, 108704, 108706, 108745, 108750, 108807, 109353, 118683, 542606, 542611, 
           542645, 542653, 542658, 542665, 542680, 567719, 567724, 567730, 567738, 582357, 582364, 582375, 
           582381, 582422, 582428, 582459, 582466, 726533, 726542, 726557, 726561, 726568, 726576, 726582, 
           726585, 727272, 729918, 775519, 775546, 823561, 823578, 823583, 823589, 823593, 823635, 823647, 
           823658, 927973, 1012647, 1681208, 1681222, 1681229, 2004222, 2417117, 2417124]

# Indicator Calculation Functions
def calc_moving_avg(df, window):
    return df['close'].rolling(window=window).mean()

def calc_volatility(df, window):
    return df['close'].pct_change().rolling(window=window).std()

def calc_rsi(df, window=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_ema(df, window):
    return df['close'].ewm(span=window, adjust=False).mean()

def calc_macd(df, short_window=12, long_window=26, signal_window=9):
    short_ema = df['close'].ewm(span=short_window, adjust=False).mean()
    long_ema = df['close'].ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    return macd_line, signal_line

def calc_bollinger_bands(df, window=20, num_std=2):
    sma = df['close'].rolling(window=window).mean()
    rolling_std = df['close'].rolling(window=window).std()
    upper_band = sma + (rolling_std * num_std)
    lower_band = sma - (rolling_std * num_std)
    return upper_band, lower_band

def calc_stochastic_oscillator(df, window=14):
    low_min = df['low'].rolling(window=window).min()
    high_max = df['high'].rolling(window=window).max()
    stochastic = 100 * (df['close'] - low_min) / (high_max - low_min)
    return stochastic

# Calculate indicators
df['MovingAvg'] = calc_moving_avg(df, 30)
df['Volatility'] = calc_volatility(df, 30)
df['RSI'] = calc_rsi(df, 30)
df['EMA'] = calc_ema(df, 30)
df['MACD'], df['Signal_Line'] = calc_macd(df)
df['Upper_BB'], df['Lower_BB'] = calc_bollinger_bands(df)
df['Stochastic'] = calc_stochastic_oscillator(df)

# Extract values for provided indices
indicators = df.loc[indices, ['MovingAvg', 'Volatility', 'RSI', 'EMA', 'MACD', 'Signal_Line', 'Upper_BB', 'Lower_BB', 'Stochastic']].dropna()

# Normalize the indicators
scaler = MinMaxScaler()
normalized_indicators = pd.DataFrame(
    scaler.fit_transform(indicators), 
    columns=indicators.columns, 
    index=indicators.index
)

# Calculate standard deviations and means
indicator_std_devs = normalized_indicators.std()
indicator_means = normalized_indicators.mean()

# Display results
print("Normalized Indicator Standard Deviations:")
print(indicator_std_devs)

print("\nNormalized Indicator Means:")
print(indicator_means)
