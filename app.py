import streamlit as st
import numpy as np
from datetime import datetime

# -------------------------------------------------
# PAGE SETUP
# -------------------------------------------------
st.set_page_config(
    page_title="Aviator AI Predictor",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# CUSTOM MOBILE APP DESIGN
# -------------------------------------------------
st.markdown("""
<style>

/* Main app */
.stApp {
    background:
        radial-gradient(circle at top, #172554 0%, #081120 40%, #020617 100%);
    color: white;
}

/* Mobile width */
.block-container {
    max-width: 600px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Title */
.logo {
    text-align: center;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 5px;
}

.logo span {
    color: #22c55e;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 25px;
}

/* Cards */
.card {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(71, 85, 105, 0.7);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

/* Prediction */
.prediction-card {
    background: linear-gradient(135deg, #14532d, #064e3b);
    border-radius: 24px;
    padding: 25px;
    text-align: center;
    border: 1px solid #22c55e;
    margin: 15px 0;
}

.prediction-number {
    font-size: 52px;
    font-weight: 900;
    color: #ffffff;
}

.prediction-label {
    color: #bbf7d0;
    font-size: 14px;
}

/* Stats */
.stat-box {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 15px;
    padding: 15px;
    text-align: center;
}

.stat-number {
    font-size: 24px;
    font-weight: bold;
    color: #22c55e;
}

.stat-label {
    font-size: 11px;
    color: #94a3b8;
}

/* Buttons */
.stButton button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: white;
    font-size: 17px;
    font-weight: bold;
    padding: 12px;
}

/* Input */
textarea, input {
    border-radius: 12px !important;
}

/* Warning */
.warning-box {
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid rgba(251, 191, 36, 0.4);
    border-radius: 14px;
    padding: 12px;
    color: #fde68a;
    font-size: 12px;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None


# -------------------------------------------------
# ANALYSIS FUNCTIONS
# -------------------------------------------------

def clean_multiplier(value):
    """Limits extremely large multipliers so they
    don't distort statistical analysis."""
    return min(value, 100)


def calculate_prediction(data):

    data = np.array([clean_multiplier(x) for x in data])

    # Recent data receives more importance
    recent_5 = data[-5:]
    recent_10 = data[-10:] if len(data) >= 10 else data

    # Basic averages
    avg_5 = np.mean(recent_5)
    avg_10 = np.mean(recent_10)
    median = np.median(data)

    # Detect low multiplier streak
    low_streak = 0

    for value in reversed(data):
        if value < 2:
            low_streak += 1
        else:
            break

    # Percentage of rounds below 2x
    low_percentage = np.sum(data < 2) / len(data)

    # Percentage above 5x
    high_percentage = np.sum(data >= 5) / len(data)

    # Volatility
    volatility = np.std(data)

    # -------------------------------------------------
    # AI-STYLE WEIGHTED ESTIMATION
    # -------------------------------------------------

    prediction = (
        avg_5 * 0.45 +
        avg_10 * 0.25 +
        median * 0.30
    )

    # Reduce influence of unrealistic extreme results
    prediction = min(prediction, 10)

    # Small pattern adjustment
    if low_streak >= 3:
        prediction *= 1.10

    if low_percentage > 0.75:
        prediction *= 0.90

    if high_percentage > 0.25:
        prediction *= 1.05

    # Keep output in a reasonable display range
    prediction = max(1.01, min(prediction, 10))

    # Confidence score
    confidence = 50

    if len(data) >= 20:
        confidence += 15

    if len(data) >= 50:
        confidence += 10

    # High volatility = lower confidence
    if volatility < 3:
        confidence += 10
    else:
        confidence -= 10

    confidence = max(35, min(confidence, 85))

    return {
        "prediction": round(prediction, 2),
        "confidence": round(confidence),
        "average": round(np.mean(data), 2),
        "low_percentage": round(low_percentage * 100),
        "high_percentage": round(high_percentage * 100),
        "low_streak": low_streak,
        "volatility": round(volatility, 2)
    }


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.markdown("""
<div class="logo">
✈️ <span>AVIATOR</span> AI
</div>

<div class="subtitle">
Advanced Multiplier Analysis System
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------
# MAIN INPUT CARD
# -------------------------------------------------

st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📊 Enter Previous Results")

st.caption(
    "Paste previous multipliers separated by commas."
)

multipliers_text = st.text_area(
    "Example",
    placeholder="1.12, 2.45, 1.08, 5.60, 1.34, 2.10...",
    height=120,
    label_visibility="collapsed"
)

analyze = st.button("🤖 ANALYZE NEXT ROUND")

st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------
# ANALYZE BUTTON
# -------------------------------------------------

if analyze:

    try:

        values = [
            float(x.strip().replace("x", "").replace("X", ""))
            for x in multipliers_text.split(",")
            if x.strip()
        ]

        if len(values) < 10:

            st.error(
                "Please enter at least 10 previous rounds."
            )

        elif any(x <= 0 for x in values):

            st.error(
                "Multipliers must be greater than 0."
            )

        else:

            result = calculate_prediction(values)

            st.session_state.last_prediction = result

            st.session_state.history.insert(
                0,
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "prediction": result["prediction"],
                    "confidence": result["confidence"]
                }
            )

    except ValueError:

        st.error(
            "Invalid input. Use numbers separated by commas."
        )


# -------------------------------------------------
# DISPLAY PREDICTION
# -------------------------------------------------

if st.session_state.last_prediction:

    result = st.session_state.last_prediction

    prediction = result["prediction"]
    confidence = result["confidence"]

    # Prediction category
    if prediction < 1.50:
        signal = "🔴 HIGH RISK"
        description = "Recent data is concentrated around low multipliers."

    elif prediction < 2.50:
        signal = "🟡 MODERATE RANGE"
        description = "The statistical estimate is around the medium range."

    else:
        signal = "🟢 HIGHER ESTIMATED RANGE"
        description = "Recent historical values produce a higher estimate."

    st.markdown(f"""
    <div class="prediction-card">

        <div class="prediction-label">
            ESTIMATED NEXT RANGE
        </div>

        <div class="prediction-number">
            {prediction}x
        </div>

        <div style="font-size:18px;font-weight:bold;">
            {signal}
        </div>

        <div style="
            font-size:12px;
            color:#dcfce7;
            margin-top:10px;
        ">
            {description}
        </div>

    </div>
    """, unsafe_allow_html=True)


    # -------------------------------------------------
    # STATS
    # -------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">
                {confidence}%
            </div>
            <div class="stat-label">
                CONFIDENCE
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">
                {result["low_percentage"]}%
            </div>
            <div class="stat-label">
                BELOW 2X
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">
                {result["low_streak"]}
            </div>
            <div class="stat-label">
                LOW STREAK
            </div>
        </div>
        """, unsafe_allow_html=True)


    # -------------------------------------------------
    # ADVANCED ANALYSIS
    # -------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🧠 AI Pattern Analysis")

    st.write(
        f"📈 **Average multiplier:** {result['average']}x"
    )

    st.write(
        f"🚀 **Rounds above 5x:** {result['high_percentage']}%"
    )

    st.write(
        f"📉 **Volatility:** {result['volatility']}"
    )

    if result["low_streak"] >= 3:
        st.warning(
            f"⚠️ Low multiplier streak detected: "
            f"{result['low_streak']} consecutive rounds below 2x."
        )

    elif result["low_streak"] == 0:
        st.success(
            "🟢 No current low multiplier streak detected."
        )

    else:
        st.info(
            f"ℹ️ Current low streak: "
            f"{result['low_streak']} round(s)."
        )

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------
# PREDICTION HISTORY
# -------------------------------------------------

if len(st.session_state.history) > 0:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📜 Analysis History")

    for item in st.session_state.history[:10]:

        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            st.write(f"🕒 {item['time']}")

        with col2:
            st.write(f"✈️ {item['prediction']}x")

        with col3:
            st.write(f"🎯 {item['confidence']}%")

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------
# DISCLAIMER
# -------------------------------------------------

st.markdown("""
<div class="warning-box">

⚠️ <b>IMPORTANT:</b> This tool performs statistical
analysis on manually entered historical results.
It does not have access to LuckPesa or any other
betting platform's internal systems, and its output
cannot guarantee the next multiplier.

</div>
""", unsafe_allow_html=True)import streamlit as st
import numpy as np
from datetime import datetime

# -------------------------------------------------
# PAGE SETUP
# -------------------------------------------------
st.set_page_config(
    page_title="Aviator AI Predictor",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# CUSTOM MOBILE APP DESIGN
# -------------------------------------------------
st.markdown("""
<style>

/* Main app */
.stApp {
    background:
        radial-gradient(circle at top, #172554 0%, #081120 40%, #020617 100%);
    color: white;
}

/* Mobile width */
.block-container {
    max-width: 600px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Title */
.logo {
    text-align: center;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 5px;
}

.logo span {
    color: #22c55e;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 25px;
}

/* Cards */
.card {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(71, 85, 105, 0.7);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

/* Prediction */
.prediction-card {
    background: linear-gradient(135deg, #14532d, #064e3b);
    border-radius: 24px;
    padding: 25px;
    text-align: center;
    border: 1px solid #22c55e;
    margin: 15px 0;
}

.prediction-number {
    font-size: 52px;
    font-weight: 900;
    color: #ffffff;
}

.prediction-label {
    color: #bbf7d0;
    font-size: 14px;
}

/* Stats */
.stat-box {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 15px;
    padding: 15px;
    text-align: center;
}

.stat-number {
    font-size: 24px;
    font-weight: bold;
    color: #22c55e;
}

.stat-label {
    font-size: 11px;
    color: #94a3b8;
}

/* Buttons */
.stButton button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: white;
    font-size: 17px;
    font-weight: bold;
    padding: 12px;
}

/* Input */
textarea, input {
    border-radius: 12px !important;
}

/* Warning */
.warning-box {
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid rgba(251, 191, 36, 0.4);
    border-radius: 14px;
    padding: 12px;
    color: #fde68a;
    font-size: 12px;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None


# -------------------------------------------------
# ANALYSIS FUNCTIONS
# -------------------------------------------------

def clean_multiplier(value):
    """Limits extremely large multipliers so they
    don't distort statistical analysis."""
    return min(value, 100)


def calculate_prediction(data):

    data = np.array([clean_multiplier(x) for x in data])

    # Recent data receives more importance
    recent_5 = data[-5:]
    recent_10 = data[-10:] if len(data) >= 10 else data

    # Basic averages
    avg_5 = np.mean(recent_5)
    avg_10 = np.mean(recent_10)
    median = np.median(data)

    # Detect low multiplier streak
    low_streak = 0

    for value in reversed(data):
        if value < 2:
            low_streak += 1
        else:
            break

    # Percentage of rounds below 2x
    low_percentage = np.sum(data < 2) / len(data)

    # Percentage above 5x
    high_percentage = np.sum(data >= 5) / len(data)

    # Volatility
    volatility = np.std(data)

    # -------------------------------------------------
    # AI-STYLE WEIGHTED ESTIMATION
    # -------------------------------------------------

    prediction = (
        avg_5 * 0.45 +
        avg_10 * 0.25 +
        median * 0.30
    )

    # Reduce influence of unrealistic extreme results
    prediction = min(prediction, 10)

    # Small pattern adjustment
    if low_streak >= 3:
        prediction *= 1.10

    if low_percentage > 0.75:
        prediction *= 0.90

    if high_percentage > 0.25:
        prediction *= 1.05

    # Keep output in a reasonable display range
    prediction = max(1.01, min(prediction, 10))

    # Confidence score
    confidence = 50

    if len(data) >= 20:
        confidence += 15

    if len(data) >= 50:
        confidence += 10

    # High volatility = lower confidence
    if volatility < 3:
        confidence += 10
    else:
        confidence -= 10

    confidence = max(35, min(confidence, 85))

    return {
        "prediction": round(prediction, 2),
        "confidence": round(confidence),
        "average": round(np.mean(data), 2),
        "low_percentage": round(low_percentage * 100),
        "high_percentage": round(high_percentage * 100),
        "low_streak": low_streak,
        "volatility": round(volatility, 2)
    }


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.markdown("""
<div class="logo">
✈️ <span>AVIATOR</span> AI
</div>

<div class="subtitle">
Advanced Multiplier Analysis System
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------
# MAIN INPUT CARD
# -------------------------------------------------

st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📊 Enter Previous Results")

st.caption(
    "Paste previous multipliers separated by commas."
)

multipliers_text = st.text_area(
    "Example",
    placeholder="1.12, 2.45, 1.08, 5.60, 1.34, 2.10...",
    height=120,
    label_visibility="collapsed"
)

analyze = st.button("🤖 ANALYZE NEXT ROUND")

st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------
# ANALYZE BUTTON
# -------------------------------------------------

if analyze:

    try:

        values = [
            float(x.strip().replace("x", "").replace("X", ""))
            for x in multipliers_text.split(",")
            if x.strip()
        ]

        if len(values) < 10:

            st.error(
                "Please enter at least 10 previous rounds."
            )

        elif any(x <= 0 for x in values):

            st.error(
                "Multipliers must be greater than 0."
            )

        else:

            result = calculate_prediction(values)

            st.session_state.last_prediction = result

            st.session_state.history.insert(
                0,
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "prediction": result["prediction"],
                    "confidence": result["confidence"]
                }
            )

    except ValueError:

        st.error(
            "Invalid input. Use numbers separated by commas."
        )


# -------------------------------------------------
# DISPLAY PREDICTION
# -------------------------------------------------

if st.session_state.last_prediction:

    result = st.session_state.last_prediction

    prediction = result["prediction"]
    confidence = result["confidence"]

    # Prediction category
    if prediction < 1.50:
        signal = "🔴 HIGH RISK"
        description = "Recent data is concentrated around low multipliers."

    elif prediction < 2.50:
        signal = "🟡 MODERATE RANGE"
        description = "The statistical estimate is around the medium range."

    else:
        signal = "🟢 HIGHER ESTIMATED RANGE"
        description = "Recent historical values produce a higher estimate."

    st.markdown(f"""
    <div class="prediction-card">

        <div class="prediction-label">
            ESTIMATED NEXT RANGE
        </div>

        <div class="prediction-number">
            {prediction}x
        </div>

        <div style="font-size:18px;font-weight:bold;">
            {signal}
        </div>

        <div style="
            font-size:12px;
            color:#dcfce7;
            margin-top:10px;
        ">
            {description}
        </div>

    </div>
    """, unsafe_allow_html=True)


    # -------------------------------------------------
    # STATS
    # -------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">
                {confidence}%
            </div>
            <div class="stat-label">
                CONFIDENCE
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">
                {result["low_percentage"]}%
            </div>
            <div class="stat-label">
                BELOW 2X
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">
                {result["low_streak"]}
            </div>
            <div class="stat-label">
                LOW STREAK
            </div>
        </div>
        """, unsafe_allow_html=True)


    # -------------------------------------------------
    # ADVANCED ANALYSIS
    # -------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🧠 AI Pattern Analysis")

    st.write(
        f"📈 **Average multiplier:** {result['average']}x"
    )

    st.write(
        f"🚀 **Rounds above 5x:** {result['high_percentage']}%"
    )

    st.write(
        f"📉 **Volatility:** {result['volatility']}"
    )

    if result["low_streak"] >= 3:
        st.warning(
            f"⚠️ Low multiplier streak detected: "
            f"{result['low_streak']} consecutive rounds below 2x."
        )

    elif result["low_streak"] == 0:
        st.success(
            "🟢 No current low multiplier streak detected."
        )

    else:
        st.info(
            f"ℹ️ Current low streak: "
            f"{result['low_streak']} round(s)."
        )

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------
# PREDICTION HISTORY
# -------------------------------------------------

if len(st.session_state.history) > 0:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📜 Analysis History")


