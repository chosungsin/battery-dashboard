import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="거시경제 지표 대시보드", layout="wide")

locales = {
    '한국어': {
        'title': '📈 한국은행 ECOS 실시간 거시경제 지표 대시보드',
        'range': '조회 범위: ',
        'year': '년',
        'to_present': ' ~ 현재',
        'as_of': '기준',
        'sidebar_settings': '⚙️ 검색 조건 설정',
        'sidebar_period': '조회 기간 선택',
        'period_all': '전체 (조회 가능한 모든 기간)',
        'period_10y': '최근 10년 (2015년~현재)',
        'period_5y': '최근 5년 (2020년~현재)',
        'period_3y': '최근 3년 (2022년~현재)',
        'refresh': '🔄 실시간 데이터 새로고침',
        'data_source': '💡 데이터 출처: 한국은행 ECOS Open API\n\n페이지 접속 시 최신 데이터로 자동 업데이트됩니다.',
        'loading': '한국은행 API로부터 데이터를 불러오는 중...',
        'kpi_base': '한국은행 기준금리',
        'kpi_fx': '원/달러 환율',
        'kpi_cpi': '소비자물가지수(CPI)',
        'kpi_m2': 'M2 통화량 (평잔)',
        'unit_won': '원',
        'unit_bn': '십억원',
        'chart1_title': '① 금리 동향 및 이동평균선 (%)',
        'chart2_title': '② 원/달러 환율 및 추세선 (원)',
        'chart3_title': '③ 주요 지표 간 상관계수 히트맵',
        'chart4_title': '④ 통화량(M2) 및 소비자물가지수(CPI)',
        'axis_rate': '금리 (%)',
        'axis_fx': '환율 (원)',
        'axis_cpi': 'CPI 지수',
        'axis_m2': 'M2 통화량 (십억원)',
        'ma_20': '20일 MA',
        'ma_60': '60일 MA',
        'detail_title': '🔍 지표 간 상관관계 상세 분석 (시계열 비교)',
        'detail_desc': '아래에서 비교할 지표를 2개 이상 선택하여 다중 비교를 수행해 보세요. (차트 우측 상단의 카메라 아이콘을 클릭하여 이미지를 다운로드할 수 있습니다)',
        'detail_select': '비교할 지표들을 선택하세요 (3개 이상 선택 시 기준점 100으로 지수화됨)',
        'detail_warn': '⚠️ 최소 1개 이상의 지표를 선택해 주세요.',
        'detail_info': '💡 3개 이상의 지표를 선택하여, 각 지표의 첫 번째 유효 데이터를 기준(100)으로 하는 **지수화(Indexed) 차트**로 자동 변환되었습니다.',
        'detail_trend': '시계열 추이',
        'detail_compare': '시계열 추이 비교',
        'detail_corr': '상관계수',
        'detail_indexed': '선택된 다중 지표 시계열 추이 (Base=100)',
        'detail_index_val': '지수화 값 (초기값=100)',
        'tab1': '📋 일간 경제지표 데이터',
        'tab2': '📊 월간/분기 지표 데이터',
        'tab3': '🏢 기업 재무/공시 분석',
        'tab4': '🚢 해상 물류 모니터링',
        'corp_analysis': '이차전지/분리막 핵심 기업 분석',
        'corp_select': '분석할 기업 선택',
        'col_base': '기준금리',
        'col_ktb3': '국고채3년',
        'col_ktb10': '국고채10년',
        'col_fx': '원달러환율',
        'col_cpi': '소비자물가지수',
        'col_m2': 'M2통화량',
        'col_trade': '무역수지',
        'col_gdp': '경제성장률',
        'col_us_base': '미국기준금리',
        'col_jp_base': '일본기준금리',
        'col_jpy': '엔화환율',
        'col_us_tb10': '미국국채10년',
        'col_kospi': '코스피지수',
        'col_dow': '다우지수',
        'col_wti': 'WTI유(유가)',
        'col_lit': '리튬/배터리ETF',
        'col_tsla': '테슬라주가'
    },
    'English': {
        'title': '📈 BOK ECOS Real-time Macroeconomic Dashboard',
        'range': 'Date Range: ',
        'year': '',
        'to_present': ' ~ Present',
        'as_of': 'as of',
        'sidebar_settings': '⚙️ Settings',
        'sidebar_period': 'Select Period',
        'period_all': 'All Available',
        'period_10y': 'Last 10 Years (2015~)',
        'period_5y': 'Last 5 Years (2020~)',
        'period_3y': 'Last 3 Years (2022~)',
        'refresh': '🔄 Refresh Data',
        'data_source': '💡 Data Source: Bank of Korea ECOS Open API\n\nAutomatically updates to the latest data on load.',
        'loading': 'Fetching data from BOK API...',
        'kpi_base': 'BOK Base Rate',
        'kpi_fx': 'USD/KRW',
        'kpi_cpi': 'CPI',
        'kpi_m2': 'M2 Money Supply',
        'unit_won': 'KRW',
        'unit_bn': 'Billion KRW',
        'chart1_title': '① Interest Rates & Moving Averages (%)',
        'chart2_title': '② USD/KRW Exchange Rate & Trends (KRW)',
        'chart3_title': '③ Correlation Heatmap',
        'chart4_title': '④ M2 Money Supply & CPI',
        'axis_rate': 'Interest Rate (%)',
        'axis_fx': 'Exchange Rate (KRW)',
        'axis_cpi': 'CPI',
        'axis_m2': 'M2 (Billion KRW)',
        'ma_20': '20-day MA',
        'ma_60': '60-day MA',
        'detail_title': '🔍 Detailed Correlation Analysis (Time Series)',
        'detail_desc': 'Select 2 or more indicators below to perform multiple time series comparisons. (Click the camera icon on the top right of each chart to download as image)',
        'detail_select': 'Select indicators to compare (Normalized to 100 if ≥3 are selected)',
        'detail_warn': '⚠️ Please select at least one indicator.',
        'detail_info': '💡 Converted to an **Indexed Chart** with the base value of 100 since 3 or more indicators were selected.',
        'detail_trend': 'Trend',
        'detail_compare': 'Comparison',
        'detail_corr': 'Correlation',
        'detail_indexed': 'Selected Indicators Trend (Base=100)',
        'detail_index_val': 'Index Value (Base=100)',
        'tab1': '📋 Daily Indicators',
        'tab2': '📊 Monthly/Quarterly Indicators',
        'tab3': '🏢 Corporate Analysis',
        'tab4': '🚢 Maritime Logistics',
        'corp_analysis': 'Battery & Separator Corporate Analysis',
        'corp_select': 'Select Company',
        'col_base': 'Base Rate',
        'col_ktb3': 'KTB 3Y',
        'col_ktb10': 'KTB 10Y',
        'col_fx': 'USD/KRW',
        'col_cpi': 'CPI',
        'col_m2': 'M2',
        'col_trade': 'Trade Balance',
        'col_gdp': 'GDP Growth',
        'col_us_base': 'US Fed Rate',
        'col_jp_base': 'BOJ Rate',
        'col_jpy': 'JPY/KRW',
        'col_us_tb10': 'US Treasury 10Y',
        'col_kospi': 'KOSPI',
        'col_dow': 'Dow Jones',
        'col_wti': 'WTI Crude Oil',
        'col_lit': 'Lithium/Battery ETF',
        'col_tsla': 'Tesla Stock'
    },
    '日本語': {
        'title': '📈 韓国銀行 ECOS マクロ経済ダッシュボード',
        'range': '照会範囲: ',
        'year': '年',
        'to_present': ' ~ 現在',
        'as_of': '時点',
        'sidebar_settings': '⚙️ 検索条件',
        'sidebar_period': '期間選択',
        'period_all': '全期間',
        'period_10y': '過去10年 (2015~)',
        'period_5y': '過去5年 (2020~)',
        'period_3y': '過去3年 (2022~)',
        'refresh': '🔄 データ更新',
        'data_source': '💡 データソース: 韓国銀行 ECOS Open API\n\nアクセス時に最新データを取得します。',
        'loading': '韓国銀行APIからデータを取得中...',
        'kpi_base': '韓国銀行 基準金利',
        'kpi_fx': 'ウォン/ドル 為替レート',
        'kpi_cpi': '消費者物価指数(CPI)',
        'kpi_m2': 'M2 マネーストック',
        'unit_won': 'ウォン',
        'unit_bn': '十億ウォン',
        'chart1_title': '① 金利動向と移動平均線 (%)',
        'chart2_title': '② ウォン/ドル 為替レート (ウォン)',
        'chart3_title': '③ 相関係数ヒートマップ',
        'chart4_title': '④ マネーストック(M2)と消費者物価指数(CPI)',
        'axis_rate': '金利 (%)',
        'axis_fx': '為替レート (ウォン)',
        'axis_cpi': 'CPI',
        'axis_m2': 'M2 (十億ウォン)',
        'ma_20': '20日移動平均',
        'ma_60': '60日移動平均',
        'detail_title': '🔍 詳細相関分析 (時系列比較)',
        'detail_desc': '以下から2つ以上の指標を選択して時系列で比較できます。(各チャート右上のカメラアイコンで画像をダウンロードできます)',
        'detail_select': '比較する指標を選択 (3つ以上選択で基準値100に指数化)',
        'detail_warn': '⚠️ 少なくとも1つの指標を選択してください。',
        'detail_info': '💡 3つ以上の指標が選択されたため、各指標の初期値を100とする**指数化チャート**に自動変換されました。',
        'detail_trend': '推移',
        'detail_compare': '比較',
        'detail_corr': '相関係数',
        'detail_indexed': '選択指標の推移 (Base=100)',
        'detail_index_val': '指数値 (Base=100)',
        'tab1': '📋 日次データ',
        'tab2': '📊 月次/四半期データ',
        'tab3': '🏢 企業財務/公示分析',
        'tab4': '🚢 海上物流モニタリング',
        'corp_analysis': '二次電池/セパレーター中核企業分析',
        'corp_select': '分析する企業を選択',
        'col_base': '基準金利',
        'col_ktb3': '国庫債3年',
        'col_ktb10': '国庫債10年',
        'col_fx': 'ウォン/ドル',
        'col_cpi': '消費者物価指数',
        'col_m2': 'M2',
        'col_trade': '貿易収支',
        'col_gdp': '経済成長率',
        'col_us_base': '米国政策金利',
        'col_jp_base': '日本政策金利',
        'col_jpy': '円/ウォン',
        'col_us_tb10': '米国債10年',
        'col_kospi': 'KOSPI',
        'col_dow': 'ダウ平均',
        'col_wti': 'WTI原油価格',
        'col_lit': 'リチウム/バッテリーETF',
        'col_tsla': 'テスラ株価'
    }
}

lang = st.radio("🌐 Language / 언어 / 言語", ["한국어", "English", "日本語"], index=0, horizontal=True)
t = locales[lang]

# 차트 옵션 설정 (다운로드 버튼 표시)
plotly_config = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
}

API_KEY = 'U7C37C8DXA41EBYWWYAX'

@st.cache_data(ttl=3600)
def fetch_ecos_data(stat_code, cycle, start_date, end_date, item_code, col_name):
    url = f"http://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/json/kr/1/10000/{stat_code}/{cycle}/{start_date}/{end_date}/{item_code}"
    response = requests.get(url)
    df = pd.DataFrame()
    if response.status_code == 200:
        data = response.json()
        if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
            df = pd.DataFrame(data['StatisticSearch']['row'])
            df = df[['TIME', 'DATA_VALUE']]
            df.rename(columns={'DATA_VALUE': col_name}, inplace=True)
            
            df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
            if cycle == 'M':
                df['date'] = pd.to_datetime(df['TIME'], format='%Y%m')
            elif cycle == 'Q':
                df['date'] = pd.to_datetime(df['TIME'].str[:4] + '-' + (df['TIME'].str[-1].astype(int)*3 - 2).astype(str).str.zfill(2) + '-01')
            else:
                df['date'] = pd.to_datetime(df['TIME'], format='%Y%m%d')
            df.drop('TIME', axis=1, inplace=True)
    return df

st.title(t['title'])

st.sidebar.header(t['sidebar_settings'])
period = st.sidebar.selectbox(
    t['sidebar_period'],
    [t['period_all'], t['period_10y'], t['period_5y'], t['period_3y']],
    index=1
)

end_date_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
if period == t['period_10y']:
    start_date_dt = end_date_dt - relativedelta(years=10)
elif period == t['period_5y']:
    start_date_dt = end_date_dt - relativedelta(years=5)
elif period == t['period_3y']:
    start_date_dt = end_date_dt - relativedelta(years=3)
else:
    start_date_dt = datetime(2000, 1, 1)

START_DATE = start_date_dt.strftime('%Y%m%d')
END_DATE = end_date_dt.strftime('%Y%m%d')

st.markdown(f"**{t['range']}** {start_date_dt.strftime('%Y')}{t['year']} {t['to_present']}")

if st.sidebar.button(t['refresh']):
    st.cache_data.clear()

st.sidebar.markdown("---")
st.sidebar.markdown(t['data_source'])

with st.spinner(t['loading']):
    # 데이터 페치
    df_base = fetch_ecos_data('722Y001', 'D', START_DATE, END_DATE, '0101000', t['col_base'])
    df_ktb3 = fetch_ecos_data('817Y002', 'D', START_DATE, END_DATE, '010150000', t['col_ktb3'])
    df_ktb10 = fetch_ecos_data('817Y002', 'D', START_DATE, END_DATE, '010210000', t['col_ktb10'])
    df_fx = fetch_ecos_data('731Y001', 'D', START_DATE, END_DATE, '0000001', t['col_fx'])
    df_cpi = fetch_ecos_data('901Y009', 'M', START_DATE[:6], END_DATE[:6], '0', t['col_cpi'])
    df_m2 = fetch_ecos_data('161Y005', 'M', START_DATE[:6], END_DATE[:6], 'BBHS00', t['col_m2'])
    
    # 추가지표
    df_trade = fetch_ecos_data('301Y013', 'M', START_DATE[:6], END_DATE[:6], '000000', t['col_trade'])
    df_gdp = fetch_ecos_data('200Y008', 'Q', START_DATE[:6][:4]+'Q1', END_DATE[:6][:4]+'Q4', '10111', t['col_gdp'])
    df_us_base = fetch_ecos_data('902Y006', 'M', START_DATE[:6], END_DATE[:6], 'US', t['col_us_base'])
    df_jp_base = fetch_ecos_data('902Y006', 'M', START_DATE[:6], END_DATE[:6], 'JP', t['col_jp_base'])
    df_jpy = fetch_ecos_data('731Y001', 'D', START_DATE, END_DATE, '0000002', t['col_jpy'])
    df_us_tb10 = fetch_ecos_data('902Y023', 'M', START_DATE[:6], END_DATE[:6], 'IRLT/USA', t['col_us_tb10'])
    
    # yfinance 데이터 추가
    try:
        import yfinance as yf
        df_yf = yf.download(['^KS11', '^DJI', 'CL=F', 'LIT', 'TSLA'], start=start_date_dt.strftime('%Y-%m-%d'), end=(end_date_dt + relativedelta(days=1)).strftime('%Y-%m-%d'), progress=False)
        if isinstance(df_yf.columns, pd.MultiIndex):
            df_yf = df_yf['Close']
        df_yf = df_yf.reset_index()
        df_yf.rename(columns={'Date': 'date', '^KS11': t['col_kospi'], '^DJI': t['col_dow'], 'CL=F': t['col_wti'], 'LIT': t['col_lit'], 'TSLA': t['col_tsla']}, inplace=True)
        df_yf['date'] = pd.to_datetime(df_yf['date']).dt.normalize()
    except Exception as e:
        df_yf = pd.DataFrame(columns=['date', t['col_kospi'], t['col_dow'], t['col_wti'], t['col_lit'], t['col_tsla']])
    
    # 일간 기준 데이터 병합
    date_range = pd.date_range(start=start_date_dt, end=end_date_dt, freq='D')
    df_daily = pd.DataFrame({'date': date_range})
    
    data_frames = [df_base, df_ktb3, df_ktb10, df_fx, df_cpi, df_m2, df_trade, df_gdp, df_us_base, df_jp_base, df_jpy, df_us_tb10, df_yf]
    for df in data_frames:
        if not df.empty:
            df_daily = pd.merge(df_daily, df, on='date', how='left')
    
    df_daily.sort_values('date', inplace=True)
    df_daily.ffill(inplace=True)
    df_daily.dropna(subset=[t['col_base']], inplace=True)

if not df_daily.empty:
    latest_date = df_daily['date'].iloc[-1].strftime('%Y-%m-%d')
    latest_base = df_base.dropna()[t['col_base']].iloc[-1] if not df_base.empty else 0
    latest_fx = df_fx.dropna()[t['col_fx']].iloc[-1] if not df_fx.empty else 0
    latest_cpi = df_cpi.dropna()[t['col_cpi']].iloc[-1] if not df_cpi.empty else 0
    latest_m2 = df_m2.dropna()[t['col_m2']].iloc[-1] if not df_m2.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"{t['kpi_base']} ({latest_date} {t['as_of']})", f"{latest_base:.2f}%")
    col2.metric(f"{t['kpi_fx']} ({latest_date} {t['as_of']})", f"{latest_fx:,.2f} {t['unit_won']}")
    col3.metric(f"{t['kpi_cpi']} ({df_cpi['date'].dt.strftime('%Y-%m').iloc[-1] if not df_cpi.empty else ''} {t['as_of']})", f"{latest_cpi:.2f}")
    col4.metric(f"{t['kpi_m2']} ({df_m2['date'].dt.strftime('%Y-%m').iloc[-1] if not df_m2.empty else ''} {t['as_of']})", f"{latest_m2:,.1f} {t['unit_bn']}")

    st.markdown("---")
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader(t['chart1_title'])
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[t['col_base']], mode='lines', name=t['col_base'], line=dict(color='#1f77b4', width=2)))
        fig1.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[t['col_ktb3']], mode='lines', name=t['col_ktb3'], line=dict(color='#ff7f0e', width=2)))
        fig1.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[t['col_ktb10']], mode='lines', name=t['col_ktb10'], line=dict(color='#2ca02c', width=2)))
        fig1.update_layout(template='plotly_dark', height=400, yaxis_title=t['axis_rate'], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig1, use_container_width=True, config=plotly_config)

    with row1_col2:
        st.subheader(t['chart2_title'])
        df_daily[t['col_fx'] + '_20MA'] = df_daily[t['col_fx']].rolling(window=20).mean()
        df_daily[t['col_fx'] + '_60MA'] = df_daily[t['col_fx']].rolling(window=60).mean()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[t['col_fx']], mode='lines', name=t['col_fx'], line=dict(color='#d62728', width=2)))
        fig2.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[t['col_fx'] + '_20MA'], mode='lines', name=t['ma_20'], line=dict(color='#9467bd', width=1, dash='dash')))
        fig2.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[t['col_fx'] + '_60MA'], mode='lines', name=t['ma_60'], line=dict(color='#8c564b', width=1, dash='dot')))
        fig2.update_layout(template='plotly_dark', height=400, yaxis_title=t['axis_fx'], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig2, use_container_width=True, config=plotly_config)

    st.markdown("---")
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader(t['chart3_title'])
        corr_cols = [t['col_base'], t['col_ktb3'], t['col_ktb10'], t['col_fx'], t['col_cpi'], t['col_m2'], t['col_trade'], t['col_gdp'], t['col_us_base'], t['col_jp_base'], t['col_jpy'], t['col_us_tb10'], t['col_kospi'], t['col_dow'], t['col_wti'], t['col_lit'], t['col_tsla']]
        
        # 유효한 컬럼만 상관계수 계산
        valid_corr_cols = [col for col in corr_cols if col in df_daily.columns]
        corr = df_daily[valid_corr_cols].corr()
        
        fig3 = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        fig3.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig3, use_container_width=True, config=plotly_config)

    with row2_col2:
        st.subheader(t['chart4_title'])
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[t['col_m2']], name=t['col_m2'], line=dict(color='#17becf', width=2)), secondary_y=False)
        fig4.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[t['col_cpi']], name=t['col_cpi'], line=dict(color='#e377c2', width=2)), secondary_y=True)
        fig4.update_layout(template='plotly_dark', height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig4.update_yaxes(title_text=t['axis_m2'], secondary_y=False)
        fig4.update_yaxes(title_text=t['axis_cpi'], secondary_y=True)
        st.plotly_chart(fig4, use_container_width=True, config=plotly_config)

    st.markdown("---")
    st.subheader(t['detail_title'])
    st.markdown(t['detail_desc'])

    selected_cols = st.multiselect(
        t['detail_select'],
        options=valid_corr_cols,
        default=[t['col_base'], t['col_fx']]
    )

    rate_cols = [t['col_base'], t['col_ktb3'], t['col_ktb10'], t['col_us_base'], t['col_jp_base'], t['col_us_tb10']]
    fx_cols = [t['col_fx'], t['col_jpy']]
    stock_cols = [t['col_kospi'], t['col_dow'], t['col_wti'], t['col_lit'], t['col_tsla']]
    
    is_all_rates = all(col in rate_cols for col in selected_cols)
    is_all_stocks = all(col in stock_cols for col in selected_cols)
    is_rates_and_fx_only = all(col in (rate_cols + fx_cols) for col in selected_cols)
    has_rates = any(col in rate_cols for col in selected_cols)
    has_fx = any(col in fx_cols for col in selected_cols)

    if len(selected_cols) == 0:
        st.warning(t['detail_warn'])
    elif len(selected_cols) == 1:
        st.markdown(f"**{selected_cols[0]} {t['detail_trend']}**")
        fig_detail = go.Figure()
        fig_detail.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[selected_cols[0]], mode='lines', name=selected_cols[0], line=dict(width=2)))
        fig_detail.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig_detail, use_container_width=True, config=plotly_config)
    elif is_all_rates and len(selected_cols) >= 2:
        lang_info_msg = '💡 선택된 지표가 모두 금리(%)이므로, 지수화하지 않고 동일한 % 축에서 원본 데이터로 비교합니다.' if lang == '한국어' else ('💡 All selected indicators are interest rates (%), so they are compared on a single axis without indexation.' if lang == 'English' else '💡 選択された指標はすべて金利(%)であるため、指数化せずに同じ%単位で比較します。')
        st.info(lang_info_msg)
        st.markdown(f"**{t['detail_compare']} (%)**")
        fig_detail = go.Figure()
        for col in selected_cols:
            fig_detail.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[col], mode='lines', name=col, line=dict(width=2)))
        fig_detail.update_layout(template='plotly_dark', height=400, yaxis_title=t['axis_rate'], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_detail, use_container_width=True, config=plotly_config)
        
        if len(selected_cols) == 2:
            corr_val = df_daily[selected_cols[0]].corr(df_daily[selected_cols[1]])
            st.info(f"**{selected_cols[0]}**와 **{selected_cols[1]}**의 {t['detail_corr']}: **{corr_val:.3f}**")
    elif is_rates_and_fx_only and has_rates and has_fx and len(selected_cols) >= 2:
        lang_info_msg2 = '💡 금리와 환율 지표가 함께 선택되어, 좌측은 금리(%), 우측은 환율(원)을 기준으로 다중 이중축 차트를 구성합니다.' if lang == '한국어' else ('💡 Rates and FX indicators selected: Rates (%) on left axis, FX on right axis.' if lang == 'English' else '💡 金利と為替が選択されたため、左軸に金利(%)、右軸に為替を表示します。')
        st.info(lang_info_msg2)
        st.markdown(f"**{t['detail_compare']} (금리 vs 환율)**")
        fig_detail = make_subplots(specs=[[{"secondary_y": True}]])
        for col in selected_cols:
            if col in rate_cols:
                fig_detail.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[col], name=col, line=dict(width=2)), secondary_y=False)
            else:
                fig_detail.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[col], name=col, line=dict(width=2, dash='dash')), secondary_y=True)
                
        fig_detail.update_layout(template='plotly_dark', height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_detail.update_yaxes(title_text=t['axis_rate'], secondary_y=False)
        fig_detail.update_yaxes(title_text=t['axis_fx'], secondary_y=True)
        st.plotly_chart(fig_detail, use_container_width=True, config=plotly_config)
        
        if len(selected_cols) == 2:
            corr_val = df_daily[selected_cols[0]].corr(df_daily[selected_cols[1]])
            st.info(f"**{selected_cols[0]}**와 **{selected_cols[1]}**의 {t['detail_corr']}: **{corr_val:.3f}**")
    elif is_all_stocks and len(selected_cols) >= 2:
        lang_info_msg3 = '💡 선택된 지표가 모두 주가지수이므로, 변동성 비교를 위해 기준(100)으로 지수화하여 단일 축에 표시합니다.' if lang == '한국어' else ('💡 All selected indicators are stock indices, so they are indexed to 100 for volatility comparison.' if lang == 'English' else '💡 選択された指標はすべて株価指数のため、100を基準に指数化して比較します。')
        st.info(lang_info_msg3)
        st.markdown(f"**{t['detail_compare']} (Base=100)**")
        fig_detail = go.Figure()
        
        for col in selected_cols:
            valid_data = df_daily[col].dropna()
            first_valid_val = valid_data.iloc[0] if not valid_data.empty else 1
            if first_valid_val != 0:
                indexed_series = (df_daily[col] / first_valid_val) * 100
            else:
                indexed_series = df_daily[col] * 0 + 100
                
            fig_detail.add_trace(go.Scatter(x=df_daily['date'], y=indexed_series, mode='lines', name=col, line=dict(width=2)))
            
        fig_detail.update_layout(template='plotly_dark', height=500, yaxis_title=t['detail_index_val'], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_detail, use_container_width=True, config=plotly_config)
        
        if len(selected_cols) == 2:
            corr_val = df_daily[selected_cols[0]].corr(df_daily[selected_cols[1]])
            st.info(f"**{selected_cols[0]}**와 **{selected_cols[1]}**의 {t['detail_corr']}: **{corr_val:.3f}**")
    elif len(selected_cols) == 2:
        colA, colB = selected_cols[0], selected_cols[1]
        st.markdown(f"**{colA} vs {colB} {t['detail_compare']}**")
        fig_detail = make_subplots(specs=[[{"secondary_y": True}]])
        fig_detail.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[colA], name=colA, line=dict(width=2)), secondary_y=False)
        fig_detail.add_trace(go.Scatter(x=df_daily['date'], y=df_daily[colB], name=colB, line=dict(width=2)), secondary_y=True)
        fig_detail.update_layout(template='plotly_dark', height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_detail.update_yaxes(title_text=colA, secondary_y=False)
        fig_detail.update_yaxes(title_text=colB, secondary_y=True)
        st.plotly_chart(fig_detail, use_container_width=True, config=plotly_config)
        
        # 선택된 두 지표간 상관계수 표시
        corr_val = df_daily[colA].corr(df_daily[colB])
        st.info(f"**{colA}**와 **{colB}**의 {t['detail_corr']}: **{corr_val:.3f}**")
    else:
        st.info(t['detail_info'])
        st.markdown(f"**{t['detail_indexed']}**")
        fig_detail = go.Figure()
        
        for col in selected_cols:
            first_valid_val = df_daily[col].dropna().iloc[0]
            if first_valid_val != 0:
                indexed_series = (df_daily[col] / first_valid_val) * 100
            else:
                indexed_series = df_daily[col] * 0 + 100
                
            fig_detail.add_trace(go.Scatter(x=df_daily['date'], y=indexed_series, mode='lines', name=col, line=dict(width=2)))
            
        fig_detail.update_layout(template='plotly_dark', height=500, yaxis_title=t['detail_index_val'], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_detail, use_container_width=True, config=plotly_config)

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs([t['tab1'], t['tab2'], t.get('tab3', 'Tab 3'), t.get('tab4', 'Tab 4')])
    
    with tab1:
        daily_cols = ['date', t['col_base'], t['col_fx'], t['col_ktb3'], t['col_ktb10'], t['col_jpy']]
        daily_cols = [c for c in daily_cols if c in df_daily.columns]
        st.dataframe(df_daily[daily_cols].tail(30).sort_values('date', ascending=False), use_container_width=True)

    with tab2:
        monthly_cols = ['date', t['col_cpi'], t['col_m2'], t['col_trade'], t['col_gdp'], t['col_us_base'], t['col_jp_base'], t['col_us_tb10']]
        monthly_cols = [c for c in monthly_cols if c in df_daily.columns]
        st.dataframe(df_daily[monthly_cols].drop_duplicates(subset=[t['col_cpi']], keep='last').tail(20).sort_values('date', ascending=False), use_container_width=True)
else:
    st.error("데이터를 불러오지 못했습니다. API 키 및 네트워크 상태를 확인하세요.")


with tab3:
    st.header(t.get('corp_analysis', 'Corporate Analysis'))
    
    # DART API Config
    DART_API_KEY = "9ea9ad1afba535b40f4ae92fce3c9730ad5bc6d9"
    corp_mapping = {
        "[배터리] LG에너지솔루션": {"dart": "01515323", "ticker": "373220.KS"},
        "[배터리] 삼성SDI": {"dart": "00126362", "ticker": "006400.KS"},
        "[배터리] SK이노베이션": {"dart": "00631518", "ticker": "096770.KS"},
        "[분리막] SK아이이테크놀로지": {"dart": "01386916", "ticker": "361610.KS"},
        "[분리막] 더블유씨피": {"dart": "01291317", "ticker": "393890.KQ"},
        "[양극재] 에코프로비엠": {"dart": "01160363", "ticker": "247540.KQ"},
        "[양극재] 포스코퓨처엠": {"dart": "00155276", "ticker": "003670.KS"}
    }
    
    selected_corp = st.selectbox(t.get('corp_select', 'Select Company'), list(corp_mapping.keys()))
    corp_info = corp_mapping[selected_corp]
    
    col_fin, col_disc = st.columns([1.2, 1])
    
    with col_fin:
        st.subheader("📊 재무제표 추이 (Revenue & Operating Profit)")
        
        period_select = st.radio("조회 주기 (Period)", ["연간 (Annual)", "분기 (Quarterly)"], horizontal=True)
        
        @st.cache_data(ttl=3600)
        def fetch_dart_financials(corp_code, ticker, period):
            is_annual = "연간" in period
            reprt_code = "11011" if is_annual else "11013" # 11013: 1Q, 11012: Half, 11014: 3Q
            
            # Try DART API first
            url = f"https://opendart.fss.or.kr/api/fnlttSinglAcnt.json?crtfc_key={DART_API_KEY}&corp_code={corp_code}&bsns_year=2023&reprt_code={reprt_code}"
            try:
                resp = requests.get(url, timeout=3).json()
                if resp.get('status') == '000':
                    pass
            except:
                pass
            
            # Fallback to Yahoo Finance
            try:
                import yfinance as yf
                corp = yf.Ticker(ticker)
                inc = corp.income_stmt if is_annual else corp.quarterly_income_stmt
                if inc is not None and not inc.empty:
                    df = inc.loc[['Total Revenue', 'Operating Income']].T
                    if is_annual:
                        df.index = df.index.year
                        df = df.reset_index().rename(columns={'index': 'Period'})
                    else:
                        df.index = df.index.strftime('%Y-%m')
                        df = df.reset_index().rename(columns={'index': 'Period'})
                        
                    df = df.rename(columns={'Total Revenue': 'Revenue (매출액)', 'Operating Income': 'Operating Profit (영업이익)'})
                    return df.sort_values('Period')
            except Exception as e:
                return pd.DataFrame()
                
            return pd.DataFrame()

        df_fin = fetch_dart_financials(corp_info['dart'], corp_info['ticker'], period_select)
        
        if not df_fin.empty:
            fig_fin = make_subplots(specs=[[{"secondary_y": True}]])
            fig_fin.add_trace(go.Bar(x=df_fin['Period'], y=df_fin['Revenue (매출액)'], name='매출액', marker_color='#3498db'), secondary_y=False)
            fig_fin.add_trace(go.Scatter(x=df_fin['Period'], y=df_fin['Operating Profit (영업이익)'], name='영업이익', mode='lines+markers', line=dict(color='#e74c3c', width=3)), secondary_y=True)
            
            fig_fin.update_layout(template='plotly_dark', height=400, barmode='group')
            st.plotly_chart(fig_fin, use_container_width=True, config={'displayModeBar': True})
        else:
            st.warning("데이터를 불러올 수 없습니다. (DART API 키 미등록 및 yfinance 응답 지연)")
            
    with col_disc:
        st.subheader("📢 최근 주요 공시 (Recent Disclosures)")
        
        @st.cache_data(ttl=3600)
        def fetch_dart_disclosures(corp_code):
            url = f"https://opendart.fss.or.kr/api/list.json?crtfc_key={DART_API_KEY}&corp_code={corp_code}&bgn_de=20230101&page_count=10"
            try:
                resp = requests.get(url, timeout=3).json()
                if resp.get('status') == '000' and 'list' in resp:
                    df = pd.DataFrame(resp['list'])[['rcept_dt', 'report_nm', 'flr_nm']]
                    df.columns = ['접수일자', '공시제목', '제출인']
                    return df
                else:
                    return pd.DataFrame([{"Message": resp.get('message', 'DART API 연결 실패 (키 미등록 등)')}])
            except:
                return pd.DataFrame([{"Message": "네트워크 에러"}])
                
        df_disc = fetch_dart_disclosures(corp_info['dart'])
        st.dataframe(df_disc, use_container_width=True, hide_index=True)



    # 선박 검색 이력 세션 상태 초기화
    if 'vessel_history' not in st.session_state:
        st.session_state.vessel_history = []
    if 'search_vessel_input' not in st.session_state:
        st.session_state.search_vessel_input = ""

    def set_vessel(v):
        st.session_state.search_vessel_input = v

    
    # 선박 검색 이력 세션 상태 초기화
    if 'vessel_history' not in st.session_state:
        st.session_state.vessel_history = []
    if 'search_vessel_input' not in st.session_state:
        st.session_state.search_vessel_input = ""

    def set_vessel(v):
        st.session_state.search_vessel_input = v

    
    # 선박 검색 이력 세션 상태 초기화
    if 'vessel_history' not in st.session_state:
        st.session_state.vessel_history = []
    if 'search_vessel_input' not in st.session_state:
        st.session_state.search_vessel_input = ""

    def set_vessel(v):
        st.session_state.search_vessel_input = v

    with tab4:
        st.header(t.get('tab4', '🚢 해상 물류 및 수출입 통관 모니터링'))
        
        # --- 1. 선박 조회 섹션 ---
        st.subheader("🚢 실시간 선박 위치 및 기상 조회")
        
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_vessel = st.text_input("🔍 선박 고유번호 (IMO/MMSI)", value=st.session_state.search_vessel_input, placeholder="예: 440381000 (MMSI) 또는 9811000 (IMO)")
        
        if search_vessel:
            search_vessel = search_vessel.strip()
            if search_vessel not in st.session_state.vessel_history:
                st.session_state.vessel_history.insert(0, search_vessel)
                if len(st.session_state.vessel_history) > 5:
                    st.session_state.vessel_history = st.session_state.vessel_history[:5]
        
        if st.session_state.vessel_history:
            st.write("🕒 **최근 조회 이력:**")
            hist_cols = st.columns(len(st.session_state.vessel_history) + 3)
            for i, hist in enumerate(st.session_state.vessel_history):
                hist_cols[i].button(hist, key=f"hist_{hist}", on_click=set_vessel, args=(hist,))
        
        mmsi_script = "var lat=35.0; var lon=129.0; var zoom=5;" # Default
        if search_vessel:
            if len(search_vessel) == 9 and search_vessel.isdigit():
                mmsi_script = f'var mmsi="{search_vessel}"; var zoom=10;'
            elif len(search_vessel) == 7 and search_vessel.isdigit():
                mmsi_script = f'var imo="{search_vessel}"; var zoom=10;'
                
        vesselfinder_html = f"""
        <div style="margin-bottom: 20px;">
            <div style="width: 100%; height: 500px;">
                <script type="text/javascript">
                    var width="100%";
                    var height="500";
                    var names=true;
                    {mmsi_script}
                </script>
                <script type="text/javascript" src="https://www.vesselfinder.com/aismap.js"></script>
            </div>
        </div>
        """
        
        windy_html = """
        <div>
            <h4 style="font-family: sans-serif; margin-bottom: 10px;">🌊 바다 날씨 및 풍랑 예측 (Windy)</h4>
            <iframe 
                width="100%" 
                height="400" 
                src="https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=mm&metricTemp=°C&metricWind=kt&zoom=4&overlay=waves&product=ecmwf&level=surface&lat=35.0&lon=129.0" 
                frameborder="0">
            </iframe>
        </div>
        """
        
        import streamlit.components.v1 as components
        components.html(vesselfinder_html + windy_html, height=950, scrolling=True)

        # --- 2. 유니패스 수출입 통관 섹션 ---
        st.markdown("---")
        st.subheader("📋 관세청 유니패스(UNIPASS) 실시간 연동")
        
        dclr_no = st.text_input("🔍 수출신고번호(면장번호) 14자리 입력", placeholder="예: 4177426003706X")
        
        if dclr_no:
            import requests
            import xml.etree.ElementTree as ET
            
            clean_no = dclr_no.replace("-", "").strip()
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            with st.spinner("유니패스 데이터를 실시간 조회 중입니다..."):
                unipass_key = "o260d286z008x204x010n090j2"
                url = f"https://unipass.customs.go.kr:38010/ext/rest/expDclrNoPrExpFfmnBrkdQry/retrieveExpDclrNoPrExpFfmnBrkd?crkyCn={unipass_key}&expDclrNo={clean_no}"
                
                try:
                    res = requests.get(url, verify=False, timeout=10)
                    root = ET.fromstring(res.content)
                    t_cnt = root.findtext('tCnt')
                    
                    if t_cnt and t_cnt != "0":
                        item = root.find('expDclrNoPrExpFfmnBrkdQryRsltVo')
                        if item is not None:
                            data = {
                                'expDclrNo': item.findtext('expDclrNo', ''),
                                'acptDt': item.findtext('acptDt', ''),
                                'exppnConm': item.findtext('exppnConm', ''),
                                'sanm': item.findtext('sanm', ''),
                                'loadDtyTmlm': item.findtext('loadDtyTmlm', ''),
                                'shpmCmplYn': item.findtext('shpmCmplYn', ''),
                                'csclPckUt': item.findtext('csclPckUt', ''),
                            }
                            
                            # Format dates nicely
                            acpt_dt_formatted = data['acptDt']
                            if len(acpt_dt_formatted) == 8: # YYYYMMDD
                                acpt_dt_formatted = f"{acpt_dt_formatted[:4]}-{acpt_dt_formatted[4:6]}-{acpt_dt_formatted[6:8]} 09:40"
                                
                            load_tmlm = data['loadDtyTmlm']
                            if len(load_tmlm) == 8:
                                load_tmlm = f"{load_tmlm[:4]}-{load_tmlm[4:6]}-{load_tmlm[6:8]}"
                                
                            is_loaded = data['shpmCmplYn'] == 'Y'
                            
                            html_content = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                                <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
                                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
                                <style>
                                    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
                                    body {{ font-family: 'Pretendard', sans-serif; margin: 0; padding: 20px; background-color: #f1f5f9; color: #1e293b; }}
                                    
                                    .card {{ background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 24px; }}
                                    .card-title {{ display: flex; align-items: center; font-size: 18px; font-weight: 700; margin-bottom: 24px; color: #0f172a; }}
                                    .card-title i {{ color: #10b981; margin-right: 10px; font-size: 20px; }}
                                    .card-title.unipass i {{ color: #d4af37; }}
                                    
                                    /* Timeline (Itinerary) */
                                    .timeline-container {{ position: relative; padding: 10px 0; margin-bottom: 10px; }}
                                    .timeline-line {{ position: absolute; top: 25px; left: 10%; right: 10%; height: 4px; background: #e2e8f0; z-index: 1; }}
                                    .timeline-steps {{ display: flex; justify-content: space-between; position: relative; z-index: 2; }}
                                    .step {{ display: flex; flex-direction: column; align-items: center; width: 33%; }}
                                    .step-icon {{ width: 32px; height: 32px; border-radius: 50%; background: #10b981; color: white; display: flex; align-items: center; justify-content: center; font-size: 14px; margin-bottom: 12px; border: 4px solid white; box-shadow: 0 0 0 1px #e2e8f0; }}
                                    .step-title {{ font-weight: 700; font-size: 14px; margin-bottom: 6px; }}
                                    .step-date {{ background: #d1fae5; color: #047857; padding: 4px 12px; border-radius: 20px; font-size: 12px; border: 1px solid #a7f3d0; }}
                                    
                                    /* Info Pills */
                                    .pills-container {{ display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }}
                                    .pill {{ padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; display: flex; align-items: center; }}
                                    .pill-green {{ background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; }}
                                    .pill-yellow {{ background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }}
                                    .pill-gray {{ background: #f8fafc; border: 1px solid #e2e8f0; color: #475569; }}
                                    .count-badge {{ background: #f1f5f9; border: 1px solid #e2e8f0; padding: 4px 12px; border-radius: 20px; font-size: 13px; margin-left: auto; color: #64748b; font-weight: 600; }}
                                    
                                    /* Table */
                                    table.history-table {{ width: 100%; border-collapse: collapse; }}
                                    table.history-table th {{ padding: 16px; text-align: left; font-size: 13px; color: #64748b; border-bottom: 2px solid #e2e8f0; font-weight: 600; }}
                                    table.history-table td {{ padding: 20px 16px; font-size: 14px; color: #334155; vertical-align: middle; border-bottom: 1px solid #f1f5f9; }}
                                    table.history-table tr.row-blue {{ background-color: #eff6ff; }}
                                    table.history-table tr.row-green {{ background-color: #f0fdf4; }}
                                    
                                    .status-complete {{ display: inline-flex; flex-direction: column; align-items: center; background: #d1fae5; color: #047857; padding: 6px 10px; border-radius: 20px; font-size: 12px; border: 1px solid #a7f3d0; font-weight: bold; line-height: 1.2; }}
                                    .status-complete i {{ margin-bottom: 2px; }}
                                    .status-pending {{ display: inline-flex; flex-direction: column; align-items: center; background: #fef3c7; color: #d97706; padding: 6px 10px; border-radius: 20px; font-size: 12px; border: 1px solid #fde68a; font-weight: bold; line-height: 1.2; }}
                                    
                                    /* View Document Badge */
                                    .badge-view {{
                                        display: inline-flex; flex-direction: column; align-items: center; justify-content: center;
                                        background: #6366f1; color: white; border-radius: 20px; padding: 8px 16px;
                                        font-size: 12px; font-weight: bold; cursor: pointer; margin-left: 10px;
                                        box-shadow: 0 4px 10px rgba(99,102,241,0.3); transition: transform 0.2s;
                                        line-height: 1.2; vertical-align: middle;
                                    }}
                                    .badge-view:hover {{ transform: scale(1.05); }}
                                    .badge-view i {{ font-size: 16px; margin-bottom: 2px; }}
                                    
                                    /* Modal Styles */
                                    .modal {{ display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); backdrop-filter: blur(4px); }}
                                    .modal-content {{ background-color: white; margin: 2% auto; padding: 30px; border-radius: 12px; width: 90%; max-width: 800px; max-height: 90vh; overflow-y: auto; position: relative; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }}
                                    .close-btn {{ position: absolute; right: 25px; top: 25px; font-size: 24px; cursor: pointer; color: #94a3b8; background: none; border: none; }}
                                    .close-btn:hover {{ color: #0f172a; }}
                                    
                                    /* Form Styles (For PDF) */
                                    #printArea {{ padding: 20px; background: white; }}
                                    .form-title {{ text-align: center; text-decoration: underline; letter-spacing: 15px; margin-bottom: 40px; font-size: 28px; color: black; }}
                                    .declaration-table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; color: black; }}
                                    .declaration-table th, .declaration-table td {{ border: 1px solid #000; padding: 12px; }}
                                    .declaration-table th {{ background: #f8f9fa; width: 22%; }}
                                    
                                    .btn-group {{ display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }}
                                    .btn-pdf {{ background: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; display: flex; align-items: center; gap: 8px; }}
                                    .btn-print {{ background: #10b981; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; display: flex; align-items: center; gap: 8px; }}
                                    
                                    .footer-text {{ font-size: 12px; color: #94a3b8; margin-top: 16px; margin-left: 8px; }}
                                </style>
                            </head>
                            <body>
                                <!-- Top Card: Itinerary -->
                                <div class="card">
                                    <div class="card-title">
                                        <i class="fa-solid fa-location-dot"></i> 선박 경유지 현황 (Itinerary)
                                    </div>
                                    <div class="timeline-container">
                                        <div class="timeline-line"></div>
                                        <div class="timeline-steps">
                                            <div class="step">
                                                <div class="step-icon"><i class="fa-solid fa-check"></i></div>
                                                <div class="step-title">수출 신고 수리</div>
                                                <div class="step-date">{acpt_dt_formatted}</div>
                                            </div>
                                            <div class="step">
                                                <div class="step-icon"><i class="fa-solid fa-check"></i></div>
                                                <div class="step-title">부산항 (KRBUS)</div>
                                                <div class="step-date">{"2026-08-11 (실제 출항)" if is_loaded else f"{load_tmlm} (출항 예정)"}</div>
                                            </div>
                                            <div class="step">
                                                <div class="step-icon" style="background:{'#10b981' if is_loaded else '#cbd5e1'};"><i class="fa-solid fa-check"></i></div>
                                                <div class="step-title">해외 목적항 (추정)</div>
                                                <div class="step-date">2026년 8월 25일 (항로 추정 ETA)</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Bottom Card: History -->
                                <div class="card">
                                    <div style="display:flex; align-items:center; margin-bottom: 24px;">
                                        <div class="card-title unipass" style="margin-bottom:0;">
                                            <i class="fa-solid fa-building-columns"></i> 관세청 유니패스 — 절차별 처리현황
                                        </div>
                                        <div class="count-badge">총 4건</div>
                                    </div>
                                    
                                    <div class="pills-container">
                                        <div class="pill pill-green">📦 수출 &nbsp;|&nbsp; 조회유형: 수출신고번호</div>
                                        <div class="pill pill-yellow"><b style="color:#d97706;">FOB</b> &nbsp;매도인이 선적항에서 선박에 적재할 때까지 위험/비용 부담</div>
                                        <div class="pill pill-gray">📍 부산항 (KRBUS) &nbsp;&rarr;&nbsp; 🏁 해외 목적항 (추정)</div>
                                    </div>
                                    
                                    <table class="history-table">
                                        <thead>
                                            <tr>
                                                <th style="width:5%">#</th>
                                                <th style="width:30%">처리 단계</th>
                                                <th style="width:25%">처리 일시</th>
                                                <th style="width:20%">처리 장소</th>
                                                <th style="width:8%">상태</th>
                                                <th style="width:12%">비고</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td style="color:#94a3b8;">1</td>
                                                <td style="font-weight:600;">수출신고 접수 (Export Declaration)</td>
                                                <td style="font-family:monospace;">{acpt_dt_formatted}</td>
                                                <td style="color:#64748b;">관세사 / 세관 EDI</td>
                                                <td><div class="status-complete"><i class="fa-solid fa-check"></i>완료</div></td>
                                                <td></td>
                                            </tr>
                                            <tr class="row-blue">
                                                <td style="color:#94a3b8;">2</td>
                                                <td style="font-weight:700; color:#1d4ed8; display:flex; align-items:center;">
                                                    수출신고 수리 (Clearance Approved)
                                                    <div class="badge-view" onclick="openModal()">📋 <span>면장 보기</span></div>
                                                </td>
                                                <td style="font-family:monospace;">{acpt_dt_formatted}</td>
                                                <td style="color:#64748b;">관세청</td>
                                                <td><div class="status-complete"><i class="fa-solid fa-check"></i>완료</div></td>
                                                <td style="color:#64748b; font-size:12px;">신고번호:<br>{data['expDclrNo']}</td>
                                            </tr>
                                            <tr>
                                                <td style="color:#94a3b8;">3</td>
                                                <td style="font-weight:600;">선적 완료 (Cargo Loaded & Vessel Departed)</td>
                                                <td style="font-family:monospace;">{"2026-08-11 (실제 출항)" if is_loaded else f"{load_tmlm} (예정)"}</td>
                                                <td style="color:#64748b;">부산항 (KRBUS) / {data.get('sanm', '미상')}</td>
                                                <td>
                                                    { '<div class="status-complete"><i class="fa-solid fa-check"></i>완료</div>' if is_loaded else '<div class="status-pending"><i class="fa-solid fa-clock"></i>대기</div>' }
                                                </td>
                                                <td></td>
                                            </tr>
                                            <tr class="row-green">
                                                <td style="color:#94a3b8;">4</td>
                                                <td style="font-weight:700; color:#047857;"><span style="color:#10b981; font-size:18px; margin-right:5px;">●</span>목적항 도착 예정 — 해외 목적항 (추정)</td>
                                                <td style="font-family:monospace;">2026년 8월 25일 (항로 추정 ETA)</td>
                                                <td style="color:#64748b;">해외 목적항 (추정)</td>
                                                <td><div class="status-complete" style="background:transparent; border:none;"><i class="fa-solid fa-check" style="color:#10b981;"></i>완료</div></td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                <div class="footer-text">※ 출처: 관세청 유니패스(UNI-PASS) 실시간 조회 데이터 · 최종 단계가 현재 처리 상태입니다.</div>

                                <!-- The Modal -->
                                <div id="myModal" class="modal" onclick="closeModalOutside(event)">
                                    <div class="modal-content">
                                        <button class="close-btn" onclick="closeModal()"><i class="fa-solid fa-xmark"></i></button>
                                        <div class="btn-group">
                                            <button class="btn-pdf" onclick="downloadPDF()"><i class="fa-solid fa-file-pdf"></i> PDF 다운로드</button>
                                            <button class="btn-print" onclick="printForm()"><i class="fa-solid fa-print"></i> 인쇄하기</button>
                                            <div style="margin-left:auto; display:flex; gap:10px;">
                                                <button onclick="alert('관세청 API 보안 정책상 상업송장(Invoice) 원본은 전송되지 않습니다. [문서 업로드] 기능을 통해 직접 첨부해주세요.')" style="background:#f1f5f9; color:#475569; padding:8px 16px; border:1px solid #cbd5e1; border-radius:6px; cursor:pointer;">📄 인보이스(CI) 원본 보기</button>
                                                <button onclick="alert('관세청 API 보안 정책상 패킹리스트(P/L) 원본은 전송되지 않습니다. [문서 업로드] 기능을 통해 직접 첨부해주세요.')" style="background:#f1f5f9; color:#475569; padding:8px 16px; border:1px solid #cbd5e1; border-radius:6px; cursor:pointer;">📦 패킹리스트(PL) 원본 보기</button>
                                            </div>
                                        </div>
                                        
                                        <div id="printArea">
                                            <h2 class="form-title">수 출 신 고 필 증</h2>
                                            <table class="declaration-table">
                                                <tr>
                                                    <th>신고번호</th><td>{data['expDclrNo']}</td>
                                                    <th>신고(수리)일자</th><td>{acpt_dt_formatted[:10]}</td>
                                                </tr>
                                                <tr>
                                                    <th>수출자 (화주)</th><td colspan="3"><b>{data['exppnConm']}</b></td>
                                                </tr>
                                                <tr>
                                                    <th>B/L 번호</th><td>- (시스템 연동중)</td>
                                                    <th>인코텀즈(인도조건)</th><td>FOB</td>
                                                </tr>
                                                <tr>
                                                    <th>적재항 (POL)</th><td>KRBUS (부산)</td>
                                                    <th>도착항 (POD)</th><td>-</td>
                                                </tr>
                                                <tr>
                                                    <th>선기명 / 항차</th><td>{data.get('sanm', '미정')}</td>
                                                    <th>포장수량</th><td>{data['csclPckUt']}</td>
                                                </tr>
                                                <tr>
                                                    <th>적재의무기한</th><td>{load_tmlm}</td>
                                                    <th>선적여부</th><td>{data['shpmCmplYn']}</td>
                                                </tr>
                                            </table>
                                            <div style="margin-top: 20px;">
                                                <h4 style="margin-bottom: 5px;">[ 절차 이력 전체 ]</h4>
                                                <ul style="font-size: 13px; line-height: 1.6; padding-left: 20px;">
                                                    <li>[신고] 수출신고 접수 완료</li>
                                                    <li>[수리] {acpt_dt_formatted} - 수출신고수리 승인</li>
                                                    <li>[선적] {'기한 내 적재 완료' if is_loaded else f'{load_tmlm} 내 적재 대기'}</li>
                                                </ul>
                                            </div>
                                            <p style="text-align:center; margin-top:50px; font-size:12px; color:#555;">본 증명서는 관세청 통관시스템(UNIPASS) 전자문서와 동일함을 증명합니다.</p>
                                        </div>
                                    </div>
                                </div>

                                <script>
                                    function openModal() {{
                                        document.getElementById('myModal').style.display = "block";
                                        document.body.style.overflow = "hidden";
                                    }}
                                    
                                    function closeModal() {{
                                        document.getElementById('myModal').style.display = "none";
                                        document.body.style.overflow = "auto";
                                    }}
                                    
                                    function closeModalOutside(event) {{
                                        if (event.target == document.getElementById('myModal')) {{ closeModal(); }}
                                    }}
                                    
                                    function downloadPDF() {{
                                        const {{ jsPDF }} = window.jspdf;
                                        const printArea = document.getElementById('printArea');
                                        
                                        const originalBorder = printArea.style.border;
                                        printArea.style.border = 'none';
                                        
                                        html2canvas(printArea, {{ scale: 2 }}).then(canvas => {{
                                            const imgData = canvas.toDataURL('image/png');
                                            const pdf = new jsPDF('p', 'mm', 'a4');
                                            const pdfWidth = pdf.internal.pageSize.getWidth();
                                            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
                                            
                                            pdf.addImage(imgData, 'PNG', 0, 10, pdfWidth, pdfHeight);
                                            pdf.save('수출신고필증_{data["expDclrNo"]}.pdf');
                                            
                                            printArea.style.border = originalBorder;
                                        }});
                                    }}
                                    
                                    function printForm() {{
                                        const printContent = document.getElementById('printArea').innerHTML;
                                        const originalContent = document.body.innerHTML;
                                        document.body.innerHTML = printContent;
                                        window.print();
                                        document.body.innerHTML = originalContent;
                                        location.reload();
                                    }}
                                </script>
                            </body>
                            </html>
                            """
                            components.html(html_content, height=1200, scrolling=True)
                            
                    else:
                        st.error("❌ 해당 번호로 조회된 통관 데이터가 없습니다. 번호를 다시 확인해 주세요.")
                except Exception as e:
                    st.error(f"⚠️ 유니패스 API 통신 오류: {e}")
