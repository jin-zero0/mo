"""
로직 데이터 전처리 모듈
시간 및 설비 데이터의 null값 처리와 윈도우 슬라이딩 기능
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogicDataPreprocessor:
    """로직 데이터 전처리 클래스"""
    
    def __init__(self, window_size_minutes: int = 5):
        self.window_size_minutes = window_size_minutes
        self.processed_data = None
        self.windowed_data = None
        
    def generate_sample_data(self, size: int = 10000) -> pd.DataFrame:
        """샘플 로직 데이터 생성 (시간 + 설비 데이터)"""
        logger.info(f"{size}개의 샘플 데이터 생성 중...")
        
        # 시간 데이터 생성 (초 단위)
        start_time = datetime.now()
        timestamps = [start_time + timedelta(seconds=i) for i in range(size)]
        
        # 설비 데이터 생성 (진동값)
        np.random.seed(42)
        vibration_x = np.random.normal(0, 1, size) + np.sin(np.linspace(0, 4*np.pi, size))
        vibration_y = np.random.normal(0, 1.2, size) + np.cos(np.linspace(0, 3*np.pi, size))
        vibration_z = np.random.normal(0, 0.8, size) + np.sin(np.linspace(0, 5*np.pi, size))
        
        temperature = 25 + np.random.normal(0, 5, size) + 10*np.sin(np.linspace(0, 2*np.pi, size))
        pressure = 100 + np.random.normal(0, 10, size) + 5*np.cos(np.linspace(0, 3*np.pi, size))
        
        # null값 의도적으로 삽입 (5% 정도)
        null_indices = np.random.choice(size, int(size * 0.05), replace=False)
        vibration_x[null_indices[:len(null_indices)//3]] = np.nan
        vibration_y[null_indices[len(null_indices)//3:2*len(null_indices)//3]] = np.nan
        temperature[null_indices[2*len(null_indices)//3:]] = np.nan
        
        # 시간 데이터에도 일부 null값 삽입
        time_null_indices = np.random.choice(size, int(size * 0.02), replace=False)
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'vibration_x': vibration_x,
            'vibration_y': vibration_y,
            'vibration_z': vibration_z,
            'temperature': temperature,
            'pressure': pressure,
            'index_id': range(1, size + 1)
        })
        
        # 시간 null값 처리
        df.loc[time_null_indices, 'timestamp'] = pd.NaT
        
        logger.info(f"샘플 데이터 생성 완료: {len(df)}개")
        return df
    
    def preprocess_time_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """시간 데이터 null값 전처리"""
        logger.info("시간 데이터 null값 전처리 중...")
        
        df = df.copy()
        
        # 시간 null값 처리 - 선형 보간
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('index_id')
        
        # null이 아닌 시간값들을 기준으로 선형 보간
        df['timestamp'] = df['timestamp'].interpolate(method='time')
        
        # 여전히 null인 경우 (처음이나 끝) forward fill / backward fill
        df['timestamp'] = df['timestamp'].fillna(method='ffill').fillna(method='bfill')
        
        logger.info("시간 데이터 전처리 완료")
        return df
    
    def preprocess_equipment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """설비 데이터 null값을 평균값으로 처리"""
        logger.info("설비 데이터 null값 평균값 처리 중...")
        
        df = df.copy()
        equipment_columns = ['vibration_x', 'vibration_y', 'vibration_z', 'temperature', 'pressure']
        
        for col in equipment_columns:
            mean_value = df[col].mean()
            df[col] = df[col].fillna(mean_value)
            logger.info(f"{col} null값 {mean_value:.3f}로 대체")
        
        logger.info("설비 데이터 전처리 완료")
        return df
    
    def apply_window_sliding(self, df: pd.DataFrame) -> List[Dict]:
        """5분 윈도우 슬라이딩 기법 적용"""
        logger.info(f"{self.window_size_minutes}분 윈도우 슬라이딩 적용 중...")
        
        df = df.sort_values('timestamp')
        windowed_data = []
        
        start_time = df['timestamp'].min()
        end_time = df['timestamp'].max()
        current_time = start_time
        window_id = 1
        
        while current_time < end_time:
            window_end = current_time + timedelta(minutes=self.window_size_minutes)
            
            # 현재 윈도우에 해당하는 데이터 필터링
            window_mask = (df['timestamp'] >= current_time) & (df['timestamp'] < window_end)
            window_df = df[window_mask]
            
            if len(window_df) > 0:
                # 윈도우 내 데이터 집계
                window_summary = {
                    'window_id': window_id,
                    'start_time': current_time,
                    'end_time': window_end,
                    'data_count': len(window_df),
                    'vibration_x_mean': window_df['vibration_x'].mean(),
                    'vibration_x_std': window_df['vibration_x'].std(),
                    'vibration_y_mean': window_df['vibration_y'].mean(),
                    'vibration_y_std': window_df['vibration_y'].std(),
                    'vibration_z_mean': window_df['vibration_z'].mean(),
                    'vibration_z_std': window_df['vibration_z'].std(),
                    'temperature_mean': window_df['temperature'].mean(),
                    'temperature_std': window_df['temperature'].std(),
                    'pressure_mean': window_df['pressure'].mean(),
                    'pressure_std': window_df['pressure'].std(),
                    'index_ids': window_df['index_id'].tolist(),
                    'tag': f"window_{window_id}_{self.window_size_minutes}min"
                }
                windowed_data.append(window_summary)
                window_id += 1
            
            current_time = window_end
        
        logger.info(f"윈도우 슬라이딩 완료: {len(windowed_data)}개 윈도우")
        return windowed_data
    
    def process_data(self, data: pd.DataFrame = None, size: int = 10000) -> Tuple[pd.DataFrame, List[Dict]]:
        """전체 데이터 처리 파이프라인"""
        logger.info("데이터 전처리 파이프라인 시작")
        
        # 1. 데이터 생성 또는 사용
        if data is None:
            df = self.generate_sample_data(size)
        else:
            df = data.copy()
        
        # 2. 시간 데이터 전처리
        df = self.preprocess_time_data(df)
        
        # 3. 설비 데이터 전처리
        df = self.preprocess_equipment_data(df)
        
        # 4. 윈도우 슬라이딩
        windowed_data = self.apply_window_sliding(df)
        
        self.processed_data = df
        self.windowed_data = windowed_data
        
        logger.info("데이터 전처리 파이프라인 완료")
        return df, windowed_data
    
    def save_processed_data(self, filepath: str):
        """처리된 데이터 저장"""
        if self.processed_data is not None:
            self.processed_data.to_csv(f"{filepath}_processed.csv", index=False)
            logger.info(f"전처리된 데이터 저장: {filepath}_processed.csv")
        
        if self.windowed_data is not None:
            windowed_df = pd.DataFrame(self.windowed_data)
            windowed_df.to_csv(f"{filepath}_windowed.csv", index=False)
            logger.info(f"윈도우 데이터 저장: {filepath}_windowed.csv")
    
    def get_data_summary(self) -> Dict:
        """데이터 요약 통계"""
        if self.processed_data is None or self.windowed_data is None:
            return {}
        
        return {
            'total_records': len(self.processed_data),
            'total_windows': len(self.windowed_data),
            'time_range': {
                'start': self.processed_data['timestamp'].min(),
                'end': self.processed_data['timestamp'].max()
            },
            'window_size_minutes': self.window_size_minutes,
            'avg_records_per_window': np.mean([w['data_count'] for w in self.windowed_data])
        }

if __name__ == "__main__":
    # 테스트 실행
    preprocessor = LogicDataPreprocessor(window_size_minutes=5)
    processed_df, windowed_data = preprocessor.process_data(size=10000)
    
    print("=== 데이터 전처리 결과 ===")
    print(f"전처리된 데이터: {len(processed_df)}개")
    print(f"윈도우 데이터: {len(windowed_data)}개")
    print("\n=== 데이터 요약 ===")
    summary = preprocessor.get_data_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")