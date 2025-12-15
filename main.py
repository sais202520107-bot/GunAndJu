import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="Netflix 한국 콘텐츠 트렌드 분석",
    layout="wide"
)

# -----------------------------
# 데이터 로드 (에러 방어)
# -----------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("netflix_korea_10y_trend.csv")
    except FileNotFoundError:
        st.error("❌ netflix_korea_10y_trend.csv 파일을 찾을 수 없습니다.")
        st.stop()
    return df

df = load_data()

# -----------------------------
# 필수 컬럼 검사
# -----------------------------
required_cols = ['release_year', 'type', 'listed_in']
for col in required_cols:
    if col not in df.columns:
        st.error(f"❌ 필수 컬럼이 없습니다: {col}")
        st.stop()

# -----------------------------
# 최소 전처리 (웹 안정성)
# -----------------------------
df = df.dropna(subset=['release_year'])
df['release_year'] = df['release_year'].astype(int)
df['type'] = df['type'].fillna("Unknown")
df['listed_in'] = df['listed_in'].fillna("Unknown")

# -----------------------------
# 제목 & 설명
# -----------------------------
st.title("🎬 최근 10년간 Netflix 한국 콘텐츠 트렌드")
st.markdown(
    """
    이 대시보드는 **Netflix에 공개된 한국 콘텐츠만을 대상으로**  
    최근 10년간 콘텐츠 수, 유형, 장르 변화를 분석합니다.
    """
)

# -----------------------------
# 사이드바: 연도 선택
# -----------------------------
st.sidebar.header("🔎 분석 조건")

min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())

year_range = st.sidebar.slider(
    "연도 범위 선택",
    min_year,
    max_year,
    (min_year, max_year)
)

filtered = df[
    (df['release_year'] >= year_range[0]) &
    (df['release_year'] <= year_range[1])
]

if filtered.empty:
    st.warning("⚠️ 선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# -----------------------------
# 1️⃣ 연도별 한국 콘텐츠 수 변화
# -----------------------------
st.subheader("📈 연도별 한국 콘텐츠 수 변화")

yearly = filtered.groupby('release_year').size()

fig1, ax1 = plt.subplots()
ax1.plot(yearly.index, yearly.values)
ax1.set_xlabel("연도")
ax1.set_ylabel("콘텐츠 수")
st.pyplot(fig1)

# -----------------------------
# 2️⃣ 영화 vs TV 쇼 변화
# -----------------------------
st.subheader("🎞 한국 콘텐츠 유형 분포")

type_counts = filtered['type'].value_counts()

fig2, ax2 = plt.subplots()
ax2.bar(type_counts.index, type_counts.values)
ax2.set_ylabel("개수")
st.pyplot(fig2)

# -----------------------------
# 3️⃣ 한국 콘텐츠 장르 트렌드 (Top 5)
# -----------------------------
st.subheader("🎭 한국 콘텐츠 주요 장르 (Top 5)")

genre_counts = (
    filtered['listed_in']
    .str.split(', ')
    .explode()
    .value_counts()
    .head(5)
)

fig3, ax3 = plt.subplots()
ax3.barh(genre_counts.index, genre_counts.values)
ax3.set_xlabel("콘텐츠 수")
st.pyplot(fig3)

# -----------------------------
# 4️⃣ 데이터 테이블
# -----------------------------
st.subheader("📄 한국 콘텐츠 데이터 미리보기")
st.dataframe(filtered.head(50))
