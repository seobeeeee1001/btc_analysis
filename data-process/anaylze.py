import pandas as pd

# CSV 파일 읽기
df = pd.read_csv('1m_history.csv')

# 'close' 값을 180행(3시간) 뒤로 이동시킨 열 생성
df['close_180'] = df['close'].shift(-180)

# 10% 이상 증가한 경우를 조건으로 필터링
condition = df['close_180'] >= df['close'] * 1.08

# 조건에 맞는 행의 인덱스 출력
result_indices = df[condition].index.tolist()

# 연속된 인덱스들 제외
non_consecutive_indices = [result_indices[0]]  # 첫 번째 인덱스는 무조건 추가

for i in range(1, len(result_indices)):
    if result_indices[i] != result_indices[i-1] + 1:  # 이전 인덱스와 차이가 1이 아닌 경우만 추가
        non_consecutive_indices.append(result_indices[i])

print("The rows where close increased by more than 15% within 20 rows (non-consecutive) are:", non_consecutive_indices)
