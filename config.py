"""
리트리버 성능 체크 시스템 설정
"""
import os

# OpenAI API 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
EMBEDDING_MODEL = "text-embedding-3-small"

# 데이터 처리 설정
DATA_SIZE = 10000  # 1만개 데이터
WINDOW_SIZE = 5  # 5분 윈도우
CHUNK_SIZE = 512  # 청크 크기
OVERLAP = 50  # 오버랩

# MemVid 설정
VIDEO_FPS = 30
FRAME_SIZE = 512
VIDEO_CODEC = 'h264'
CRF = 23

# 성능 측정 설정
TEST_QUERIES = 100  # 테스트 쿼리 수
TOP_K = 5  # 상위 K개 결과

# 파일 경로
DATA_DIR = "data"
OUTPUT_DIR = "output"
VIDEO_DIR = "videos"
INDEX_DIR = "indexes"

# 디렉토리 생성
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)