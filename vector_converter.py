"""
MemVid를 사용한 벡터 데이터베이스 변환기
OpenAI text-embedding-3-small 모델 사용
"""
import os
import json
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from memvid import MemvidEncoder, MemvidRetriever
import openai
from tqdm import tqdm
import logging

from config import OPENAI_API_KEY, EMBEDDING_MODEL, VIDEO_DIR, INDEX_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorConverter:
    """MemVid 벡터 변환기 클래스"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
        
        self.encoder = None
        self.retriever = None
        self.video_path = None
        self.index_path = None
        
    def prepare_data_for_vectorization(self, windowed_data: List[Dict]) -> List[Dict]:
        """윈도우 데이터를 벡터화를 위한 텍스트 청크로 변환"""
        logger.info("벡터화를 위한 데이터 준비 중...")
        
        chunks = []
        for window in windowed_data:
            # 윈도우 데이터를 텍스트로 변환
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

포함된 인덱스: {', '.join(map(str, window['index_ids'][:10]))}{'...' if len(window['index_ids']) > 10 else ''}
            """.strip()
            
            chunk_data = {
                'content': text_content,
                'metadata': {
                    'window_id': window['window_id'],
                    'tag': window['tag'],
                    'start_time': str(window['start_time']),
                    'end_time': str(window['end_time']),
                    'data_count': window['data_count'],
                    'vibration_signature': f"{window['vibration_x_mean']:.3f}_{window['vibration_y_mean']:.3f}_{window['vibration_z_mean']:.3f}",
                    'temperature_avg': window['temperature_mean'],
                    'pressure_avg': window['pressure_mean']
                }
            }
            chunks.append(chunk_data)
        
        logger.info(f"벡터화를 위한 {len(chunks)}개 청크 준비 완료")
        return chunks
    
    def create_vector_database(self, chunks: List[Dict], video_name: str = "vibration_data") -> Tuple[str, str]:
        """MemVid를 사용하여 벡터 데이터베이스 생성"""
        logger.info(f"MemVid 벡터 데이터베이스 생성 중: {video_name}")
        
        # MemVid 인코더 초기화
        self.encoder = MemvidEncoder(
            chunk_size=512,
            overlap=50
        )
        
        # 텍스트 청크들을 MemVid에 추가
        for chunk in tqdm(chunks, desc="청크 추가"):
            self.encoder.add_text(
                chunk['content'],
                metadata=chunk['metadata']
            )
        
        # 비디오 파일 경로 설정
        self.video_path = os.path.join(VIDEO_DIR, f"{video_name}.mp4")
        self.index_path = os.path.join(INDEX_DIR, f"{video_name}_index.json")
        
        # 비디오 생성
        logger.info("MP4 파일 생성 중...")
        start_time = time.time()
        
        self.encoder.build_video(
            self.video_path,
            self.index_path,
            fps=30,
            frame_size=512
        )
        
        build_time = time.time() - start_time
        logger.info(f"벡터 데이터베이스 생성 완료! 소요시간: {build_time:.2f}초")
        logger.info(f"비디오 파일: {self.video_path}")
        logger.info(f"인덱스 파일: {self.index_path}")
        
        return self.video_path, self.index_path
    
    def load_vector_database(self, video_path: str, index_path: str):
        """기존 벡터 데이터베이스 로드"""
        logger.info(f"벡터 데이터베이스 로드: {video_path}")
        
        self.video_path = video_path
        self.index_path = index_path
        self.retriever = MemvidRetriever(video_path, index_path)
        
        logger.info("벡터 데이터베이스 로드 완료")
    
    def search_similar_vectors(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """유사도 검색 수행"""
        if self.retriever is None:
            raise ValueError("벡터 데이터베이스가 로드되지 않았습니다.")
        
        logger.info(f"유사도 검색 수행: '{query[:50]}...'")
        start_time = time.time()
        
        results = self.retriever.search(query, top_k=top_k)
        
        search_time = time.time() - start_time
        logger.info(f"검색 완료! 소요시간: {search_time:.3f}초")
        
        # 결과 포맷팅
        formatted_results = []
        for i, (content, score) in enumerate(results):
            # 메타데이터 추출 (실제 구현에 따라 조정 필요)
            metadata = {}
            try:
                if hasattr(self.retriever, 'get_metadata'):
                    metadata = self.retriever.get_metadata(i)
            except:
                pass
            
            formatted_results.append((content, score, metadata))
        
        return formatted_results
    
    def get_vector_database_info(self) -> Dict:
        """벡터 데이터베이스 정보 반환"""
        if not self.video_path or not self.index_path:
            return {}
        
        info = {
            'video_path': self.video_path,
            'index_path': self.index_path,
            'video_exists': os.path.exists(self.video_path),
            'index_exists': os.path.exists(self.index_path)
        }
        
        if info['video_exists']:
            info['video_size_mb'] = os.path.getsize(self.video_path) / (1024 * 1024)
        
        if info['index_exists']:
            info['index_size_mb'] = os.path.getsize(self.index_path) / (1024 * 1024)
            
            # 인덱스 파일에서 추가 정보 읽기
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    info['total_chunks'] = len(index_data.get('embeddings', []))
                    info['embedding_dimension'] = len(index_data.get('embeddings', [{}])[0]) if index_data.get('embeddings') else 0
            except:
                pass
        
        return info

class VectorMatcher:
    """벡터 일대일 매칭 시스템"""
    
    def __init__(self, converter: VectorConverter):
        self.converter = converter
        
    def perform_matching_test(self, test_data: List[Dict], top_k: int = 1) -> Dict:
        """일대일 매칭 테스트 수행"""
        logger.info(f"{len(test_data)}개 항목에 대한 매칭 테스트 시작")
        
        results = {
            'total_tests': len(test_data),
            'correct_matches': 0,
            'partial_matches': 0,
            'no_matches': 0,
            'avg_search_time': 0,
            'detailed_results': []
        }
        
        total_search_time = 0
        
        for test_item in tqdm(test_data, desc="매칭 테스트"):
            # 원본 데이터에서 쿼리 생성
            query = f"윈도우 {test_item['window_id']} 진동 데이터 온도 {test_item['temperature_mean']:.1f} 압력 {test_item['pressure_mean']:.1f}"
            
            start_time = time.time()
            search_results = self.converter.search_similar_vectors(query, top_k=top_k)
            search_time = time.time() - start_time
            total_search_time += search_time
            
            # 매칭 결과 분석
            match_result = self._analyze_match(test_item, search_results)
            results['detailed_results'].append({
                'test_item': test_item,
                'query': query,
                'search_results': search_results,
                'match_result': match_result,
                'search_time': search_time
            })
            
            # 결과 카운팅
            if match_result == 'correct':
                results['correct_matches'] += 1
            elif match_result == 'partial':
                results['partial_matches'] += 1
            else:
                results['no_matches'] += 1
        
        results['avg_search_time'] = total_search_time / len(test_data)
        results['accuracy'] = results['correct_matches'] / results['total_tests'] * 100
        results['partial_accuracy'] = (results['correct_matches'] + results['partial_matches']) / results['total_tests'] * 100
        
        logger.info(f"매칭 테스트 완료!")
        logger.info(f"정확도: {results['accuracy']:.2f}%")
        logger.info(f"부분 정확도: {results['partial_accuracy']:.2f}%")
        logger.info(f"평균 검색 시간: {results['avg_search_time']:.3f}초")
        
        return results
    
    def _analyze_match(self, test_item: Dict, search_results: List[Tuple]) -> str:
        """매칭 결과 분석"""
        if not search_results:
            return 'no_match'
        
        best_result = search_results[0]
        content, score, metadata = best_result
        
        # 윈도우 ID로 정확한 매칭 확인
        if f"윈도우 ID: {test_item['window_id']}" in content:
            return 'correct'
        
        # 유사도 점수로 부분 매칭 확인
        if score > 0.7:  # 임계값 조정 가능
            return 'partial'
        
        return 'no_match'

def create_openai_embeddings(texts: List[str], model: str = EMBEDDING_MODEL) -> List[List[float]]:
    """OpenAI API를 사용하여 임베딩 생성"""
    logger.info(f"OpenAI {model} 모델로 임베딩 생성 중...")
    
    embeddings = []
    batch_size = 100  # API 제한에 맞춰 배치 처리
    
    for i in tqdm(range(0, len(texts), batch_size), desc="임베딩 생성"):
        batch_texts = texts[i:i+batch_size]
        
        try:
            response = openai.embeddings.create(
                model=model,
                input=batch_texts
            )
            
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
            
        except Exception as e:
            logger.error(f"임베딩 생성 중 오류: {e}")
            # 오류 발생 시 더미 임베딩으로 대체
            dummy_embedding = [0.0] * 1536  # text-embedding-3-small 차원
            embeddings.extend([dummy_embedding] * len(batch_texts))
    
    logger.info(f"임베딩 생성 완료: {len(embeddings)}개")
    return embeddings

if __name__ == "__main__":
    # 테스트 실행
    from data_preprocessor import LogicDataPreprocessor
    
    # 데이터 전처리
    preprocessor = LogicDataPreprocessor()
    processed_df, windowed_data = preprocessor.process_data(size=1000)  # 테스트용으로 작게
    
    # 벡터 변환
    converter = VectorConverter()
    chunks = converter.prepare_data_for_vectorization(windowed_data)
    video_path, index_path = converter.create_vector_database(chunks, "test_vibration")
    
    # 매칭 테스트
    converter.load_vector_database(video_path, index_path)
    matcher = VectorMatcher(converter)
    
    # 일부 데이터로 매칭 테스트
    test_results = matcher.perform_matching_test(windowed_data[:10])
    
    print("\n=== 벡터 변환 및 매칭 테스트 결과 ===")
    print(f"정확도: {test_results['accuracy']:.2f}%")
    print(f"평균 검색 시간: {test_results['avg_search_time']:.3f}초")