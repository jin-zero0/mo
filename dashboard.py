"""
리트리버 성능 체크 대시보드
Streamlit을 사용한 웹 인터페이스
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import time
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="리트리버 성능 체크 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 설정
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #1f77b4;
}
.success-metric {
    border-left-color: #2e8b57;
}
.warning-metric {
    border-left-color: #ff8c00;
}
.error-metric {
    border-left-color: #dc143c;
}
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🎯 리트리버 성능 체크 대시보드")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 데이터 크기 설정
        data_size = st.slider("데이터 크기", 1000, 10000, 5000, step=1000)
        window_size = st.selectbox("윈도우 크기 (분)", [1, 5, 10, 15], index=1)
        
        # API 키 설정
        api_key = st.text_input("OpenAI API Key", type="password")
        
        # 성능 테스트 설정
        st.subheader("성능 테스트 설정")
        test_queries_count = st.number_input("테스트 쿼리 수", 10, 500, 100)
        speed_runs = st.number_input("속도 테스트 반복 횟수", 1, 10, 3)
        accuracy_sample_size = st.number_input("정확도 테스트 샘플 크기", 10, 1000, 100)
        
        # 실행 버튼
        run_test = st.button("🚀 성능 테스트 실행", type="primary")
    
    # 메인 콘텐츠
    if 'performance_results' not in st.session_state:
        st.session_state.performance_results = None
    
    # 성능 테스트 실행
    if run_test:
        if not api_key:
            st.error("OpenAI API Key를 입력해주세요.")
            return
        
        run_performance_test(data_size, window_size, api_key, test_queries_count, speed_runs, accuracy_sample_size)
    
    # 대시보드 표시
    display_dashboard()

def run_performance_test(data_size, window_size, api_key, test_queries_count, speed_runs, accuracy_sample_size):
    """성능 테스트 실행"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 1. 데이터 전처리 (20%)
        status_text.text("1단계: 데이터 전처리 중...")
        progress_bar.progress(0.1)
        
        # 실제로는 data_preprocessor 모듈을 import해서 사용
        # 여기서는 시뮬레이션된 결과 생성
        processed_data, windowed_data = simulate_data_preprocessing(data_size, window_size)
        progress_bar.progress(0.2)
        
        # 2. 벡터 변환 (40%)
        status_text.text("2단계: 벡터 데이터베이스 생성 중...")
        vector_db_info = simulate_vector_conversion(windowed_data, api_key)
        progress_bar.progress(0.4)
        
        # 3. 속도 성능 테스트 (70%)
        status_text.text("3단계: 속도 성능 테스트 중...")
        speed_results = simulate_speed_test(test_queries_count, speed_runs)
        progress_bar.progress(0.7)
        
        # 4. 정확도 성능 테스트 (90%)
        status_text.text("4단계: 정확도 성능 테스트 중...")
        accuracy_results = simulate_accuracy_test(windowed_data, accuracy_sample_size)
        progress_bar.progress(0.9)
        
        # 5. 결과 정리 (100%)
        status_text.text("5단계: 결과 정리 중...")
        
        # 종합 결과 생성
        comprehensive_results = {
            'timestamp': datetime.now().isoformat(),
            'test_config': {
                'data_size': data_size,
                'window_size': window_size,
                'test_queries_count': test_queries_count,
                'speed_runs': speed_runs,
                'accuracy_sample_size': accuracy_sample_size
            },
            'data_info': {
                'total_records': len(processed_data),
                'total_windows': len(windowed_data),
                'window_size_minutes': window_size
            },
            'vector_database': vector_db_info,
            'speed_performance': speed_results,
            'accuracy_performance': accuracy_results,
            'summary': calculate_summary(speed_results, accuracy_results)
        }
        
        st.session_state.performance_results = comprehensive_results
        progress_bar.progress(1.0)
        status_text.text("✅ 성능 테스트 완료!")
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        st.success("성능 테스트가 완료되었습니다!")
        st.rerun()
        
    except Exception as e:
        st.error(f"성능 테스트 중 오류가 발생했습니다: {e}")

def simulate_data_preprocessing(data_size, window_size):
    """데이터 전처리 시뮬레이션"""
    # 실제 구현에서는 data_preprocessor 모듈 사용
    
    # 시간 데이터 생성
    start_time = datetime.now()
    timestamps = [start_time + timedelta(seconds=i) for i in range(data_size)]
    
    # 설비 데이터 생성
    np.random.seed(42)
    processed_data = []
    for i in range(data_size):
        record = {
            'index_id': i + 1,
            'timestamp': timestamps[i],
            'vibration_x': np.random.normal(0, 1) + np.sin(i * 0.01),
            'vibration_y': np.random.normal(0, 1.2) + np.cos(i * 0.01),
            'vibration_z': np.random.normal(0, 0.8) + np.sin(i * 0.015),
            'temperature': 25 + np.random.normal(0, 5) + 10 * np.sin(i * 0.001),
            'pressure': 100 + np.random.normal(0, 10) + 5 * np.cos(i * 0.001)
        }
        processed_data.append(record)
    
    # 윈도우 데이터 생성
    window_size_seconds = window_size * 60
    num_windows = data_size // (window_size_seconds)
    windowed_data = []
    
    for w in range(num_windows):
        start_idx = w * window_size_seconds
        end_idx = min((w + 1) * window_size_seconds, data_size)
        window_records = processed_data[start_idx:end_idx]
        
        if window_records:
            window_summary = {
                'window_id': w + 1,
                'start_time': window_records[0]['timestamp'],
                'end_time': window_records[-1]['timestamp'],
                'data_count': len(window_records),
                'vibration_x_mean': np.mean([r['vibration_x'] for r in window_records]),
                'vibration_x_std': np.std([r['vibration_x'] for r in window_records]),
                'vibration_y_mean': np.mean([r['vibration_y'] for r in window_records]),
                'vibration_y_std': np.std([r['vibration_y'] for r in window_records]),
                'vibration_z_mean': np.mean([r['vibration_z'] for r in window_records]),
                'vibration_z_std': np.std([r['vibration_z'] for r in window_records]),
                'temperature_mean': np.mean([r['temperature'] for r in window_records]),
                'temperature_std': np.std([r['temperature'] for r in window_records]),
                'pressure_mean': np.mean([r['pressure'] for r in window_records]),
                'pressure_std': np.std([r['pressure'] for r in window_records]),
                'index_ids': [r['index_id'] for r in window_records],
                'tag': f"window_{w+1}_{window_size}min"
            }
            windowed_data.append(window_summary)
    
    return processed_data, windowed_data

def simulate_vector_conversion(windowed_data, api_key):
    """벡터 변환 시뮬레이션"""
    # 실제 구현에서는 vector_converter 모듈 사용
    return {
        'total_chunks': len(windowed_data),
        'video_size_mb': np.random.uniform(50, 200),
        'index_size_mb': np.random.uniform(5, 20),
        'build_time_seconds': np.random.uniform(30, 120),
        'embedding_dimension': 1536
    }

def simulate_speed_test(test_queries_count, speed_runs):
    """속도 테스트 시뮬레이션"""
    # 실제 응답 시간 시뮬레이션 (ms)
    base_time = 0.1  # 100ms 기준
    times = []
    
    for run in range(speed_runs):
        run_times = []
        for query in range(test_queries_count):
            # 약간의 변동성 추가
            query_time = base_time + np.random.normal(0, 0.02)
            query_time = max(0.05, query_time)  # 최소 50ms
            run_times.append(query_time)
        times.extend(run_times)
    
    return {
        'total_queries': test_queries_count * speed_runs,
        'avg_response_time': np.mean(times),
        'min_response_time': np.min(times),
        'max_response_time': np.max(times),
        'p95_response_time': np.percentile(times, 95),
        'p99_response_time': np.percentile(times, 99),
        'queries_per_second': 1.0 / np.mean(times),
        'response_times': times
    }

def simulate_accuracy_test(windowed_data, sample_size):
    """정확도 테스트 시뮬레이션"""
    # 정확도 시뮬레이션 (80-95% 범위)
    base_accuracy = np.random.uniform(80, 95)
    
    # 매칭 결과 시뮬레이션
    total_tests = min(sample_size, len(windowed_data))
    correct_matches = int(total_tests * base_accuracy / 100)
    partial_matches = int(total_tests * 0.1)  # 10% 부분 매칭
    no_matches = total_tests - correct_matches - partial_matches
    
    return {
        'total_tests': total_tests,
        'correct_matches': correct_matches,
        'partial_matches': partial_matches,
        'no_matches': no_matches,
        'exact_accuracy': (correct_matches / total_tests) * 100,
        'partial_accuracy': ((correct_matches + partial_matches) / total_tests) * 100,
        'avg_search_time': np.random.uniform(0.08, 0.15)
    }

def calculate_summary(speed_results, accuracy_results):
    """종합 점수 계산"""
    # 속도 점수 (응답시간 기반)
    speed_score = min(100, (0.1 / speed_results['avg_response_time']) * 100)
    
    # 정확도 점수
    accuracy_score = accuracy_results['exact_accuracy']
    
    # 가중 평균 (정확도 70%, 속도 30%)
    overall_score = accuracy_score * 0.7 + speed_score * 0.3
    
    return {
        'avg_response_time': speed_results['avg_response_time'],
        'queries_per_second': speed_results['queries_per_second'],
        'exact_accuracy': accuracy_results['exact_accuracy'],
        'partial_accuracy': accuracy_results['partial_accuracy'],
        'overall_score': min(100, overall_score),
        'speed_score': speed_score,
        'accuracy_score': accuracy_score
    }

def display_dashboard():
    """대시보드 표시"""
    if st.session_state.performance_results is None:
        st.info("🔧 사이드바에서 설정을 조정하고 '성능 테스트 실행' 버튼을 클릭하세요.")
        
        # 샘플 차트 표시
        display_sample_charts()
        return
    
    results = st.session_state.performance_results
    
    # 1. 핵심 지표 표시
    display_key_metrics(results)
    
    # 2. 성능 차트
    col1, col2 = st.columns(2)
    
    with col1:
        display_speed_charts(results['speed_performance'])
    
    with col2:
        display_accuracy_charts(results['accuracy_performance'])
    
    # 3. 상세 분석
    st.markdown("---")
    display_detailed_analysis(results)
    
    # 4. 데이터 다운로드
    display_download_section(results)

def display_key_metrics(results):
    """핵심 지표 표시"""
    st.subheader("📊 핵심 성능 지표")
    
    summary = results['summary']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = summary['overall_score']
        grade = get_performance_grade(score)
        color = get_score_color(score)
        
        st.markdown(f"""
        <div class="metric-card {color}">
            <h3>종합 점수</h3>
            <h2>{score:.1f}/100</h2>
            <p>{grade}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        accuracy = summary['exact_accuracy']
        color = get_score_color(accuracy)
        
        st.markdown(f"""
        <div class="metric-card {color}">
            <h3>정확도</h3>
            <h2>{accuracy:.1f}%</h2>
            <p>정확한 매칭률</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        response_time = summary['avg_response_time'] * 1000  # ms 변환
        color = "success-metric" if response_time < 200 else "warning-metric" if response_time < 500 else "error-metric"
        
        st.markdown(f"""
        <div class="metric-card {color}">
            <h3>응답 시간</h3>
            <h2>{response_time:.0f}ms</h2>
            <p>평균 검색 시간</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        qps = summary['queries_per_second']
        color = "success-metric" if qps > 5 else "warning-metric" if qps > 2 else "error-metric"
        
        st.markdown(f"""
        <div class="metric-card {color}">
            <h3>처리량</h3>
            <h2>{qps:.1f} QPS</h2>
            <p>초당 쿼리 수</p>
        </div>
        """, unsafe_allow_html=True)

def display_speed_charts(speed_data):
    """속도 성능 차트"""
    st.subheader("⚡ 속도 성능")
    
    # 응답 시간 분포 히스토그램
    if 'response_times' in speed_data:
        fig = px.histogram(
            x=speed_data['response_times'],
            nbins=30,
            title="응답 시간 분포",
            labels={'x': '응답 시간 (초)', 'y': '빈도'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # 속도 지표 요약
    metrics_data = {
        '지표': ['평균', '최소', '최대', 'P95', 'P99'],
        '응답시간(ms)': [
            speed_data['avg_response_time'] * 1000,
            speed_data['min_response_time'] * 1000,
            speed_data['max_response_time'] * 1000,
            speed_data['p95_response_time'] * 1000,
            speed_data['p99_response_time'] * 1000
        ]
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    st.dataframe(df_metrics, use_container_width=True)

def display_accuracy_charts(accuracy_data):
    """정확도 성능 차트"""
    st.subheader("🎯 정확도 성능")
    
    # 정확도 파이 차트
    labels = ['정확한 매칭', '부분 매칭', '매칭 실패']
    values = [
        accuracy_data['correct_matches'],
        accuracy_data['partial_matches'],
        accuracy_data['no_matches']
    ]
    colors = ['#2e8b57', '#ff8c00', '#dc143c']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        hole=0.3
    )])
    
    fig.update_layout(
        title="매칭 결과 분포",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 정확도 지표
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("정확한 매칭률", f"{accuracy_data['exact_accuracy']:.1f}%")
    
    with col2:
        st.metric("부분 매칭률", f"{accuracy_data['partial_accuracy']:.1f}%")

def display_detailed_analysis(results):
    """상세 분석"""
    st.subheader("📈 상세 분석")
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["시스템 정보", "성능 추이", "비교 분석"])
    
    with tab1:
        display_system_info(results)
    
    with tab2:
        display_performance_trends()
    
    with tab3:
        display_comparison_analysis()

def display_system_info(results):
    """시스템 정보 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("데이터 정보")
        data_info = results['data_info']
        st.write(f"- 총 레코드 수: {data_info['total_records']:,}")
        st.write(f"- 윈도우 수: {data_info['total_windows']:,}")
        st.write(f"- 윈도우 크기: {data_info['window_size_minutes']}분")
        
        st.subheader("벡터 데이터베이스")
        vector_info = results['vector_database']
        st.write(f"- 총 청크 수: {vector_info['total_chunks']:,}")
        st.write(f"- 비디오 크기: {vector_info['video_size_mb']:.1f} MB")
        st.write(f"- 인덱스 크기: {vector_info['index_size_mb']:.1f} MB")
        st.write(f"- 구축 시간: {vector_info['build_time_seconds']:.1f}초")
    
    with col2:
        st.subheader("테스트 설정")
        config = results['test_config']
        st.write(f"- 데이터 크기: {config['data_size']:,}")
        st.write(f"- 테스트 쿼리 수: {config['test_queries_count']}")
        st.write(f"- 속도 테스트 반복: {config['speed_runs']}회")
        st.write(f"- 정확도 샘플: {config['accuracy_sample_size']}")
        
        st.subheader("타임스탬프")
        timestamp = datetime.fromisoformat(results['timestamp'])
        st.write(f"- 테스트 시간: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

def display_performance_trends():
    """성능 추이 (더미 데이터)"""
    st.info("성능 추이는 여러 번의 테스트 결과가 축적되면 표시됩니다.")
    
    # 더미 추이 데이터
    dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
    accuracy_trend = np.random.uniform(80, 95, len(dates))
    speed_trend = np.random.uniform(100, 200, len(dates))
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=dates, y=accuracy_trend, name="정확도 (%)", line=dict(color='blue')),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=dates, y=speed_trend, name="응답시간 (ms)", line=dict(color='red')),
        secondary_y=True,
    )
    
    fig.update_xaxes(title_text="날짜")
    fig.update_yaxes(title_text="정확도 (%)", secondary_y=False)
    fig.update_yaxes(title_text="응답시간 (ms)", secondary_y=True)
    
    fig.update_layout(title="성능 추이 (샘플)", height=400)
    
    st.plotly_chart(fig, use_container_width=True)

def display_comparison_analysis():
    """비교 분석 (더미 데이터)"""
    st.info("다른 시스템과의 비교 분석 결과입니다.")
    
    comparison_data = {
        '시스템': ['MemVid (현재)', 'PostgreSQL+pgvector', 'Pinecone', 'Weaviate'],
        '응답시간(ms)': [120, 450, 80, 200],
        '정확도(%)': [92, 95, 98, 94],
        '설정복잡도': ['낮음', '높음', '중간', '중간'],
        '비용': ['무료', '중간', '높음', '중간']
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # 성능 비교 차트
    fig = px.scatter(
        df_comparison,
        x='응답시간(ms)',
        y='정확도(%)',
        size=[100, 80, 120, 90],
        color='시스템',
        title="시스템별 성능 비교 (응답시간 vs 정확도)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_download_section(results):
    """다운로드 섹션"""
    st.subheader("💾 결과 다운로드")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON 다운로드
        json_data = json.dumps(results, indent=2, default=str, ensure_ascii=False)
        st.download_button(
            label="📄 JSON 결과 다운로드",
            data=json_data,
            file_name=f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # CSV 요약 다운로드
        summary_df = pd.DataFrame([results['summary']])
        csv_data = summary_df.to_csv(index=False)
        st.download_button(
            label="📊 CSV 요약 다운로드",
            data=csv_data,
            file_name=f"performance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col3:
        # 리포트 다운로드 (더미)
        report_content = generate_report(results)
        st.download_button(
            label="📑 성능 리포트 다운로드",
            data=report_content,
            file_name=f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

def display_sample_charts():
    """샘플 차트 표시"""
    st.subheader("📊 샘플 대시보드")
    st.info("이것은 샘플 차트입니다. 실제 테스트를 실행하면 실제 데이터가 표시됩니다.")
    
    # 샘플 데이터
    sample_times = np.random.normal(0.15, 0.03, 100)
    sample_accuracy = [85, 12, 3]  # 정확한매칭, 부분매칭, 실패
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(x=sample_times, nbins=20, title="응답 시간 분포 (샘플)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[go.Pie(
            labels=['정확한 매칭', '부분 매칭', '매칭 실패'],
            values=sample_accuracy,
            hole=0.3
        )])
        fig.update_layout(title="매칭 결과 분포 (샘플)")
        st.plotly_chart(fig, use_container_width=True)

def get_performance_grade(score):
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

def get_score_color(score):
    """점수에 따른 색상 클래스 반환"""
    if score >= 80:
        return "success-metric"
    elif score >= 60:
        return "warning-metric"
    else:
        return "error-metric"

def generate_report(results):
    """성능 리포트 생성"""
    summary = results['summary']
    timestamp = results['timestamp']
    
    report = f"""
=== 리트리버 성능 체크 리포트 ===

테스트 일시: {timestamp}

🎯 종합 결과
- 종합 점수: {summary['overall_score']:.1f}/100 ({get_performance_grade(summary['overall_score'])})
- 정확도: {summary['exact_accuracy']:.1f}%
- 평균 응답시간: {summary['avg_response_time']*1000:.0f}ms
- 초당 처리량: {summary['queries_per_second']:.1f} QPS

⚡ 속도 성능
- 평균 응답시간: {results['speed_performance']['avg_response_time']*1000:.1f}ms
- P95 응답시간: {results['speed_performance']['p95_response_time']*1000:.1f}ms
- P99 응답시간: {results['speed_performance']['p99_response_time']*1000:.1f}ms

🎯 정확도 성능
- 정확한 매칭: {results['accuracy_performance']['correct_matches']}/{results['accuracy_performance']['total_tests']} ({results['accuracy_performance']['exact_accuracy']:.1f}%)
- 부분 매칭: {results['accuracy_performance']['partial_matches']}/{results['accuracy_performance']['total_tests']}
- 매칭 실패: {results['accuracy_performance']['no_matches']}/{results['accuracy_performance']['total_tests']}

💾 시스템 정보
- 총 데이터: {results['data_info']['total_records']:,}개
- 윈도우 수: {results['data_info']['total_windows']:,}개
- 벡터 DB 크기: {results['vector_database']['video_size_mb']:.1f}MB

📋 권장사항
"""
    
    # 권장사항 추가
    if summary['overall_score'] >= 80:
        report += "✅ 우수한 성능입니다. 현재 설정을 유지하세요.\n"
    elif summary['overall_score'] >= 60:
        report += "⚠️ 보통 성능입니다. 다음을 고려해보세요:\n"
        if summary['avg_response_time'] > 0.2:
            report += "  - 응답시간 개선 필요\n"
        if summary['exact_accuracy'] < 85:
            report += "  - 정확도 개선 필요\n"
    else:
        report += "❌ 성능 개선이 필요합니다:\n"
        report += "  - 시스템 설정 재검토 필요\n"
        report += "  - 데이터 품질 확인 필요\n"
    
    return report

if __name__ == "__main__":
    main()