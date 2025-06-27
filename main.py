"""
리트리버 성능 체크 시스템 메인 실행 스크립트
"""
import os
import sys
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="리트리버 성능 체크 시스템")
    parser.add_argument("--mode", choices=["preprocess", "convert", "test", "dashboard", "all"], 
                       default="all", help="실행 모드")
    parser.add_argument("--data-size", type=int, default=10000, help="데이터 크기")
    parser.add_argument("--window-size", type=int, default=5, help="윈도우 크기 (분)")
    parser.add_argument("--api-key", type=str, help="OpenAI API 키")
    parser.add_argument("--output-dir", type=str, default="output", help="출력 디렉토리")
    
    args = parser.parse_args()
    
    print("🎯 리트리버 성능 체크 시스템 시작")
    print(f"실행 모드: {args.mode}")
    print(f"데이터 크기: {args.data_size:,}")
    print(f"윈도우 크기: {args.window_size}분")
    print("-" * 50)
    
    try:
        if args.mode in ["preprocess", "all"]:
            run_data_preprocessing(args.data_size, args.window_size)
        
        if args.mode in ["convert", "all"]:
            run_vector_conversion(args.api_key)
        
        if args.mode in ["test", "all"]:
            run_performance_test()
        
        if args.mode in ["dashboard", "all"]:
            run_dashboard()
            
    except ImportError as e:
        print(f"❌ 패키지 import 오류: {e}")
        print("다음 명령으로 가상환경에서 패키지를 설치하세요:")
        print("source venv/bin/activate && pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")
        return 1
    
    print("✅ 모든 작업이 완료되었습니다!")
    return 0

def run_data_preprocessing(data_size, window_size):
    """데이터 전처리 실행"""
    print("\n📊 1단계: 데이터 전처리")
    
    try:
        from data_preprocessor import LogicDataPreprocessor
        from config import DATA_DIR
        
        preprocessor = LogicDataPreprocessor(window_size_minutes=window_size)
        processed_df, windowed_data = preprocessor.process_data(size=data_size)
        
        # 결과 저장
        output_path = os.path.join(DATA_DIR, f"sample_data_{data_size}")
        preprocessor.save_processed_data(output_path)
        
        # 요약 정보 출력
        summary = preprocessor.get_data_summary()
        print(f"✅ 전처리 완료:")
        print(f"  - 총 레코드: {summary['total_records']:,}개")
        print(f"  - 윈도우 수: {summary['total_windows']:,}개")
        print(f"  - 윈도우당 평균 레코드: {summary['avg_records_per_window']:.1f}개")
        
        return processed_df, windowed_data
        
    except ImportError:
        print("⚠️ 데이터 전처리 모듈을 불러올 수 없습니다.")
        print("pandas, numpy 패키지가 설치되어 있는지 확인하세요.")
        return None, None

def run_vector_conversion(api_key):
    """벡터 변환 실행"""
    print("\n🔄 2단계: 벡터 데이터베이스 변환")
    
    try:
        from vector_converter import VectorConverter
        from data_preprocessor import LogicDataPreprocessor
        import pandas as pd
        import os
        from config import DATA_DIR, VIDEO_DIR, INDEX_DIR
        
        # 전처리된 데이터 로드 (또는 새로 생성)
        windowed_data_path = os.path.join(DATA_DIR, "sample_data_10000_windowed.csv")
        
        if os.path.exists(windowed_data_path):
            print("📁 기존 전처리 데이터 로드 중...")
            windowed_df = pd.read_csv(windowed_data_path)
            windowed_data = windowed_df.to_dict('records')
        else:
            print("📊 새로운 데이터 전처리 중...")
            preprocessor = LogicDataPreprocessor()
            _, windowed_data = preprocessor.process_data(size=1000)  # 테스트용 작은 크기
        
        # 벡터 변환
        converter = VectorConverter(api_key=api_key)
        chunks = converter.prepare_data_for_vectorization(windowed_data)
        
        video_path, index_path = converter.create_vector_database(
            chunks, 
            f"retriever_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # 결과 정보 출력
        db_info = converter.get_vector_database_info()
        print(f"✅ 벡터 변환 완료:")
        print(f"  - 총 청크 수: {db_info.get('total_chunks', len(chunks)):,}개")
        print(f"  - 비디오 크기: {db_info.get('video_size_mb', 0):.1f} MB")
        print(f"  - 인덱스 크기: {db_info.get('index_size_mb', 0):.1f} MB")
        print(f"  - 비디오 파일: {video_path}")
        print(f"  - 인덱스 파일: {index_path}")
        
        return video_path, index_path
        
    except ImportError as e:
        print(f"⚠️ 벡터 변환 모듈을 불러올 수 없습니다: {e}")
        print("memvid, openai 패키지가 설치되어 있는지 확인하세요.")
        return None, None

def run_performance_test():
    """성능 테스트 실행"""
    print("\n⚡ 3단계: 성능 테스트")
    
    try:
        from performance_checker import PerformanceChecker
        from vector_converter import VectorConverter
        from data_preprocessor import LogicDataPreprocessor
        import glob
        import os
        from config import VIDEO_DIR, INDEX_DIR
        
        # 최신 벡터 데이터베이스 파일 찾기
        video_files = glob.glob(os.path.join(VIDEO_DIR, "*.mp4"))
        index_files = glob.glob(os.path.join(INDEX_DIR, "*_index.json"))
        
        if not video_files or not index_files:
            print("⚠️ 벡터 데이터베이스 파일을 찾을 수 없습니다.")
            print("먼저 벡터 변환을 실행하세요.")
            return None
        
        # 가장 최근 파일 사용
        video_path = max(video_files, key=os.path.getctime)
        index_path = max(index_files, key=os.path.getctime)
        
        print(f"📁 벡터 DB 로드: {os.path.basename(video_path)}")
        
        # 벡터 변환기 및 성능 체커 초기화
        converter = VectorConverter()
        converter.load_vector_database(video_path, index_path)
        
        checker = PerformanceChecker(converter)
        
        # 테스트 데이터 준비
        preprocessor = LogicDataPreprocessor()
        _, windowed_data = preprocessor.process_data(size=1000)
        
        # 종합 성능 테스트 실행
        results = checker.run_comprehensive_performance_check(
            test_data=windowed_data[:100],  # 테스트용 샘플
            speed_runs=2,
            accuracy_sample_size=50
        )
        
        # 결과 요약 출력
        summary = checker.get_performance_summary()
        print(f"✅ 성능 테스트 완료:")
        print(f"  - 종합 점수: {summary.get('overall_score', 0):.1f}/100")
        print(f"  - 정확도: {summary.get('exact_accuracy_percent', 0):.1f}%")
        print(f"  - 평균 응답시간: {summary.get('avg_response_time_ms', 0):.0f}ms")
        print(f"  - 초당 처리량: {summary.get('queries_per_second', 0):.1f} QPS")
        print(f"  - 성능 등급: {summary.get('performance_grade', 'N/A')}")
        
        return results
        
    except ImportError as e:
        print(f"⚠️ 성능 테스트 모듈을 불러올 수 없습니다: {e}")
        return None

def run_dashboard():
    """대시보드 실행"""
    print("\n🌐 4단계: 대시보드 실행")
    
    try:
        import streamlit
        import subprocess
        import sys
        
        print("🚀 Streamlit 대시보드를 시작합니다...")
        print("브라우저에서 http://localhost:8501 로 접속하세요.")
        print("대시보드를 종료하려면 Ctrl+C를 누르세요.")
        
        # Streamlit 앱 실행
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ], capture_output=False)
        
        return result.returncode == 0
        
    except ImportError:
        print("⚠️ Streamlit이 설치되어 있지 않습니다.")
        print("다음 명령으로 설치하세요: pip install streamlit")
        return False
    except Exception as e:
        print(f"⚠️ 대시보드 실행 중 오류: {e}")
        return False

def check_dependencies():
    """의존성 체크"""
    required_packages = [
        'pandas', 'numpy', 'memvid', 'openai', 
        'streamlit', 'plotly', 'scikit-learn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 다음 패키지들이 설치되어 있지 않습니다:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n설치 명령:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 모든 의존성이 설치되어 있습니다.")
    return True

if __name__ == "__main__":
    # 의존성 체크
    print("🔍 의존성 체크 중...")
    if not check_dependencies():
        print("\n⚠️ 필요한 패키지를 먼저 설치해주세요.")
        sys.exit(1)
    
    # 메인 실행
    exit_code = main()
    sys.exit(exit_code)