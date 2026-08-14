import time
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 Custom CSS
# ==========================================
st.set_page_config(
    page_title="⏱️ 나만의 반응형 타이머",
    page_icon="⏱️",
    layout="centered"
)

st.markdown("""
<style>
    .main .block-container {
        max-width: 650px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .timer-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
        border-radius: 20px;
        padding: 2rem 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        font-size: clamp(3rem, 12vw, 5.5rem);
        font-weight: 800;
        color: #2b2d42;
        letter-spacing: 2px;
        margin: 0.5rem 0;
        line-height: 1;
    }
    .timer-status {
        font-size: clamp(0.9rem, 3vw, 1.1rem);
        color: #6c757d;
        font-weight: 600;
        margin-top: 0.5rem;
    }
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
# 2. Session State 초기화
# ==========================================
if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 180  # 기본 3분

if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 180.0

if "is_running" not in st.session_state:
    st.session_state.is_running = False

if "is_paused" not in st.session_state:
    st.session_state.is_paused = False

if "end_time" not in st.session_state:
    st.session_state.end_time = 0.0

# number_input 동기화를 위한 입력 변수 세션 저장
if "input_m" not in st.session_state:
    st.session_state.input_m = 3

if "input_s" not in st.session_state:
    st.session_state.input_s = 0


# ==========================================
# 3. 타이머 제어 및 시간 설정 함수
# ==========================================
def start_timer():
    if st.session_state.total_seconds <= 0:
        st.toast("⚠️ 0분 0초 이상 시간을 설정해 주세요!", icon="⚠️")
        return
    st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds
    st.session_state.is_running = True
    st.session_state.is_paused = False

def pause_timer():
    if st.session_state.is_running:
        st.session_state.remaining_seconds = max(0.0, st.session_state.end_time - time.monotonic())
        st.session_state.is_running = False
        st.session_state.is_paused = True

def resume_timer():
    if st.session_state.is_paused and st.session_state.remaining_seconds > 0:
        st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds
        st.session_state.is_running = True
        st.session_state.is_paused = False

def reset_timer():
    st.session_state.is_running = False
    st.session_state.is_paused = False
    st.session_state.remaining_seconds = float(st.session_state.total_seconds)

def set_quick_time(seconds):
    """빠른 설정 클릭 시 전체 세션 상태를 확실하게 일괄 업데이트합니다."""
    if not st.session_state.is_running and not st.session_state.is_paused:
        st.session_state.total_seconds = seconds
        st.session_state.remaining_seconds = float(seconds)
        
        # number_input에 연결된 값도 함께 변경
        m, s = divmod(seconds, 60)
        st.session_state.input_m = m
        st.session_state.input_s = s


# ==========================================
# 4. 실시간 UI 갱신 Fragment
# ==========================================
@st.fragment(run_every=0.1 if st.session_state.is_running else None)
def render_timer_ui():
    if st.session_state.is_running:
        current_remaining = st.session_state.end_time - time.monotonic()
        if current_remaining <= 0:
            st.session_state.remaining_seconds = 0.0
            st.session_state.is_running = False
            st.session_state.is_paused = False
        else:
            st.session_state.remaining_seconds = current_remaining

    rem = int(max(0, st.session_state.remaining_seconds))
    mins, secs = divmod(rem, 60)
    time_str = f"{mins:02d}:{secs:02d}"

    if st.session_state.total_seconds > 0:
        progress = max(0.0, min(1.0, st.session_state.remaining_seconds / st.session_state.total_seconds))
    else:
        progress = 0.0

    if st.session_state.is_running:
        status_msg = "🔥 집중하는 시간입니다!"
    elif st.session_state.is_paused:
        status_msg = "⏸️ 잠시 일시정지되었습니다."
    elif st.session_state.remaining_seconds == 0 and st.session_state.total_seconds > 0:
        status_msg = "🎉 시간이 모두 완료되었습니다!"
    else:
        status_msg = "READY"

    st.markdown(f"""
    <div class="timer-card">
        <div class="timer-status">{status_msg}</div>
        <div class="timer-display">{time_str}</div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress)

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
render_timer_ui()
st.write("")

# 제어 버튼
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if not st.session_state.is_running and not st.session_state.is_paused:
        st.button("▶️ 시작", on_click=start_timer, use_container_width=True, type="primary")
    elif st.session_state.is_running:
        st.button("⏸️ 일시정지", on_click=pause_timer, use_container_width=True)
    elif st.session_state.is_paused:
        st.button("▶️ 계속", on_click=resume_timer, use_container_width=True, type="primary")

with btn_col2:
    st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)

st.divider()

# 빠른 시간 설정 영역
st.subheader("⚡ 빠른 시간 설정")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

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

# 직접 시간 설정 영역 (key로 세션 상태 자동 연동)
st.subheader("⚙️ 직접 시간 설정")
input_col1, input_col2 = st.columns(2)

def update_manual_time():
    """직접 수치를 입력해 변경했을 때 처리 함수"""
    total = (st.session_state.input_m * 60) + st.session_state.input_s
    st.session_state.total_seconds = total
    st.session_state.remaining_seconds = float(total)

with input_col1:
    st.number_input(
        "분 (Minutes)",
        min_value=0,
        max_value=180,
        step=1,
        disabled=is_disabled,
        key="input_m",
        on_change=update_manual_time
    )

with input_col2:
    st.number_input(
        "초 (Seconds)",
        min_value=0,
        max_value=59,
        step=1,
        disabled=is_disabled,
        key="input_s",
        on_change=update_manual_time
    )
