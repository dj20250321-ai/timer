import time
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 Custom CSS (반응형 디자인)
# ==========================================
st.set_page_config(
    page_title="⏱️ 나만의 반응형 타이머",
    page_icon="⏱️",
    layout="centered"
)

# Custom CSS: clamp()를 이용한 폰트 반응형 적용, 깔끔한 카드 레이아웃 및 스타일링
st.markdown("""
<style>
    /* 메인 컨테이너 스타일 */
    .main .block-container {
        max-width: 650px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 타이머 카드 디자인 */
    .timer-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
        border-radius: 20px;
        padding: 2rem 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* clamp()를 사용한 반응형 대형 디지털 시계 */
    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        font-size: clamp(3rem, 12vw, 5.5rem);
        font-weight: 800;
        color: #2b2d42;
        letter-spacing: 2px;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    /* 타이머 상태 안내 문구 */
    .timer-status {
        font-size: clamp(0.9rem, 3vw, 1.1rem);
        color: #6c757d;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    /* Streamlit 기본 버튼 스타일 커스텀 */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        height: 3rem;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. Session State (앱 상태 저장소) 초기화
# ==========================================
# 앱이 새로고침되어도 변수 상태를 유지하기 위해 session_state를 사용합니다.
if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 180  # 기본값: 3분 (180초)

if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 180.0

if "is_running" not in st.session_state:
    st.session_state.is_running = False  # 타이머 실행 중 여부

if "is_paused" not in st.session_state:
    st.session_state.is_paused = False    # 일시정지 상태 여부

if "end_time" not in st.session_state:
    st.session_state.end_time = 0.0       # 목표 종료 시간 (time.monotonic 기준)


# ==========================================
# 3. 타이머 제어 함수 (Callback Functions)
# ==========================================
def start_timer():
    """타이머 시작 함수"""
    # 입력된 총 시간이 0초 이하인 경우 실행 불가
    if st.session_state.total_seconds <= 0:
        st.toast("⚠️ 0분 0초 이상 시간을 설정해 주세요!", icon="⚠️")
        return
    
    # 목표 완료 시간을 현재 monotonic 시간 + 설정한 잔여 시간으로 저장
    st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds
    st.session_state.is_running = True
    st.session_state.is_paused = False

def pause_timer():
    """타이머 일시정지 함수"""
    if st.session_state.is_running:
        # 일시정지 시점의 남은 시간을 정확히 누적 계산해 둡니다.
        st.session_state.remaining_seconds = max(0.0, st.session_state.end_time - time.monotonic())
        st.session_state.is_running = False
        st.session_state.is_paused = True

def resume_timer():
    """타이머 계속(재개) 함수"""
    if st.session_state.is_paused and st.session_state.remaining_seconds > 0:
        # 남은 시간을 기반으로 새로운 end_time을 다시 계산합니다.
        st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds
        st.session_state.is_running = True
        st.session_state.is_paused = False

def reset_timer():
    """타이머 초기화 함수"""
    st.session_state.is_running = False
    st.session_state.is_paused = False
    st.session_state.remaining_seconds = float(st.session_state.total_seconds)

def set_quick_time(seconds):
    """빠른 설정 버튼 클릭 시 호출되는 함수"""
    # 실행 중일 때는 시간 변경 불가
    if not st.session_state.is_running:
        st.session_state.total_seconds = seconds
        st.session_state.remaining_seconds = float(seconds)
        st.session_state.is_paused = False


# ==========================================
# 4. 실시간 UI 갱신 Fragment 영역
# ==========================================
# st.fragment를 사용하여 페이지 전체를 다시 그리지 않고, 0.1초마다 이 영역만 갱신합니다.
@st.fragment(run_every=0.1 if st.session_state.is_running else None)
def render_timer_ui():
    """시간 계산 및 타이머 디스플레이 출력 함수"""
    
    # [시간 계산 핵심 로직] 
    # 단순히 1씩 빼지 않고 time.monotonic()으로 실제 흘러간 오차 없는 시간을 계산합니다.
    if st.session_state.is_running:
        current_remaining = st.session_state.end_time - time.monotonic()
        
        # 타이머 종료 처리
        if current_remaining <= 0:
            st.session_state.remaining_seconds = 0.0
            st.session_state.is_running = False
            st.session_state.is_paused = False
        else:
            st.session_state.remaining_seconds = current_remaining

    # 시, 분, 초 단위 계산
    rem = int(max(0, st.session_state.remaining_seconds))
    mins, secs = divmod(rem, 60)
    time_str = f"{mins:02d}:{secs:02d}"

    # 진행률(Progress Bar) 계산 (0.0 ~ 1.0)
    if st.session_state.total_seconds > 0:
        progress = max(0.0, min(1.0, st.session_state.remaining_seconds / st.session_state.total_seconds))
    else:
        progress = 0.0

    # 상태 메시지 정의
    if st.session_state.is_running:
        status_msg = "🔥 집중하는 시간입니다!"
    elif st.session_state.is_paused:
        status_msg = "⏸️ 잠시 일시정지되었습니다."
    elif st.session_state.remaining_seconds == 0 and st.session_state.total_seconds > 0:
        status_msg = "🎉 시간이 모두 완료되었습니다!"
    else:
        status_msg = "READY"

    # 카드 형태의 메인 타이머 UI
    st.markdown(f"""
    <div class="timer-card">
        <div class="timer-status">{status_msg}</div>
        <div class="timer-display">{time_str}</div>
    </div>
    """, unsafe_allow_html=True)

    # 진행률 막대
    st.progress(progress)

    # 시간이 완료되었을 때 실행되는 효과
    if st.session_state.remaining_seconds == 0 and not st.session_state.is_running and not st.session_state.is_paused:
        if st.session_state.total_seconds > 0:
            st.balloons()
            st.success("🎊 설정한 시간이 끝났습니다! 수고하셨습니다!")


# ==========================================
# 5. 메인 앱 화면 구성
# ==========================================
st.title("⏱️ 나만의 반응형 타이머")
st.write("스마트폰과 PC 어디서나 편리하게 사용할 수 있는 나만의 타이머입니다.")

st.write("")

# 1) 실시간 타이머 및 진행률 표시
render_timer_ui()

st.write("")

# 2) 타이머 제어 버튼 영역 (반응형 2열 / 4열 배치)
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if not st.session_state.is_running and not st.session_state.is_paused:
        # 시작 버튼
        st.button("▶️ 시작", on_click=start_timer, use_container_width=True, type="primary")
    elif st.session_state.is_running:
        # 일시정지 버튼
        st.button("⏸️ 일시정지", on_click=pause_timer, use_container_width=True)
    elif st.session_state.is_paused:
        # 계속(재개) 버튼
        st.button("▶️ 계속", on_click=resume_timer, use_container_width=True, type="primary")

with btn_col2:
    # 초기화 버튼
    st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)

st.divider()

# 3) 빠른 설정 버튼 (1분, 3분, 5분, 10분)
st.subheader("⚡ 빠른 시간 설정")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

# 실행 중일 때는 빠른 설정 버튼 비활성화 (오류 방지)
is_disabled = st.session_state.is_running or st.session_state.is_paused

with q_col1:
    st.button("1분", on_click=set_quick_time, args=(60,), use_container_width=True, disabled=is_disabled)
with q_col2:
    st.button("3분", on_click=set_quick_time, args=(180,), use_container_width=True, disabled=is_disabled)
with q_col3:
    st.button("5분", on_click=set_quick_time, args=(300,), use_container_width=True, disabled=is_disabled)
with q_col4:
    st.button("10분", on_click=set_quick_time, args=(600,), use_container_width=True, disabled=is_disabled)

st.write("")

# 4) 사용자 수동 시간 설정 영역
st.subheader("⚙️ 직접 시간 설정")

input_col1, input_col2 = st.columns(2)

# 현재 세션의 total_seconds 값을 기반으로 분과 초 초기값 추출
default_m, default_s = divmod(st.session_state.total_seconds, 60)

with input_col1:
    user_m = st.number_input(
        "분 (Minutes)",
        min_value=0,
        max_value=180,
        value=default_m,
        step=1,
        disabled=is_disabled,
        key="input_minutes"
    )

with input_col2:
    user_s = st.number_input(
        "초 (Seconds)",
        min_value=0,
        max_value=59,
        value=default_s,
        step=1,
        disabled=is_disabled,
        key="input_seconds"
    )

# 입력값이 변경되었을 때 실행 중이 아니라면 세션 상태 업데이트
if not is_disabled:
    calculated_seconds = (user_m * 60) + user_s
    if calculated_seconds != st.session_state.total_seconds:
        st.session_state.total_seconds = calculated_seconds
        st.session_state.remaining_seconds = float(calculated_seconds)
        st.rerun()
