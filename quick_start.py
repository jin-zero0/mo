#!/usr/bin/env python3
"""
리트리버 성능 체크 시스템 - 빠른 시작
"""

def main():
    print("🎯 리트리버 성능 체크 시스템")
    print("=" * 50)
    
    print("\n📋 시스템 개요:")
    print("이 시스템은 MemVid를 활용한 벡터 데이터베이스 리트리버의 성능을 측정합니다.")
    
    print("\n🔧 구성 요소:")
    print("1. 데이터 전처리 (data_preprocessor.py)")
    print("   - 1만개 로직 데이터 처리 (시간 + 설비)")
    print("   - Null값 자동 처리")
    print("   - 5분 윈도우 슬라이딩")
    
    print("\n2. 벡터 변환 (vector_converter.py)")
    print("   - MemVid MP4 기반 벡터 저장")
    print("   - OpenAI text-embedding-3-small")
    print("   - 메타데이터 태깅")
    
    print("\n3. 성능 측정 (performance_checker.py)")
    print("   - 속도 체크: 응답시간, QPS, 백분위수")
    print("   - 정확도 체크: 일대일 매칭, 유사도 분석")
    print("   - 종합 점수 및 등급")
    
    print("\n4. 대시보드 (dashboard.py)")
    print("   - Streamlit 웹 인터페이스")
    print("   - 실시간 성능 모니터링")
    print("   - 시각화 차트")
    
    print("\n🚀 실행 방법:")
    print("1. 데모 실행:      python3 demo.py")
    print("2. 전체 실행:      python3 main.py --mode all --api-key YOUR_KEY")
    print("3. 대시보드:       streamlit run dashboard.py")
    
    print("\n📊 성능 지표:")
    print("- 속도: 평균 응답시간 (ms), 초당 처리량 (QPS)")
    print("- 정확도: 정확한 매칭률 (%), 부분 매칭률 (%)")
    print("- 종합: A+ (90+) ~ D (50미만) 등급")
    
    print("\n💡 주요 특징:")
    print("✅ 5분 윈도우 슬라이딩으로 시계열 데이터 처리")
    print("✅ MemVid MP4 기반 압축 효율적 벡터 저장")
    print("✅ 일대일 매칭으로 정확도 검증")
    print("✅ 태그 시스템으로 데이터 추적")
    print("✅ 실시간 대시보드 모니터링")
    
    print("\n📞 도움말:")
    print("- README.md: 상세 사용법")
    print("- demo.py: 시스템 시연")
    print("- config.py: 설정 조정")
    
    print("\n🎉 시작해보세요!")
    print("python3 demo.py")

if __name__ == "__main__":
    main()