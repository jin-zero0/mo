#!/usr/bin/env python3
"""
리트리버 성능 체크 시스템 데모
실제 패키지 없이도 시스템 구조와 기능을 보여주는 시연용 스크립트
"""

import json
import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os

class DemoDataPreprocessor:
    """데모용 데이터 전처리 클래스"""
    
    def __init__(self, window_size_minutes: int = 5):
        self.window_size_minutes = window_size_minutes
        
    def generate_sample_data(self, size: int = 10000) -> List[Dict]:
        """샘플 로직 데이터 생성"""
        print(f"📊 {size:,}개의 샘플 데이터 생성 중...")
        
        data = []
        start_time = datetime.now()
        
        for i in range(size):
            # 시뮬레이션된 센서 데이터
            record = {
                'index_id': i + 1,
                'timestamp': start_time + timedelta(seconds=i),
                            'vibration_x': random.gauss(0, 1) + 0.5 * math.sin(i * 0.01),
            'vibration_y': random.gauss(0, 1.2) + 0.3 * math.cos(i * 0.01),
            'vibration_z': random.gauss(0, 0.8) + 0.2 * math.sin(i * 0.015),
            'temperature': 25 + random.gauss(0, 5) + 10 * math.sin(i * 0.001),
            'pressure': 100 + random.gauss(0, 10) + 5 * math.cos(i * 0.001)
            }
            
            # 5% 확률로 null값 삽입
            if random.random() < 0.05:
                if random.random() < 0.3:
                    record['vibration_x'] = None
                elif random.random() < 0.6:
                    record['temperature'] = None
            
            data.append(record)
        
        print(f"✅ 샘플 데이터 생성 완료")
        return data
    
    def preprocess_data(self, data: List[Dict]) -> List[Dict]:
        """데이터 전처리"""
        print("🔧 데이터 전처리 중...")
        
        # Null값 처리 시뮬레이션
        null_count = 0
        for record in data:
            for key in ['vibration_x', 'vibration_y', 'vibration_z', 'temperature', 'pressure']:
                if record.get(key) is None:
                    # 평균값으로 대체 (시뮬레이션)
                    if key.startswith('vibration'):
                        record[key] = random.gauss(0, 1)
                    elif key == 'temperature':
                        record[key] = random.gauss(25, 5)
                    elif key == 'pressure':
                        record[key] = random.gauss(100, 10)
                    null_count += 1
        
        print(f"✅ Null값 {null_count}개 평균값으로 대체 완료")
        return data
    
    def apply_window_sliding(self, data: List[Dict]) -> List[Dict]:
        """윈도우 슬라이딩 적용"""
        print(f"🔄 {self.window_size_minutes}분 윈도우 슬라이딩 적용 중...")
        
        window_size_seconds = self.window_size_minutes * 60
        windows = []
        
        for i in range(0, len(data), window_size_seconds):
            window_data = data[i:i + window_size_seconds]
            if not window_data:
                continue
            
            # 윈도우 통계 계산
            vib_x_values = [r['vibration_x'] for r in window_data if r['vibration_x'] is not None]
            vib_y_values = [r['vibration_y'] for r in window_data if r['vibration_y'] is not None]
            vib_z_values = [r['vibration_z'] for r in window_data if r['vibration_z'] is not None]
            temp_values = [r['temperature'] for r in window_data if r['temperature'] is not None]
            pressure_values = [r['pressure'] for r in window_data if r['pressure'] is not None]
            
            window_summary = {
                'window_id': len(windows) + 1,
                'start_time': window_data[0]['timestamp'],
                'end_time': window_data[-1]['timestamp'],
                'data_count': len(window_data),
                'vibration_x_mean': sum(vib_x_values) / len(vib_x_values) if vib_x_values else 0,
                'vibration_x_std': (sum([(x - sum(vib_x_values)/len(vib_x_values))**2 for x in vib_x_values]) / len(vib_x_values))**0.5 if len(vib_x_values) > 1 else 0,
                'vibration_y_mean': sum(vib_y_values) / len(vib_y_values) if vib_y_values else 0,
                'vibration_y_std': (sum([(x - sum(vib_y_values)/len(vib_y_values))**2 for x in vib_y_values]) / len(vib_y_values))**0.5 if len(vib_y_values) > 1 else 0,
                'vibration_z_mean': sum(vib_z_values) / len(vib_z_values) if vib_z_values else 0,
                'vibration_z_std': (sum([(x - sum(vib_z_values)/len(vib_z_values))**2 for x in vib_z_values]) / len(vib_z_values))**0.5 if len(vib_z_values) > 1 else 0,
                'temperature_mean': sum(temp_values) / len(temp_values) if temp_values else 25,
                'temperature_std': (sum([(x - sum(temp_values)/len(temp_values))**2 for x in temp_values]) / len(temp_values))**0.5 if len(temp_values) > 1 else 0,
                'pressure_mean': sum(pressure_values) / len(pressure_values) if pressure_values else 100,
                'pressure_std': (sum([(x - sum(pressure_values)/len(pressure_values))**2 for x in pressure_values]) / len(pressure_values))**0.5 if len(pressure_values) > 1 else 0,
                'tag': f"window_{len(windows) + 1}_{self.window_size_minutes}min"
            }
            windows.append(window_summary)
        
        print(f"✅ {len(windows)}개 윈도우 생성 완료")
        return windows

class DemoVectorConverter:
    """데모용 벡터 변환 클래스"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.chunks = []
        
    def prepare_chunks(self, windowed_data: List[Dict]) -> List[Dict]:
        """윈도우 데이터를 텍스트 청크로 변환"""
        print("📝 벡터화를 위한 텍스트 청크 준비 중...")
        
        chunks = []
        for window in windowed_data:
            text_content = f"""
윈도우 ID: {window['window_id']}
시간 범위: {window['start_time']} ~ {window['end_time']}
데이터 개수: {window['data_count']}

진동 데이터:
- X축: 평균 {window['vibration_x_mean']:.3f}, 표준편차 {window['vibration_x_std']:.3f}
- Y축: 평균 {window['vibration_y_mean']:.3f}, 표준편차 {window['vibration_y_std']:.3f}
- Z축: 평균 {window['vibration_z_mean']:.3f}, 표준편차 {window['vibration_z_std']:.3f}

온도: 평균 {window['temperature_mean']:.3f}, 표준편차 {window['temperature_std']:.3f}
압력: 평균 {window['pressure_mean']:.3f}, 표준편차 {window['pressure_std']:.3f}

태그: {window['tag']}
            """.strip()
            
            chunk = {
                'content': text_content,
                'metadata': {
                    'window_id': window['window_id'],
                    'tag': window['tag'],
                    'vibration_signature': f"{window['vibration_x_mean']:.3f}_{window['vibration_y_mean']:.3f}_{window['vibration_z_mean']:.3f}"
                }
            }
            chunks.append(chunk)
        
        self.chunks = chunks
        print(f"✅ {len(chunks)}개 텍스트 청크 준비 완료")
        return chunks
    
    def create_vector_database(self, video_name: str = "demo_vibration") -> Tuple[str, str]:
        """벡터 데이터베이스 생성 시뮬레이션"""
        print(f"🎥 MemVid 벡터 데이터베이스 생성 중: {video_name}")
        
        # 생성 시간 시뮬레이션
        time.sleep(2)
        
        video_path = f"videos/{video_name}.mp4"
        index_path = f"indexes/{video_name}_index.json"
        
        # 파일 크기 시뮬레이션
        video_size_mb = len(self.chunks) * 0.1 + random.uniform(10, 50)
        index_size_mb = len(self.chunks) * 0.01 + random.uniform(1, 5)
        
        print(f"✅ 벡터 데이터베이스 생성 완료!")
        print(f"  - 비디오 파일: {video_path} ({video_size_mb:.1f} MB)")
        print(f"  - 인덱스 파일: {index_path} ({index_size_mb:.1f} MB)")
        print(f"  - 총 청크 수: {len(self.chunks):,}개")
        
        return video_path, index_path

class DemoPerformanceChecker:
    """데모용 성능 체크 클래스"""
    
    def __init__(self, chunks: List[Dict]):
        self.chunks = chunks
        
    def simulate_speed_test(self, num_queries: int = 100) -> Dict:
        """속도 테스트 시뮬레이션"""
        print(f"⚡ 속도 성능 테스트 시작: {num_queries}개 쿼리")
        
        response_times = []
        
        for i in range(num_queries):
            # 응답시간 시뮬레이션 (50-300ms)
            response_time = random.uniform(0.05, 0.3)
            response_times.append(response_time)
            
            if (i + 1) % 20 == 0:
                print(f"  진행률: {i + 1}/{num_queries}")
        
        avg_time = sum(response_times) / len(response_times)
        
        speed_results = {
            'total_queries': num_queries,
            'avg_response_time': avg_time,
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'queries_per_second': 1.0 / avg_time,
            'response_times': response_times
        }
        
        print(f"✅ 속도 테스트 완료!")
        print(f"  - 평균 응답시간: {avg_time*1000:.1f}ms")
        print(f"  - 초당 처리량: {speed_results['queries_per_second']:.1f} QPS")
        
        return speed_results
    
    def simulate_accuracy_test(self, sample_size: int = 50) -> Dict:
        """정확도 테스트 시뮬레이션"""
        print(f"🎯 정확도 성능 테스트 시작: {sample_size}개 샘플")
        
        # 정확도 시뮬레이션 (80-95% 범위)
        base_accuracy = random.uniform(0.8, 0.95)
        
        correct_matches = int(sample_size * base_accuracy)
        partial_matches = int(sample_size * 0.1)  # 10% 부분 매칭
        no_matches = sample_size - correct_matches - partial_matches
        
        accuracy_results = {
            'total_tests': sample_size,
            'correct_matches': correct_matches,
            'partial_matches': partial_matches,
            'no_matches': no_matches,
            'exact_accuracy': (correct_matches / sample_size) * 100,
            'partial_accuracy': ((correct_matches + partial_matches) / sample_size) * 100
        }
        
        print(f"✅ 정확도 테스트 완료!")
        print(f"  - 정확한 매칭: {correct_matches}/{sample_size} ({accuracy_results['exact_accuracy']:.1f}%)")
        print(f"  - 부분 매칭: {partial_matches}/{sample_size}")
        print(f"  - 매칭 실패: {no_matches}/{sample_size}")
        
        return accuracy_results
    
    def calculate_overall_score(self, speed_results: Dict, accuracy_results: Dict) -> Dict:
        """종합 점수 계산"""
        # 속도 점수 (100ms 기준)
        speed_score = min(100, (0.1 / speed_results['avg_response_time']) * 100)
        
        # 정확도 점수
        accuracy_score = accuracy_results['exact_accuracy']
        
        # 가중 평균 (정확도 70%, 속도 30%)
        overall_score = accuracy_score * 0.7 + speed_score * 0.3
        
        return {
            'overall_score': min(100, overall_score),
            'speed_score': speed_score,
            'accuracy_score': accuracy_score,
            'grade': self.get_grade(overall_score)
        }
    
    def get_grade(self, score: float) -> str:
        """성능 등급 반환"""
        if score >= 90:
            return "A+ (최우수)"
        elif score >= 80:
            return "A (우수)"
        elif score >= 70:
            return "B+ (양호)"
        elif score >= 60:
            return "B (보통)"
        elif score >= 50:
            return "C (개선필요)"
        else:
            return "D (불량)"

def generate_demo_report(results: Dict) -> str:
    """데모 리포트 생성"""
    summary = results['summary']
    timestamp = results['timestamp']
    
    report = f"""
=== 리트리버 성능 체크 리포트 (데모) ===

테스트 일시: {timestamp}

🎯 종합 결과
- 종합 점수: {summary['overall_score']:.1f}/100 ({summary['grade']})
- 정확도: {summary['accuracy_score']:.1f}%
- 속도 점수: {summary['speed_score']:.1f}점
- 평균 응답시간: {results['speed']['avg_response_time']*1000:.1f}ms
- 초당 처리량: {results['speed']['queries_per_second']:.1f} QPS

⚡ 속도 성능
- 평균 응답시간: {results['speed']['avg_response_time']*1000:.1f}ms
- 최소 응답시간: {results['speed']['min_response_time']*1000:.1f}ms
- 최대 응답시간: {results['speed']['max_response_time']*1000:.1f}ms
- 총 쿼리 수: {results['speed']['total_queries']:,}개

🎯 정확도 성능
- 정확한 매칭: {results['accuracy']['correct_matches']}/{results['accuracy']['total_tests']} ({results['accuracy']['exact_accuracy']:.1f}%)
- 부분 매칭: {results['accuracy']['partial_matches']}/{results['accuracy']['total_tests']}
- 매칭 실패: {results['accuracy']['no_matches']}/{results['accuracy']['total_tests']}

💾 시스템 정보
- 총 데이터: {results['data_info']['total_records']:,}개
- 윈도우 수: {results['data_info']['total_windows']:,}개
- 윈도우 크기: {results['data_info']['window_size']}분

📋 권장사항
"""
    
    if summary['overall_score'] >= 80:
        report += "✅ 우수한 성능입니다. 현재 설정을 유지하세요.\n"
    elif summary['overall_score'] >= 60:
        report += "⚠️ 보통 성능입니다. 다음을 고려해보세요:\n"
        if results['speed']['avg_response_time'] > 0.2:
            report += "  - 응답시간 개선 필요\n"
        if summary['accuracy_score'] < 85:
            report += "  - 정확도 개선 필요\n"
    else:
        report += "❌ 성능 개선이 필요합니다:\n"
        report += "  - 시스템 설정 재검토 필요\n"
        report += "  - 데이터 품질 확인 필요\n"
    
    return report

def main():
    """메인 데모 실행"""
    print("🎯 리트리버 성능 체크 시스템 데모")
    print("=" * 50)
    
    # 1. 데이터 전처리
    print("\n📊 1단계: 데이터 전처리")
    preprocessor = DemoDataPreprocessor(window_size_minutes=5)
    
    raw_data = preprocessor.generate_sample_data(size=10000)
    processed_data = preprocessor.preprocess_data(raw_data)
    windowed_data = preprocessor.apply_window_sliding(processed_data)
    
    # 2. 벡터 변환
    print("\n🔄 2단계: 벡터 데이터베이스 변환")
    converter = DemoVectorConverter(api_key="demo-api-key")
    chunks = converter.prepare_chunks(windowed_data)
    video_path, index_path = converter.create_vector_database("demo_retriever_test")
    
    # 3. 성능 테스트
    print("\n⚡ 3단계: 성능 테스트")
    checker = DemoPerformanceChecker(chunks)
    
    speed_results = checker.simulate_speed_test(num_queries=100)
    accuracy_results = checker.simulate_accuracy_test(sample_size=50)
    summary = checker.calculate_overall_score(speed_results, accuracy_results)
    
    # 4. 결과 정리
    print("\n📊 4단계: 결과 정리")
    
    comprehensive_results = {
        'timestamp': datetime.now().isoformat(),
        'data_info': {
            'total_records': len(processed_data),
            'total_windows': len(windowed_data),
            'window_size': 5
        },
        'vector_database': {
            'video_path': video_path,
            'index_path': index_path,
            'total_chunks': len(chunks)
        },
        'speed': speed_results,
        'accuracy': accuracy_results,
        'summary': summary
    }
    
    # 5. 결과 출력
    print("\n" + "=" * 50)
    print("🎉 데모 결과 요약")
    print("=" * 50)
    
    print(f"📊 데이터 처리:")
    print(f"  - 총 레코드: {len(processed_data):,}개")
    print(f"  - 윈도우 수: {len(windowed_data):,}개")
    print(f"  - 텍스트 청크: {len(chunks):,}개")
    
    print(f"\n⚡ 속도 성능:")
    print(f"  - 평균 응답시간: {speed_results['avg_response_time']*1000:.1f}ms")
    print(f"  - 초당 처리량: {speed_results['queries_per_second']:.1f} QPS")
    
    print(f"\n🎯 정확도 성능:")
    print(f"  - 정확도: {accuracy_results['exact_accuracy']:.1f}%")
    print(f"  - 부분 정확도: {accuracy_results['partial_accuracy']:.1f}%")
    
    print(f"\n🏆 종합 결과:")
    print(f"  - 종합 점수: {summary['overall_score']:.1f}/100")
    print(f"  - 성능 등급: {summary['grade']}")
    
    # 6. 리포트 저장
    print(f"\n💾 리포트 저장:")
    
    # JSON 결과 저장
    os.makedirs("output", exist_ok=True)
    json_filename = f"output/demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, indent=2, default=str, ensure_ascii=False)
    print(f"  - JSON 결과: {json_filename}")
    
    # 텍스트 리포트 저장
    report = generate_demo_report(comprehensive_results)
    report_filename = f"output/demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  - 텍스트 리포트: {report_filename}")
    
    print("\n✅ 데모 완료! 실제 시스템에서는 MemVid와 OpenAI API를 사용합니다.")
    print("\n📋 다음 단계:")
    print("  1. 가상환경 설정: python3 -m venv venv && source venv/bin/activate")
    print("  2. 패키지 설치: pip install -r requirements.txt")
    print("  3. API 키 설정: export OPENAI_API_KEY='your-key'")
    print("  4. 실제 실행: python main.py --mode all --api-key YOUR_KEY")
    print("  5. 대시보드: streamlit run dashboard.py")

if __name__ == "__main__":
    main()