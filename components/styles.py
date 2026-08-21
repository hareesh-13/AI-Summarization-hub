"""
components/styles.py
All custom CSS for the AI Summarization Hub.
Returns a <style> block for st.markdown injection.
"""


def get_css() -> str:
    return """
<style>
/* ===================================================
   GOOGLE FONTS
=================================================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ===================================================
   CSS VARIABLES / DESIGN TOKENS
=================================================== */
:root {
    --primary:      #4F46E5;
    --primary-dark: #3730A3;
    --secondary:    #7C3AED;
    --accent:       #06B6D4;
    --bg:           #F8FAFC;
    --surface:      #FFFFFF;
    --border:       #E2E8F0;
    --text-primary: #0F172A;
    --text-muted:   #64748B;
    --success:      #10B981;
    --warning:      #F59E0B;
    --error:        #EF4444;
    --radius:       14px;
    --radius-sm:    8px;
    --shadow:       0 4px 24px rgba(79,70,229,0.08);
    --shadow-lg:    0 8px 40px rgba(79,70,229,0.14);
}

/* ===================================================
   GLOBAL RESET & BASE
=================================================== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary);
}

/* Streamlit main app area */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* Remove default Streamlit header decoration */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton, .stAppDeployButton { display: none; }
#stDecoration { display: none; }

/* ===================================================
   SIDEBAR STYLING
=================================================== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E1B4B 0%, #312E81 60%, #1E1B4B 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}

[data-testid="stSidebar"] * {
    color: #E0E7FF !important;
}

[data-testid="stSidebar"] .stRadio label {
    color: #C7D2FE !important;
    font-size: 0.95rem !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
}

/* Sidebar radio button active */
[data-testid="stSidebar"] [data-baseweb="radio"] div[aria-checked="true"] + div {
    color: #A5B4FC !important;
    font-weight: 600 !important;
}

/* ===================================================
   BRAND HEADER IN SIDEBAR
=================================================== */
.sidebar-brand {
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
}

.sidebar-logo {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 0.3rem;
}

.sidebar-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #A5B4FC !important;
    letter-spacing: 0.5px;
}

.sidebar-subtitle {
    font-size: 0.75rem !important;
    color: #818CF8 !important;
    margin-top: 2px;
}

/* ===================================================
   PAGE HERO HEADER
=================================================== */
.page-hero {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #06B6D4 100%);
    border-radius: var(--radius);
    padding: 1.8rem 2rem;
    margin-bottom: 1.8rem;
    box-shadow: var(--shadow-lg);
    animation: heroSlide 0.5s cubic-bezier(0.16,1,0.3,1) both;
}

@keyframes heroSlide {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.hero-icon {
    font-size: 2.8rem;
    flex-shrink: 0;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.25));
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin: 0 !important;
    padding: 0 !important;
    letter-spacing: -0.3px;
}

.hero-subtitle {
    font-size: 0.95rem !important;
    color: rgba(255,255,255,0.82) !important;
    margin-top: 0.3rem !important;
    line-height: 1.5;
}

/* ===================================================
   CARDS
=================================================== */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow);
    transition: box-shadow 0.2s ease;
}

.card:hover {
    box-shadow: var(--shadow-lg);
}

/* ===================================================
   SUMMARY OUTPUT CARD
=================================================== */
.summary-card {
    background: linear-gradient(135deg, #F8F9FF 0%, #F0F4FF 100%);
    border: 1.5px solid #C7D2FE;
    border-radius: var(--radius);
    padding: 1.8rem 2rem;
    margin: 1rem 0 1.5rem 0;
    line-height: 1.8;
    box-shadow: 0 2px 16px rgba(79,70,229,0.06);
    animation: fadeIn 0.4s ease both;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

.summary-card h2 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--primary) !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin-top: 1.4rem !important;
    padding-bottom: 0.3rem;
    border-bottom: 2px solid #E0E7FF;
}

.summary-card h2:first-child { margin-top: 0 !important; }

.summary-card li {
    margin-bottom: 0.4rem;
}

.summary-card strong {
    color: var(--secondary);
}

/* ===================================================
   STREAMLIT WIDGETS OVERRIDE
=================================================== */

/* Primary Button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    box-shadow: 0 4px 14px rgba(79,70,229,0.35) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79,70,229,0.45) !important;
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0px) !important;
}

/* Secondary / default buttons */
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}

/* Text inputs */
.stTextInput > div > div > input,
.stTextArea textarea {
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
    outline: none !important;
}

/* Sidebar Inputs / Placeholder Contrast */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}

[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
    color: #0F172A !important;
}

[data-testid="stSidebar"] .stTextInput input::placeholder,
[data-testid="stSidebar"] .stTextArea textarea::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #64748B !important;
}

/* Select boxes */
.stSelectbox > div > div {
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}

[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 16px rgba(79,70,229,0.1);
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: var(--primary) !important;
}

[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #F1F5F9;
    border-radius: var(--radius-sm);
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: calc(var(--radius-sm) - 2px) !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    transition: all 0.2s ease !important;
}

.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--primary) !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* Expanders */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
}

/* Download buttons */
.stDownloadButton > button {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--primary) !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton > button:hover {
    background: #EEF2FF !important;
    border-color: var(--primary) !important;
    box-shadow: 0 4px 12px rgba(79,70,229,0.15) !important;
    transform: translateY(-1px) !important;
}

/* Spinner text */
.stSpinner > div {
    color: var(--primary) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
}

/* Progress / info / warning / error boxes */
.stAlert {
    border-radius: var(--radius-sm) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F1F5F9; }
::-webkit-scrollbar-thumb { background: #C7D2FE; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ===================================================
   RESPONSIVE
=================================================== */
@media (max-width: 768px) {
    .page-hero {
        flex-direction: column;
        text-align: center;
        padding: 1.2rem;
    }
    .hero-title { font-size: 1.4rem !important; }
}
</style>
"""
