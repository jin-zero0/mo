"""
리트리버 성능 체크 모듈
속도 및 정확도 측정
"""
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import json
import os

from vector_converter import VectorConverter, VectorMatcher
from config import TEST_QUERIES, TOP_K, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceChecker:
    """리트리버 성능 체크 클래스"""
    
    def __init__(self, converter: VectorConverter):
        self.converter = converter
        self.matcher = VectorMatcher(converter)
        self.performance_results = {}
        
    def check_speed_performance(self, test_queries: List[str], runs: int = 3) -> Dict:
        """속도 성능 체크"""
        logger.info(f"속도 성능 체크 시작: {len(test_queries)}개 쿼리, {runs}회 반복")
        
        all_times = []
        query_results = []
        
        for run in range(runs):
            logger.info(f"Run {run + 1}/{runs}")
            run_times = []
            
            for i, query in enumerate(test_queries):
                start_time = time.perf_counter()
                results = self.converter.search_similar_vectors(query, top_k=TOP_K)
                end_time = time.perf_counter()
                
                query_time = end_time - start_time
                run_times.append(query_time)
                
                if run == 0:  # 첫 번째 실행에서만 결과 저장
                    query_results.append({
                        'query': query,
                        'results': results,
                        'time': query_time
                    })
                
                if (i + 1) % 10 == 0:
                    logger.info(f"  쿼리 {i + 1}/{len(test_queries)} 완료")
            
            all_times.append(run_times)
        
        # 통계 계산
        times_array = np.array(all_times)
        avg_times = np.mean(times_array, axis=0)
        
        speed_stats = {
            'total_queries': len(test_queries),
            'runs': runs,
            'avg_response_time': float(np.mean(avg_times)),
            'min_response_time': float(np.min(avg_times)),
            'max_response_time': float(np.max(avg_times)),
            'std_response_time': float(np.std(avg_times)),
            'median_response_time': float(np.median(avg_times)),
            'p95_response_time': float(np.percentile(avg_times, 95)),
            'p99_response_time': float(np.percentile(avg_times, 99)),
            'queries_per_second': len(test_queries) / np.sum(avg_times),
            'detailed_times': avg_times.tolist(),
            'query_results': query_results
        }
        
        logger.info(f"속도 성능 체크 완료!")
        logger.info(f"평균 응답 시간: {speed_stats['avg_response_time']:.3f}초")
        logger.info(f"초당 쿼리 처리: {speed_stats['queries_per_second']:.2f} QPS")
        
        return speed_stats
    
    def check_accuracy_performance(self, test_data: List[Dict], sample_size: int = None) -> Dict:
        """정확도 성능 체크"""
        logger.info("정확도 성능 체크 시작")
        
        if sample_size and sample_size < len(test_data):
            test_sample = np.random.choice(test_data, sample_size, replace=False).tolist()
        else:
            test_sample = test_data
        
        logger.info(f"테스트 샘플 크기: {len(test_sample)}")
        
        # 일대일 매칭 테스트 수행
        matching_results = self.matcher.perform_matching_test(test_sample)
        
        # 다양한 임계값에서의 정확도 계산
        accuracy_at_thresholds = self._calculate_accuracy_at_thresholds(matching_results)
        
        # 태그별 정확도 분석
        tag_accuracy = self._analyze_tag_accuracy(matching_results)
        
        accuracy_stats = {
            'total_tests': matching_results['total_tests'],
            'exact_accuracy': matching_results['accuracy'],
            'partial_accuracy': matching_results['partial_accuracy'],
            'avg_search_time': matching_results['avg_search_time'],
            'accuracy_at_thresholds': accuracy_at_thresholds,
            'tag_accuracy': tag_accuracy,
            'confusion_matrix': self._create_confusion_matrix(matching_results),
            'detailed_results': matching_results['detailed_results']
        }
        
        logger.info(f"정확도 성능 체크 완료!")
        logger.info(f"정확도: {accuracy_stats['exact_accuracy']:.2f}%")
        logger.info(f"부분 정확도: {accuracy_stats['partial_accuracy']:.2f}%")
        
        return accuracy_stats
    
    def _calculate_accuracy_at_thresholds(self, matching_results: Dict) -> Dict:
        """다양한 유사도 임계값에서의 정확도 계산"""
        thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
        accuracy_at_thresholds = {}
        
        for threshold in thresholds:
            correct_count = 0
            for result in matching_results['detailed_results']:
                if result['search_results'] and result['search_results'][0][1] >= threshold:
                    if result['match_result'] in ['correct', 'partial']:
                        correct_count += 1
            
            accuracy_at_thresholds[f"threshold_{threshold}"] = (
                correct_count / matching_results['total_tests'] * 100
            )
        
        return accuracy_at_thresholds
    
    def _analyze_tag_accuracy(self, matching_results: Dict) -> Dict:
        """태그별 정확도 분석"""
        tag_stats = {}
        
        for result in matching_results['detailed_results']:
            tag = result['test_item']['tag']
            if tag not in tag_stats:
                tag_stats[tag] = {'total': 0, 'correct': 0, 'partial': 0}
            
            tag_stats[tag]['total'] += 1
            if result['match_result'] == 'correct':
                tag_stats[tag]['correct'] += 1
            elif result['match_result'] == 'partial':
                tag_stats[tag]['partial'] += 1
        
        # 정확도 계산
        for tag in tag_stats:
            stats = tag_stats[tag]
            stats['exact_accuracy'] = stats['correct'] / stats['total'] * 100
            stats['partial_accuracy'] = (stats['correct'] + stats['partial']) / stats['total'] * 100
        
        return tag_stats
    
    def _create_confusion_matrix(self, matching_results: Dict) -> Dict:
        """혼동 행렬 생성"""
        matrix = {
            'correct': {'predicted_correct': 0, 'predicted_partial': 0, 'predicted_no_match': 0},
            'partial': {'predicted_correct': 0, 'predicted_partial': 0, 'predicted_no_match': 0},
            'no_match': {'predicted_correct': 0, 'predicted_partial': 0, 'predicted_no_match': 0}
        }
        
        for result in matching_results['detailed_results']:
            actual = result['match_result']
            if actual == 'correct':
                actual_key = 'correct'
            elif actual == 'partial':
                actual_key = 'partial'
            else:
                actual_key = 'no_match'
            
            # 예측 결과는 유사도 점수로 판단
            if result['search_results']:
                score = result['search_results'][0][1]
                if score > 0.8:
                    predicted_key = 'predicted_correct'
                elif score > 0.6:
                    predicted_key = 'predicted_partial'
                else:
                    predicted_key = 'predicted_no_match'
            else:
                predicted_key = 'predicted_no_match'
            
            matrix[actual_key][predicted_key] += 1
        
        return matrix
    
    def run_comprehensive_performance_check(
        self, 
        test_data: List[Dict], 
        test_queries: List[str] = None,
        speed_runs: int = 3,
        accuracy_sample_size: int = None
    ) -> Dict:
        """종합 성능 체크 실행"""
        logger.info("=== 종합 성능 체크 시작 ===")
        
        start_time = time.time()
        
        # 테스트 쿼리 생성 (제공되지 않은 경우)
        if test_queries is None:
            test_queries = self._generate_test_queries(test_data)
        
        # 1. 속도 성능 체크
        speed_results = self.check_speed_performance(test_queries, runs=speed_runs)
        
        # 2. 정확도 성능 체크
        accuracy_results = self.check_accuracy_performance(test_data, sample_size=accuracy_sample_size)
        
        # 3. 시스템 정보 수집
        system_info = self._collect_system_info()
        
        total_time = time.time() - start_time
        
        comprehensive_results = {
            'timestamp': datetime.now().isoformat(),
            'total_check_time': total_time,
            'speed_performance': speed_results,
            'accuracy_performance': accuracy_results,
            'system_info': system_info,
            'summary': {
                'avg_response_time': speed_results['avg_response_time'],
                'queries_per_second': speed_results['queries_per_second'],
                'exact_accuracy': accuracy_results['exact_accuracy'],
                'partial_accuracy': accuracy_results['partial_accuracy'],
                'overall_score': self._calculate_overall_score(speed_results, accuracy_results)
            }
        }
        
        # 결과 저장
        self.performance_results = comprehensive_results
        self._save_results(comprehensive_results)
        
        logger.info("=== 종합 성능 체크 완료 ===")
        logger.info(f"전체 소요 시간: {total_time:.2f}초")
        logger.info(f"종합 점수: {comprehensive_results['summary']['overall_score']:.2f}/100")
        
        return comprehensive_results
    
    def _generate_test_queries(self, test_data: List[Dict], num_queries: int = None) -> List[str]:
        """테스트 쿼리 생성"""
        if num_queries is None:
            num_queries = min(TEST_QUERIES, len(test_data))
        
        queries = []
        sampled_data = np.random.choice(test_data, num_queries, replace=False)
        
        query_templates = [
            "윈도우 {window_id} 진동 데이터",
            "온도 {temp:.1f}도 압력 {pressure:.1f} 설비 상태",
            "진동 X축 {vib_x:.2f} Y축 {vib_y:.2f} Z축 {vib_z:.2f}",
            "{tag} 데이터 분석",
            "시간 구간 {start_time} 설비 진동"
        ]
        
        for data in sampled_data:
            template = np.random.choice(query_templates)
            query = template.format(
                window_id=data['window_id'],
                temp=data['temperature_mean'],
                pressure=data['pressure_mean'],
                vib_x=data['vibration_x_mean'],
                vib_y=data['vibration_y_mean'],
                vib_z=data['vibration_z_mean'],
                tag=data['tag'],
                start_time=str(data['start_time']).split('.')[0]
            )
            queries.append(query)
        
        return queries
    
    def _collect_system_info(self) -> Dict:
        """시스템 정보 수집"""
        db_info = self.converter.get_vector_database_info()
        
        return {
            'vector_database': db_info,
            'embedding_model': 'text-embedding-3-small',
            'memvid_version': '0.1.3',
            'test_parameters': {
                'top_k': TOP_K,
                'test_queries': TEST_QUERIES
            }
        }
    
    def _calculate_overall_score(self, speed_results: Dict, accuracy_results: Dict) -> float:
        """종합 점수 계산"""
        # 속도 점수 (응답시간 기반, 1초 이하면 만점)
        speed_score = min(100, (1.0 / speed_results['avg_response_time']) * 10)
        
        # 정확도 점수
        accuracy_score = accuracy_results['exact_accuracy']
        
        # 가중 평균 (정확도 70%, 속도 30%)
        overall_score = accuracy_score * 0.7 + speed_score * 0.3
        
        return min(100, overall_score)
    
    def _save_results(self, results: Dict):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_results_{timestamp}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"성능 체크 결과 저장: {filepath}")
    
    def get_performance_summary(self) -> Dict:
        """성능 요약 반환"""
        if not self.performance_results:
            return {}
        
        summary = self.performance_results.get('summary', {})
        return {
            'timestamp': self.performance_results.get('timestamp'),
            'avg_response_time_ms': summary.get('avg_response_time', 0) * 1000,
            'queries_per_second': summary.get('queries_per_second', 0),
            'exact_accuracy_percent': summary.get('exact_accuracy', 0),
            'partial_accuracy_percent': summary.get('partial_accuracy', 0),
            'overall_score': summary.get('overall_score', 0),
            'performance_grade': self._get_performance_grade(summary.get('overall_score', 0))
        }
    
    def _get_performance_grade(self, score: float) -> str:
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

if __name__ == "__main__":
    # 테스트 실행
    from data_preprocessor import LogicDataPreprocessor
    from vector_converter import VectorConverter
    
    # 데이터 전처리
    preprocessor = LogicDataPreprocessor()
    processed_df, windowed_data = preprocessor.process_data(size=1000)
    
    # 벡터 변환
    converter = VectorConverter()
    chunks = converter.prepare_data_for_vectorization(windowed_data)
    video_path, index_path = converter.create_vector_database(chunks, "performance_test")
    converter.load_vector_database(video_path, index_path)
    
    # 성능 체크
    checker = PerformanceChecker(converter)
    results = checker.run_comprehensive_performance_check(
        test_data=windowed_data,
        speed_runs=2,
        accuracy_sample_size=50
    )
    
    print("\n=== 성능 체크 결과 요약 ===")
    summary = checker.get_performance_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")