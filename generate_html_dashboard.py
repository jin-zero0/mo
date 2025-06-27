#!/usr/bin/env python3
"""
HTML 대시보드 생성기
실제 데이터를 사용해서 정적 HTML 대시보드를 생성
"""

import json
import os
from datetime import datetime

def load_latest_results():
    """최신 결과 파일 로드"""
    output_dir = "output"
    if not os.path.exists(output_dir):
        return None
    
    # JSON 파일들 찾기
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    if not json_files:
        return None
    
    # 가장 최신 파일 선택
    latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
    
    with open(os.path.join(output_dir, latest_file), 'r', encoding='utf-8') as f:
        return json.load(f)

def get_grade_color(score):
    """점수에 따른 색상 반환"""
    if score >= 90:
        return "#2e8b57"  # 초록색 (A+)
    elif score >= 80:
        return "#4169e1"  # 파란색 (A)
    elif score >= 70:
        return "#ffa500"  # 주황색 (B+)
    elif score >= 60:
        return "#ff8c00"  # 진한 주황색 (B)
    elif score >= 50:
        return "#dc143c"  # 빨간색 (C)
    else:
        return "#8b0000"  # 진한 빨간색 (D)

def generate_html_dashboard(results):
    """HTML 대시보드 생성"""
    
    # 결과 데이터 추출
    summary = results['summary']
    speed = results['speed']
    accuracy = results['accuracy']
    data_info = results['data_info']
    vector_db = results['vector_database']
    
    # 응답시간 데이터 준비 (Chart.js용)
    response_times = speed['response_times']
    response_times_ms = [t * 1000 for t in response_times]  # ms 변환
    
    # 히스토그램 데이터 생성
    bins = [0, 50, 100, 150, 200, 250, 300, 350]
    hist_data = [0] * (len(bins) - 1)
    for time_ms in response_times_ms:
        for i in range(len(bins) - 1):
            if bins[i] <= time_ms < bins[i + 1]:
                hist_data[i] += 1
                break
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 리트리버 성능 체크 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        
        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(145deg, #f8f9ff, #e8eeff);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-left: 5px solid;
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        
        .metric-sublabel {{
            color: #888;
            font-size: 0.9em;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .details-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .details-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        
        .detail-item {{
            margin-bottom: 15px;
        }}
        
        .detail-label {{
            font-weight: bold;
            color: #333;
        }}
        
        .detail-value {{
            color: #666;
            margin-left: 10px;
        }}
        
        .grade-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 10px;
            transition: width 0.8s ease;
        }}
        
        .download-section {{
            text-align: center;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 15px;
            margin-top: 20px;
        }}
        
        .download-btn {{
            display: inline-block;
            padding: 12px 24px;
            margin: 10px;
            background: linear-gradient(145deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: transform 0.3s ease;
        }}
        
        .download-btn:hover {{
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .details-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 리트리버 성능 체크 대시보드</h1>
            <div class="timestamp">📅 테스트 일시: {datetime.fromisoformat(results['timestamp']).strftime('%Y년 %m월 %d일 %H:%M:%S')}</div>
        </div>
        
        <!-- 핵심 지표 카드 -->
        <div class="metrics-grid">
            <div class="metric-card" style="border-left-color: {get_grade_color(summary['overall_score'])}">
                <div class="metric-label">🏆 종합 점수</div>
                <div class="metric-value" style="color: {get_grade_color(summary['overall_score'])}">{summary['overall_score']:.1f}/100</div>
                <span class="grade-badge" style="background-color: {get_grade_color(summary['overall_score'])}">{summary['grade']}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {summary['overall_score']}%"></div>
                </div>
            </div>
            
            <div class="metric-card" style="border-left-color: {get_grade_color(summary['accuracy_score'])}">
                <div class="metric-label">🎯 정확도</div>
                <div class="metric-value" style="color: {get_grade_color(summary['accuracy_score'])}">{summary['accuracy_score']:.1f}%</div>
                <div class="metric-sublabel">정확한 매칭률</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {summary['accuracy_score']}%"></div>
                </div>
            </div>
            
            <div class="metric-card" style="border-left-color: {'#2e8b57' if speed['avg_response_time'] * 1000 < 200 else '#ffa500' if speed['avg_response_time'] * 1000 < 500 else '#dc143c'}">
                <div class="metric-label">⚡ 응답 시간</div>
                <div class="metric-value" style="color: {'#2e8b57' if speed['avg_response_time'] * 1000 < 200 else '#ffa500' if speed['avg_response_time'] * 1000 < 500 else '#dc143c'}">{speed['avg_response_time'] * 1000:.0f}ms</div>
                <div class="metric-sublabel">평균 검색 시간</div>
            </div>
            
            <div class="metric-card" style="border-left-color: {'#2e8b57' if speed['queries_per_second'] > 5 else '#ffa500' if speed['queries_per_second'] > 2 else '#dc143c'}">
                <div class="metric-label">📊 처리량</div>
                <div class="metric-value" style="color: {'#2e8b57' if speed['queries_per_second'] > 5 else '#ffa500' if speed['queries_per_second'] > 2 else '#dc143c'}">{speed['queries_per_second']:.1f} QPS</div>
                <div class="metric-sublabel">초당 쿼리 수</div>
            </div>
        </div>
        
        <!-- 차트 섹션 -->
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">⚡ 응답 시간 분포</div>
                <canvas id="responseTimeChart" width="400" height="300"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">🎯 매칭 결과 분포</div>
                <canvas id="accuracyChart" width="400" height="300"></canvas>
            </div>
        </div>
        
        <!-- 상세 정보 -->
        <div class="details-section">
            <div class="chart-title">📈 상세 분석</div>
            <div class="details-grid">
                <div>
                    <h3 style="color: #667eea; margin-bottom: 20px;">💾 시스템 정보</h3>
                    <div class="detail-item">
                        <span class="detail-label">총 레코드 수:</span>
                        <span class="detail-value">{data_info['total_records']:,}개</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">윈도우 수:</span>
                        <span class="detail-value">{data_info['total_windows']:,}개</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">윈도우 크기:</span>
                        <span class="detail-value">{data_info['window_size']}분</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">벡터 청크 수:</span>
                        <span class="detail-value">{vector_db['total_chunks']:,}개</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">비디오 파일:</span>
                        <span class="detail-value">{vector_db['video_path']}</span>
                    </div>
                </div>
                
                <div>
                    <h3 style="color: #667eea; margin-bottom: 20px;">📊 성능 통계</h3>
                    <div class="detail-item">
                        <span class="detail-label">최소 응답시간:</span>
                        <span class="detail-value">{speed['min_response_time'] * 1000:.1f}ms</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">최대 응답시간:</span>
                        <span class="detail-value">{speed['max_response_time'] * 1000:.1f}ms</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">P95 응답시간:</span>
                        <span class="detail-value">{speed.get('p95_response_time', speed['max_response_time']) * 1000:.1f}ms</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">정확한 매칭:</span>
                        <span class="detail-value">{accuracy['correct_matches']}/{accuracy['total_tests']} ({accuracy['exact_accuracy']:.1f}%)</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">부분 매칭:</span>
                        <span class="detail-value">{accuracy['partial_matches']}/{accuracy['total_tests']}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 다운로드 섹션 -->
        <div class="download-section">
            <h3 style="color: #667eea; margin-bottom: 20px;">💾 결과 다운로드</h3>
            <p>테스트 결과는 output 폴더에 저장되어 있습니다:</p>
            <a href="#" class="download-btn" onclick="alert('output/demo_results_*.json 파일을 확인하세요!')">📄 JSON 결과</a>
            <a href="#" class="download-btn" onclick="alert('output/demo_report_*.txt 파일을 확인하세요!')">📑 텍스트 리포트</a>
        </div>
    </div>

    <script>
        // 응답 시간 히스토그램
        const ctx1 = document.getElementById('responseTimeChart').getContext('2d');
        new Chart(ctx1, {{
            type: 'bar',
            data: {{
                labels: ['0-50ms', '50-100ms', '100-150ms', '150-200ms', '200-250ms', '250-300ms', '300-350ms'],
                datasets: [{{
                    label: '쿼리 수',
                    data: {hist_data},
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }});

        // 정확도 도넛 차트
        const ctx2 = document.getElementById('accuracyChart').getContext('2d');
        new Chart(ctx2, {{
            type: 'doughnut',
            data: {{
                labels: ['정확한 매칭', '부분 매칭', '매칭 실패'],
                datasets: [{{
                    data: [{accuracy['correct_matches']}, {accuracy['partial_matches']}, {accuracy['no_matches']}],
                    backgroundColor: [
                        '#2e8b57',
                        '#ffa500', 
                        '#dc143c'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});

        // 페이지 로드 애니메이션
        window.addEventListener('load', function() {{
            const cards = document.querySelectorAll('.metric-card');
            cards.forEach((card, index) => {{
                setTimeout(() => {{
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.style.transition = 'all 0.6s ease';
                    setTimeout(() => {{
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }}, 100);
                }}, index * 200);
            }});
        }});
    </script>
</body>
</html>
"""
    
    return html_content

def main():
    """메인 실행 함수"""
    print("🌐 HTML 대시보드 생성 중...")
    
    # 최신 결과 로드
    results = load_latest_results()
    if not results:
        print("❌ 결과 파일을 찾을 수 없습니다. 먼저 demo.py를 실행하세요.")
        return
    
    # HTML 대시보드 생성
    html_content = generate_html_dashboard(results)
    
    # 파일 저장
    html_filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML 대시보드 생성 완료: {html_filename}")
    print(f"🌐 브라우저에서 열어보세요: file://{os.path.abspath(html_filename)}")
    print("\n📊 대시보드 내용:")
    print(f"  - 종합 점수: {results['summary']['overall_score']:.1f}/100")
    print(f"  - 정확도: {results['summary']['accuracy_score']:.1f}%")
    print(f"  - 응답시간: {results['speed']['avg_response_time'] * 1000:.1f}ms")
    print(f"  - 처리량: {results['speed']['queries_per_second']:.1f} QPS")

if __name__ == "__main__":
    main()