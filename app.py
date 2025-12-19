import streamlit as st
import time
import random

# --- 1. 설정 및 데이터 ---
st.set_page_config(page_title="A반 이름 맞추기", layout="centered")

# 승현님이 주신 이미지 기준 38명 명단 (가나다순 정렬 확인됨)
ALL_NAMES = [
    "길소연", "김경태", "김미경", "김성균", "김영민", "김원구", "김윤희", "김효경", "류요한", "박병현",
    "박성수", "박진우", "배윤영", "신성원", "신승현", "안남호", "안상환", "여수빈", "오승욱", "우다은",
    "유원종", "이다경", "이상곤", "이상목", "이상윤", "이성엽", "이연주", "이윤형", "이종훈", "임상효",
    "장성준", "전명균", "정석현", "정찬수", "진혁진", "최부권", "황민경", "황인재"
]

# 초성 추출 함수
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def get_chosung(text):
    result = ""
    for char in text:
        if '가' <= char <= '힣':
            code = ord(char) - 44032
            cho = code // 588
            result += CHOSUNG_LIST[cho]
        else:
            result += char
    return result

# --- 2. CSS (디자인: 중앙 정렬 & 에러 방지 & 스타일) ---
st.markdown("""
    <style>
        /* 기본 레이아웃 정리 */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* 모바일 화면 여백 최소화 */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 600px;
        }

        /* 텍스트 중앙 정렬 유틸리티 */
        .center-text {
            text-align: center !important;
        }

        /* 시작 화면 제목 */
        .intro-title {
            font-size: 32px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 10px;
            color: #1E1E1E;
        }
        .intro-sub {
            font-size: 20px;
            text-align: center;
            color: #555;
            margin-bottom: 30px;
        }
        
        /* 커스텀 안내 박스 (파란색, 중앙 정렬) */
        .custom-info-box {
            background-color: #e6f3ff;
            color: #0068c9;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
            border: 1px solid #cce5ff;
        }

        /* 타이머 스타일 */
        #timer-box {
            font-size: 24px;
            font-weight: bold;
            color: #ff4b4b;
            text-align: center;
            margin-bottom: 15px;
        }

        /* 문제 (초성) 박스 */
        .chosung-box {
            font-size: 70px;
            font-weight: bold;
            text-align: center;
            color: #333;
            background-color: #f0f2f6;
            border-radius: 20px;
            padding: 30px 0;
            margin-bottom: 20px;
            letter-spacing: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* O/X 피드백 (빨간펜 스타일) */
        .feedback-mark {
            font-size: 180px;
            color: #FF0000;
            text-align: center;
            font-weight: 900;
            line-height: 1.2;
            text-shadow: 3px 3px 0px #fff;
            animation: pop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            margin-top: 20px;
        }
        
        @keyframes pop {
            0% { transform: scale(0.5); opacity: 0; }
            100% { transform: scale(1.0); opacity: 1; }
        }

        /* 최종 등급 메시지 스타일 */
        .tier-text {
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            margin-top: 20px;
            color: #ff4b4b;
        }
        
        /* [중요] 제출 버튼 스타일 (꽉 찬 너비 = 중앙 정렬 효과) */
        /* Streamlit 버전에 따라 data-testid가 다를 수 있어 여러 경로 지정 */
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            background-color: #4CAF50 !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            height: 60px !important;
            font-size: 22px !important;
            border-radius: 12px !important;
            margin-top: 10px !important;
        }
        
        /* 입력창 텍스트 가운데 정렬 */
        input {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. 세션 상태 ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'start'
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'correct_count' not in st.session_state:
    st.session_state.correct_count = 0
if 'current_q_idx' not in st.session_state:
    st.session_state.current_q_idx = 0
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'last_feedback' not in st.session_state:
    st.session_state.last_feedback = None

# --- 4. 로직 함수 ---

def start_game():
    sample_count = min(10, len(ALL_NAMES))
    st.session_state.questions = random.sample(ALL_NAMES, sample_count)
    st.session_state.current_q_idx = 0
    st.session_state.score = 0
    st.session_state.correct_count = 0 
    st.session_state.game_state = 'playing'
    st.session_state.start_time = time.time()
    st.rerun()

def check_answer():
    # 1. 사용자 입력 정리
    user_input = st.session_state.user_input.strip()
    user_input = user_input.replace(" ", "")
    
    # 2. 정답 판별 로직
    target_name = st.session_state.questions[st.session_state.current_q_idx]
    target_chosung = get_chosung(target_name)
    
    # 중복 초성 허용: 해당 초성을 가진 모든 명단을 정답으로 인정
    valid_names = [name for name in ALL_NAMES if get_chosung(name) == target_chosung]
    
    elapsed_time = time.time() - st.session_state.start_time
    time_limit = 30.0 # 제한시간 30초
    
    # 시간 초과 (30.5초 이상)
    if elapsed_time > (time_limit + 0.5):
        st.session_state.last_feedback = 'X'
    # 정답
    elif user_input in valid_names:
        st.session_state.last_feedback = 'O'
        st.session_state.correct_count += 1
        point = max(0, (time_limit - elapsed_time) * (100 / time_limit))
        st.session_state.score += int(point)
    # 오답
    else:
        st.session_state.last_feedback = 'X'
    
    # [중요 수정] 여기서 user_input을 초기화하면 에러가 발생하므로 삭제했습니다.
    # st.form의 clear_on_submit=True 옵션이 자동으로 처리해줍니다.
    
    st.session_state.game_state = 'feedback'

def next_question():
    st.session_state.current_q_idx += 1
    if st.session_state.current_q_idx >= 10:
        st.session_state.game_state = 'end'
    else:
        st.session_state.game_state = 'playing'
        st.session_state.start_time = time.time()
    st.rerun()

# --- 5. 화면 구성 ---

# [화면 1] 시작 화면
if st.session_state.game_state == 'start':
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='intro-title'>A반 이름 맞추기</div>", unsafe_allow_html=True)
    st.markdown("<div class='intro-sub'>초성을 보고 이름을 써넣으세요</div>", unsafe_allow_html=True)
    
    # [수정] st.info 대신 중앙 정렬된 커스텀 div 사용
    st.markdown(f"""
        <div class='custom-info-box'>
            총 10문제 | 제한시간 30초<br><br>
            문제가 꽤 어려우니 집중하세요!
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        if st.button("게임 시작", use_container_width=True, type="primary"):
            start_game()

# [화면 2] 게임 플레이
elif st.session_state.game_state == 'playing':
    current_name = st.session_state.questions[st.session_state.current_q_idx]
    chosung = get_chosung(current_name)
    
    # JS 타이머: 30초 & 자동 제출
    timer_html = """
        <div id="timer-box">⏳ 남은 시간: <span id="time-left">30.0</span>초</div>
        <script>
        var timeLeft = 30.0;
        var timerElement = document.getElementById("time-left");
        
        var timerId = setInterval(function() {
            if (timeLeft <= 0) {
                clearInterval(timerId);
                timerElement.innerHTML = "0.0";
                
                // 시간 종료 시 제출 버튼 강제 클릭
                var btn = window.parent.document.querySelector('div[data-testid="stFormSubmitButton"] button');
                if (btn) {
                    btn.click();
                }
                
            } else {
                timeLeft -= 0.1;
                timerElement.innerHTML = timeLeft.toFixed(1);
            }
        }, 100);
        </script>
    """
    
    st.components.v1.html(timer_html, height=50)
    st.markdown(f"<div class='chosung-box'>{chosung}</div>", unsafe_allow_html=True)
    
    # [중요] clear_on_submit=True 필수
    with st.form(key='answer_form', clear_on_submit=True):
        st.text_input("정답 입력", key="user_input", label_visibility="collapsed", placeholder="여기에 입력하세요")
        
        # 버튼 텍스트
        submitted = st.form_submit_button("제출 (Enter)")
        
        if submitted:
            check_answer()
            st.rerun()

# [화면 3] 피드백 (O/X)
elif st.session_state.game_state == 'feedback':
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    
    feedback = st.session_state.last_feedback
    target_name = st.session_state.questions[st.session_state.current_q_idx]

    if feedback == 'O':
        st.markdown("<div class='feedback-mark'>⭕</div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; color:green; margin-top:20px;'>정답입니다!</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='feedback-mark'>❌</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:#333; margin-top:20px;'>정답은 [ <span style='color:red; font-weight:bold;'>{target_name}</span> ] 입니다.</h3>", unsafe_allow_html=True)

    time.sleep(1.5)
    next_question()

# [화면 4] 종료 화면
elif st.session_state.game_state == 'end':
    total_score = st.session_state.score
    correct_cnt = st.session_state.correct_count
    
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<p class='intro-title'>게임 종료!</p>", unsafe_allow_html=True)
    
    # 결과 요약
    st.markdown(f"""
        <div style='background-color:#f9f9f9; padding:20px; border-radius:15px; text-align:center; margin-bottom:20px; border:1px solid #ddd;'>
            <h3 style='margin:0; color:#555;'>맞춘 문제</h3>
            <h1 style='margin:10px 0; font-size:50px; color:#333;'>{correct_cnt} / 10</h1>
            <hr style='margin: 20px 0;'>
            <h3 style='margin:0; color:#555;'>최종 점수</h3>
            <h1 style='margin:10px 0; font-size:50px; color:#4CAF50;'>{total_score}점</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # 등급 메시지
    tier_msg = ""
    if total_score >= 600:
        tier_msg = "찐사랑💖"
        st.balloons()
    elif total_score >= 200:
        tier_msg = "조금 더 노력해줘💘"
    else:
        tier_msg = "당신... 누구세요?🤔"
        
    st.markdown(f"<div class='tier-text'>{tier_msg}</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        if st.button("다시 도전하기", use_container_width=True):
            st.session_state.game_state = 'start'
            st.rerun()