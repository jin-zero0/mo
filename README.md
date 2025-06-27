# 리트리버 성능 체크 시스템

MemVid를 활용한 벡터 데이터베이스 리트리버의 성능을 측정하고 분석하는 종합 시스템입니다.

## 🎯 주요 기능

### 1. 데이터 전처리
- 1만개 로직 데이터 처리 (시간 + 설비 데이터)
- Null값 자동 처리 (시간: 선형 보간, 설비: 평균값 대체)
- 5분 단위 윈도우 슬라이딩 기법 적용
- 태그 시스템을 통한 데이터 추적

### 2. 벡터 데이터베이스 구축
- MemVid를 사용한 MP4 기반 벡터 저장
- OpenAI text-embedding-3-small 모델 활용
- 메타데이터 태깅 및 인덱싱
- 압축 효율적인 비디오 포맷 지원

### 3. 성능 측정
- **속도 체크**: 응답시간, 처리량(QPS), 백분위수 통계
- **정확도 체크**: 일대일 매칭 테스트, 유사도 임계값 분석
- 태그별 정확도 분석
- 혼동 행렬 및 상세 메트릭

### 4. 대시보드
- 실시간 성능 모니터링
- 시각화된 차트 및 그래프
- 종합 점수 및 등급 시스템
- 결과 다운로드 기능

## 🛠️ 설치 및 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd mo
```

### 2. 가상환경 설정
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## 🚀 사용법

### 전체 시스템 실행
```bash
python main.py --mode all --data-size 10000 --window-size 5 --api-key YOUR_API_KEY
```

### 단계별 실행

#### 1. 데이터 전처리만
```bash
python main.py --mode preprocess --data-size 10000 --window-size 5
```

#### 2. 벡터 변환만
```bash
python main.py --mode convert --api-key YOUR_API_KEY
```

#### 3. 성능 테스트만
```bash
python main.py --mode test
```

#### 4. 대시보드만
```bash
python main.py --mode dashboard
```

### 대시보드 직접 실행
```bash
streamlit run dashboard.py
```

## 📊 성능 지표

### 속도 성능
- **평균 응답시간**: 검색 쿼리당 평균 처리 시간 (ms)
- **처리량 (QPS)**: 초당 처리 가능한 쿼리 수
- **백분위수**: P95, P99 응답시간
- **응답시간 분포**: 히스토그램 시각화

### 정확도 성능
- **정확한 매칭률**: 완전히 일치하는 결과 비율 (%)
- **부분 매칭률**: 유사도 임계값 이상의 결과 비율 (%)
- **태그별 정확도**: 각 윈도우 태그별 성능 분석
- **혼동 행렬**: 예측 vs 실제 결과 매트릭스

### 종합 점수
- **가중 평균**: 정확도 70% + 속도 30%
- **성능 등급**: A+ (90+) ~ D (50미만)
- **개선 권장사항**: 자동 생성

## 📁 프로젝트 구조

```
mo/
├── config.py                 # 시스템 설정
├── data_preprocessor.py      # 데이터 전처리 모듈
├── vector_converter.py       # 벡터 변환 모듈
├── performance_checker.py    # 성능 측정 모듈
├── dashboard.py             # Streamlit 대시보드
├── main.py                  # 메인 실행 스크립트
├── requirements.txt         # 의존성 목록
├── README.md               # 프로젝트 문서
├── data/                   # 전처리된 데이터
├── videos/                 # MemVid MP4 파일
├── indexes/                # 벡터 인덱스 파일
└── output/                 # 성능 테스트 결과
```

## 🔧 상세 설정

### config.py 주요 설정값
- `DATA_SIZE`: 처리할 데이터 크기 (기본: 10,000)
- `WINDOW_SIZE`: 윈도우 크기 분 단위 (기본: 5)
- `EMBEDDING_MODEL`: OpenAI 임베딩 모델 (text-embedding-3-small)
- `VIDEO_FPS`: MemVid 비디오 FPS (기본: 30)
- `TEST_QUERIES`: 테스트 쿼리 수 (기본: 100)

### 성능 최적화 팁
1. **데이터 크기 조정**: 테스트 환경에서는 1,000개부터 시작
2. **윈도우 크기**: 데이터 특성에 맞게 1-15분 범위에서 조정
3. **배치 크기**: OpenAI API 제한에 맞춰 배치 처리
4. **메모리 관리**: 대용량 데이터 처리 시 청크 단위로 분할

## 📈 결과 해석

### 성능 등급 기준
- **A+ (90-100점)**: 최우수 - 상용 서비스 수준
- **A (80-89점)**: 우수 - 실무 적용 가능
- **B+ (70-79점)**: 양호 - 개선 여지 있음
- **B (60-69점)**: 보통 - 튜닝 필요
- **C (50-59점)**: 개선필요 - 설정 재검토
- **D (50점 미만)**: 불량 - 시스템 점검 필요

### 임계값 가이드
- **응답시간**: 200ms 이하 권장, 500ms 이상 시 개선 필요
- **정확도**: 85% 이상 권장, 70% 이하 시 데이터 품질 검토
- **처리량**: 5 QPS 이상 권장

## 🔬 기술 스택

- **벡터 DB**: MemVid (MP4 기반)
- **임베딩**: OpenAI text-embedding-3-small
- **데이터 처리**: Pandas, NumPy
- **시각화**: Streamlit, Plotly
- **성능 측정**: 커스텀 메트릭 엔진

## 🐛 문제 해결

### 일반적인 오류

#### 1. API 키 오류
```
Error: OpenAI API key not found
```
**해결책**: 환경변수 또는 매개변수로 API 키 설정

#### 2. 메모리 오류
```
MemoryError: Unable to allocate array
```
**해결책**: 데이터 크기 줄이거나 배치 크기 조정

#### 3. 패키지 설치 오류
```
ImportError: No module named 'memvid'
```
**해결책**: 가상환경에서 requirements.txt 재설치

### 성능 최적화

#### 느린 응답시간
- 데이터 크기 줄이기
- 윈도우 크기 최적화
- SSD 사용 권장

#### 낮은 정확도
- 윈도우 크기 조정
- 임계값 튜닝
- 데이터 품질 검토

## 📋 향후 개발 계획

- [ ] 실시간 스트리밍 데이터 지원
- [ ] 다중 모델 비교 기능
- [ ] 자동 하이퍼파라미터 튜닝
- [ ] Docker 컨테이너 지원
- [ ] REST API 인터페이스
- [ ] 클러스터 환경 확장

## 📞 지원

이슈나 질문이 있으시면 GitHub Issues를 통해 문의해주세요.

## 📜 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**리트리버 성능 체크 시스템으로 최적의 벡터 검색 성능을 확인하세요! 🚀** 