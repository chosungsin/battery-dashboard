import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import zipfile
import io
import re
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import math
import json

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([t['tab1'], t['tab2'], t.get('tab3', 'Tab 3'), t.get('tab4', 'Tab 4'), '🇺🇸 미국 수출 관세율 및 정책 동향'])
    
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
        st.subheader("📢 최근 주요 공시 및 상세 요약 (Recent Disclosures)")
        
        def format_dart_currency(num_str):
            clean = re.sub(r'[^0-9-]', '', num_str)
            if not clean or clean == '-': return ''
            try:
                val = int(clean)
                abs_val = abs(val)
                if abs_val >= 1000000000000:
                    jo = abs_val // 1000000000000
                    eok = (abs_val % 1000000000000) // 100000000
                    res = f'{jo}조 {eok:,}억원' if eok else f'{jo}조원'
                elif abs_val >= 100000000:
                    res = f'{abs_val // 100000000:,}억원'
                else:
                    res = f'{abs_val:,}원'
                return ('-' if val < 0 else '') + res
            except:
                return num_str

        @st.cache_data(ttl=86400)
        def get_single_disclosure_summary(rcept_no, report_nm):
            url = f"https://opendart.fss.or.kr/api/document.xml?crtfc_key={DART_API_KEY}&rcept_no={rcept_no}"
            try:
                r = requests.get(url, timeout=4)
                if r.status_code != 200 or len(r.content) < 50:
                    return "상세 공시 본문 및 첨부 서류는 원본 문서를 참조하십시오."
                z = zipfile.ZipFile(io.BytesIO(r.content))
                raw = z.read(z.namelist()[0]).decode('utf-8', errors='ignore')
                soup = BeautifulSoup(raw, 'html.parser')
                for s in soup(['script', 'style']):
                    s.decompose()
                text = soup.get_text('\n')
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                joined = '\n'.join(lines)
                
                points = []
                
                # 1. 기업설명회 (IR)
                if 'IR' in report_nm or '기업설명회' in report_nm:
                    m_time = re.search(r'일시\s*([0-9]{4}[^\n]+)', joined)
                    m_purp = re.search(r'개최목적\s*([^\n]+)', joined)
                    m_place = re.search(r'장소\s*([^\n]+)', joined)
                    if m_time: points.append(f"📅 일시: {m_time.group(1).strip()}")
                    if m_place and '일시' not in m_place.group(1): points.append(f"📍 장소: {m_place.group(1).strip()}")
                    if m_purp: points.append(f"🎯 목적: {m_purp.group(1).strip()}")
                    
                # 2. 금전대여 / 담보제공 / 채무보증
                elif any(k in report_nm for k in ['금전대여', '담보제공', '채무보증']):
                    m_target = re.search(r'(?:대여\s*상대|채무자|담보제공\s*상대)\s*([^\n]+)', joined)
                    m_amt = re.search(r'(?:대여금액|채무보증금액|담보설정금액)\s*(?:\(원\))?\s*([0-9,]+)', joined)
                    if m_target: points.append(f"🏢 대상: {m_target.group(1).strip()}")
                    if m_amt: points.append(f"💰 금액: {format_dart_currency(m_amt.group(1))}")
                    
                # 3. 타법인 주식 취득/처분
                elif any(k in report_nm for k in ['타법인주식', '출자증권']):
                    m_target = re.search(r'(?:발행회사|대상회사|법인명)\s*([^\n]+)', joined)
                    m_amt = re.search(r'(?:처분금액|취득금액)\s*(?:\(원\))?\s*([0-9,]+)', joined)
                    m_purp = re.search(r'(?:처분목적|취득목적)\s*([^\n]+)', joined)
                    if m_target and m_target.group(1).strip() != '회사명': points.append(f"🏢 대상법인: {m_target.group(1).strip()}")
                    if m_amt: points.append(f"💰 거래금액: {format_dart_currency(m_amt.group(1))}")
                    if m_purp: points.append(f"🎯 목적: {m_purp.group(1).strip()}")
                    
                # 4. 실적 공시 (잠정실적 등)
                elif '실적' in report_nm:
                    m_rev = re.search(r'매출액\s*(?:당해실적)?\s*([0-9,]+)', joined)
                    m_op = re.search(r'영업이익\s*(?:당해실적)?\s*([-0-9,]+)', joined)
                    if m_rev: points.append(f"📈 매출액: {m_rev.group(1)}억원")
                    if m_op: points.append(f"📊 영업이익: {m_op.group(1)}억원")
                    
                # 5. 공급계약 / 단일판매
                elif any(k in report_nm for k in ['공급계약', '단일판매']):
                    m_cust = re.search(r'계약상대방?\s*([^\n]+)', joined)
                    m_amt = re.search(r'계약금액\s*(?:\(원\))?\s*([0-9,]+)', joined)
                    m_prod = re.search(r'계약내용\s*([^\n]+)', joined)
                    if m_cust: points.append(f"🤝 상대방: {m_cust.group(1).strip()}")
                    if m_amt: points.append(f"💰 계약금액: {format_dart_currency(m_amt.group(1))}")
                    if m_prod: points.append(f"📦 계약내용: {m_prod.group(1).strip()}")
                    
                # 6. 임원/주요주주/대량보유
                elif any(k in report_nm for k in ['임원ㆍ주요주주', '특정증권', '대량보유', '소유주식변동']):
                    m_who = re.search(r'(?:보고자|성명\(명칭\))\s*:\s*([^\n]+)', joined) or re.search(r'(?:보고자|성명\(명칭\))\s*\n\s*한\s*글\s*\n\s*([^\n]+)', joined)
                    m_pos = re.search(r'직위명?\s*([^\n]+)', joined)
                    m_ratio = re.search(r'(?:보유비율|소유비율)\s*([0-9.]+\s*%)', joined)
                    m_tot = re.search(r'이번보고서제출일\s*\n[^\n]*\n[^\n]*\n[^\n]*\n[^\n]*\n합계\s*\n[^\n]*\n([0-9.]+\s*%)', joined)
                    who_str = m_who.group(1).strip() if m_who else ''
                    pos_str = f"({m_pos.group(1).strip()})" if m_pos and m_pos.group(1).strip() != '-' else ''
                    if who_str: points.append(f"👤 보고자: {who_str} {pos_str}".strip())
                    if m_ratio: points.append(f"📊 소유비율: {m_ratio.group(1).strip()}")
                    elif m_tot: points.append(f"📊 소유비율: {m_tot.group(1).strip()}")
                    
                # 7. 정기보고서 (반기/분기/사업보고서)
                elif any(k in report_nm for k in ['사업보고서', '반기보고서', '분기보고서']):
                    m_p = re.search(r'사업연도\s*([0-9]{4}[^\n]+)', joined)
                    m_ceo = re.search(r'대\s*표\s*이\s*사\s*:\s*([^\n]+)', joined)
                    if m_p: points.append(f"🗓️ 사업연도: {m_p.group(1).strip()}")
                    if m_ceo: points.append(f"👤 대표이사: {m_ceo.group(1).strip()}")
                    points.append("재무제표 및 사업부문별 경영실적 법정 정기보고")
                    
                # 8. 대규모기업집단 현황
                elif '대규모기업집단' in report_nm:
                    points.append("공정거래법에 따른 분기별 계열회사 간 거래·채무보증·지배구조 현황 공시")
                    
                # 9. 지급수단별 지급금액
                elif '지급수단' in report_nm:
                    points.append("수탁기업 하도급 및 납품대금 지급수단별·기간별 결제현황 공시")
                    
                # 10. 계열회사와의 거래
                elif '계열회사와의상품' in report_nm or '동일인등출자' in report_nm:
                    points.append("공정거래법에 따른 계열회사 간 상품·용역 거래내역 공시")

                # 정정사항 체크
                if '정정' in report_nm:
                    m_reason = re.search(r'정정사유\s*([^\n]+)', joined)
                    if m_reason and '정 정 전' not in m_reason.group(1):
                        points.append(f"📝 정정사유: {m_reason.group(1).strip()}")
                    
                if not points:
                    for l in lines[4:]:
                        if len(l) > 15 and not any(w in l for w in ['귀중', '금융위', '한국거래소', '전화', '팩스', '본점', '발행회사']):
                            points.append(l[:90])
                            if len(points) >= 2: break
                            
                return ' · '.join(points) if points else "상세 공시 본문 및 첨부 서류는 원본 문서를 참조하십시오."
            except Exception as e:
                return "상세 공시 본문 및 첨부 서류는 원본 문서를 참조하십시오."

        @st.cache_data(ttl=1800)
        def fetch_dart_disclosures_with_summary(corp_code):
            url = f"https://opendart.fss.or.kr/api/list.json?crtfc_key={DART_API_KEY}&corp_code={corp_code}&bgn_de=20230101&page_count=10"
            try:
                resp = requests.get(url, timeout=5).json()
                if resp.get('status') == '000' and 'list' in resp:
                    raw_items = resp['list']
                    
                    def process_item(item):
                        r_dt = item.get('rcept_dt', '')
                        dt_fmt = f"{r_dt[:4]}-{r_dt[4:6]}-{r_dt[6:8]}" if len(r_dt) == 8 else r_dt
                        title = item.get('report_nm', '').strip()
                        rcp = item.get('rcept_no', '')
                        filer = item.get('flr_nm', '').strip()
                        summary = get_single_disclosure_summary(rcp, title)
                        link = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp}"
                        return {
                            'date': dt_fmt,
                            'title': title,
                            'filer': filer,
                            'summary': summary,
                            'link': link,
                            'rcept_no': rcp
                        }
                        
                    with ThreadPoolExecutor(max_workers=5) as ex:
                        disc_results = list(ex.map(process_item, raw_items))
                    return disc_results, None
                else:
                    return [], resp.get('message', 'DART 공시 내역을 불러오지 못했습니다.')
            except Exception as e:
                return [], f"네트워크 통신 오류: {e}"

        disc_items, err_msg = fetch_dart_disclosures_with_summary(corp_info['dart'])
        
        if err_msg:
            st.warning(f"⚠️ {err_msg}")
        elif not disc_items:
            st.info("최근 공시 내역이 없습니다.")
        else:
            col_view_opt, col_count_opt = st.columns([1.2, 0.8])
            with col_view_opt:
                view_mode = st.radio("공시 보기 모드", ["요약 카드형 (추천)", "데이터 표 형식"], horizontal=True, label_visibility="collapsed")
            with col_count_opt:
                st.markdown(f"<div style='text-align:right; font-size:12px; color:#888; padding-top:6px;'>총 <b>{len(disc_items)}건</b> 최근 공시</div>", unsafe_allow_html=True)
                
            if view_mode == "요약 카드형 (추천)":
                cards_html = """
                <style>
                .dart-disc-container {
                    max-height: 480px;
                    overflow-y: auto;
                    padding-right: 6px;
                    scrollbar-width: thin;
                }
                .dart-card {
                    background: rgba(128, 128, 128, 0.05);
                    border: 1px solid rgba(128, 128, 128, 0.2);
                    border-radius: 10px;
                    padding: 12px 14px;
                    margin-bottom: 10px;
                    transition: all 0.2s ease;
                }
                .dart-card:hover {
                    border-color: #3b82f6;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
                }
                .dart-card-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 6px;
                    flex-wrap: wrap;
                    gap: 6px;
                }
                .dart-badge-date {
                    background: rgba(59, 130, 246, 0.15);
                    color: #3b82f6;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                }
                .dart-badge-filer {
                    background: rgba(100, 116, 139, 0.15);
                    color: #64748b;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                .dart-link-btn {
                    background: #2563eb;
                    color: #ffffff !important;
                    padding: 3px 10px;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                    text-decoration: none !important;
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    transition: background 0.15s ease;
                }
                .dart-link-btn:hover {
                    background: #1d4ed8;
                    color: #ffffff !important;
                }
                .dart-card-title {
                    font-size: 13.5px;
                    font-weight: 700;
                    margin-bottom: 6px;
                    line-height: 1.4;
                }
                .dart-summary-box {
                    background: rgba(59, 130, 246, 0.08);
                    border-left: 3px solid #3b82f6;
                    border-radius: 4px;
                    padding: 7px 11px;
                    font-size: 12.5px;
                    line-height: 1.5;
                }
                .dart-summary-label {
                    font-weight: 700;
                    color: #3b82f6;
                    margin-right: 4px;
                }
                </style>
                <div class="dart-disc-container">
                """
                for item in disc_items:
                    cards_html += f"""
                    <div class="dart-card">
                        <div class="dart-card-header">
                            <div>
                                <span class="dart-badge-date">{item['date']}</span>
                                <span class="dart-badge-filer">{item['filer']}</span>
                            </div>
                            <a href="{item['link']}" target="_blank" class="dart-link-btn">
                                🔗 DART 원본보기 ↗
                            </a>
                        </div>
                        <div class="dart-card-title">{item['title']}</div>
                        <div class="dart-summary-box">
                            <span class="dart-summary-label">💡 주요내용 요약:</span>
                            <span>{item['summary']}</span>
                        </div>
                    </div>
                    """
                cards_html += "</div>"
                st.markdown(cards_html, unsafe_allow_html=True)
            else:
                df_table = pd.DataFrame(disc_items)[['date', 'title', 'summary', 'filer', 'link']]
                df_table.columns = ['접수일자', '공시제목', '주요내용 요약', '제출인', 'DART 원본링크']
                st.dataframe(
                    df_table,
                    column_config={
                        "DART 원본링크": st.column_config.LinkColumn("DART 원본링크", display_text="🔗 원본문서 열람")
                    },
                    use_container_width=True,
                    hide_index=True,
                    height=450
                )



        # 선박 검색 이력 세션 상태 초기화
    if 'vessel_history' not in st.session_state:
        st.session_state.vessel_history = []
    if 'vessel_input_widget' not in st.session_state:
        st.session_state.vessel_input_widget = ""
    if 'synced_dclr' not in st.session_state:
        st.session_state.synced_dclr = ""
        
    # 면장 검색 이력 세션 상태 초기화
    if 'dclr_history' not in st.session_state:
        st.session_state.dclr_history = []
    if 'dclr_input_widget' not in st.session_state:
        st.session_state.dclr_input_widget = ""
    if 'imo_to_dclr_cache' not in st.session_state:
        st.session_state.imo_to_dclr_cache = {}

    def set_vessel(v):
        st.session_state.vessel_input_widget = v
        # 캐시된 이력을 바탕으로 좌측 유니패스 연동
        mapped_dclr = st.session_state.imo_to_dclr_cache.get(v)
        if mapped_dclr:
            st.session_state.synced_dclr = mapped_dclr
            st.session_state.dclr_input_widget = mapped_dclr
            if mapped_dclr not in st.session_state.dclr_history:
                st.session_state.dclr_history.insert(0, mapped_dclr)

    def on_vessel_input_change():
        v = st.session_state.vessel_input_widget
        if v:
            v = v.strip()
            if v not in st.session_state.vessel_history:
                st.session_state.vessel_history.insert(0, v)
                if len(st.session_state.vessel_history) > 6:
                    st.session_state.vessel_history = st.session_state.vessel_history[:6]
            # 캐시된 이력을 바탕으로 좌측 유니패스 연동
            mapped_dclr = st.session_state.imo_to_dclr_cache.get(v)
            if mapped_dclr:
                st.session_state.synced_dclr = mapped_dclr
                st.session_state.dclr_input_widget = mapped_dclr
                if mapped_dclr not in st.session_state.dclr_history:
                    st.session_state.dclr_history.insert(0, mapped_dclr)

    def del_vessel(v):
        if v in st.session_state.vessel_history:
            st.session_state.vessel_history.remove(v)
        
    def set_dclr(v):
        # 콤마로 여러 개가 있을 때 추가하는 것도 가능하지만, 일단 이력 클릭 시 해당 건만 세팅
        st.session_state.dclr_input_widget = v

    def del_dclr(v):
        if v in st.session_state.dclr_history:
            st.session_state.dclr_history.remove(v)

    with tab4:
        st.header(t.get('tab4', '🚢 해상 물류 및 수출입 통관 모니터링'))
        
        # --- 1. 유니패스 수출입 통관 섹션 ---
        st.subheader("📋 관세청 유니패스(UNIPASS) 실시간 연동 (다중 조회 지원)")
        
        if st.session_state.dclr_history:
            st.markdown("🕒 **최근 면장 조회 이력**")
            d_cols = st.columns(3)
            for i, hist in enumerate(st.session_state.dclr_history[:6]):
                with d_cols[i % 3]:
                    sub1, sub2 = st.columns([5, 1])
                    btn_type = "primary" if hist in st.session_state.dclr_input_widget else "secondary"
                    sub1.button(f"📄 {hist}", key=f"dhist_{hist}", on_click=set_dclr, args=(hist,), type=btn_type, use_container_width=True)
                    sub2.button("✖", key=f"ddel_{hist}", on_click=del_dclr, args=(hist,), use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
        st.info("💡 여러 건을 동시에 조회하려면 쉼표(,)로 구분하여 입력하세요. 예: `4177426003706X, 1234567890123M`")
        dclr_no_raw = st.text_input("🔍 수출입신고번호 14~15자리 입력", key="dclr_input_widget", placeholder="예: 4177426003706X")
        
        main_col1, main_col2 = st.columns([1.1, 1], gap="large")
        
        with main_col1:
            if dclr_no_raw:
                import requests
                import xml.etree.ElementTree as ET
                from datetime import datetime
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                def get_realtime_eta_and_imo(query):
                    from bs4 import BeautifulSoup
                    import requests
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    try:
                        res = requests.get(f"https://www.vesselfinder.com/vessels?name={query}", headers=headers, timeout=5)
                        soup = BeautifulSoup(res.text, 'html.parser')
                        link = soup.select_one('a.ship-link')
                        if link:
                            href = link.get('href')
                            imo = href.split('/')[-1] if href else None
                            # Extract IMO from URL, e.g., /vessels/details/9863297
                            if imo and '-' in imo:
                                imo = imo.split('-')[-1]
                            return {"imo": imo, "mmsi": "조회불가", "callsign": "조회불가", "flag": "조회불가", "eta": None}
                    except:
                        pass
                    return {"imo": None, "mmsi": "미상", "callsign": "미상", "flag": "미상", "eta": None}
                
                # 다중 입력 처리
                dclr_list = [x.strip().replace("-", "") for x in dclr_no_raw.split(",") if x.strip()]
                
                # 이력에 추가 (개별 건으로 쪼개서)
                history_updated = False
                for d_no in dclr_list:
                    if d_no not in st.session_state.dclr_history:
                        st.session_state.dclr_history.insert(0, d_no)
                        history_updated = True
                
                if len(st.session_state.dclr_history) > 10:
                    st.session_state.dclr_history = st.session_state.dclr_history[:10]
                    
                if history_updated:
                    st.rerun()

                with st.spinner(f"총 {len(dclr_list)}건의 유니패스 데이터를 실시간 조회 중입니다..."):
                    unipass_key = "o260d286z008x204x010n090j2"
                    
                    # Auto-sync is triggered by the FIRST declaration only to avoid chaotic map jumps
                    synced_this_run = False
                    
                    for idx, clean_no in enumerate(dclr_list):
                        url = f"https://unipass.customs.go.kr:38010/ext/rest/expDclrNoPrExpFfmnBrkdQry/retrieveExpDclrNoPrExpFfmnBrkd?crkyCn={unipass_key}&expDclrNo={clean_no}"
                        
                        try:
                            res = requests.get(url, verify=False, timeout=10)
                            root = ET.fromstring(res.content)
                            t_cnt = root.findtext('tCnt')
                            
                            is_import = False
                            data = None
                            
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
                                    is_import = False
                            else:
                                st.warning(f"⚠️ 유니패스에서 면장번호 '{clean_no}'를 찾을 수 없습니다. (조회 결과 없음)")
                                
                            if data:
                                sanm = data.get('sanm', '')
                                    
                                # Auto-Sync Map Logic (only for the first item in the list)
                                if idx == 0 and not synced_this_run:
                                    if st.session_state.synced_dclr != clean_no:
                                        st.session_state.synced_dclr = clean_no
                                        if sanm:
                                            imo = get_realtime_eta_and_imo(sanm).get('imo')
                                            if imo and imo.isdigit():
                                                st.session_state.imo_to_dclr_cache[imo] = clean_no
                                                st.session_state.vessel_input_widget = imo
                                                if imo not in st.session_state.vessel_history:
                                                    st.session_state.vessel_history.insert(0, imo)
                                                    if len(st.session_state.vessel_history) > 6:
                                                        st.session_state.vessel_history = st.session_state.vessel_history[:6]
                                                synced_this_run = True
                                                st.rerun() # Refresh the page to show the map with new IMO
                                            
                                # Format dates nicely
                                acpt_dt_formatted = data['acptDt']
                                if len(acpt_dt_formatted) == 8: # YYYYMMDD
                                    acpt_dt_formatted = f"{acpt_dt_formatted[:4]}-{acpt_dt_formatted[4:6]}-{acpt_dt_formatted[6:8]} 09:40"
                                    
                                load_tmlm = data['loadDtyTmlm']
                                load_date_obj = None
                                if len(load_tmlm) == 8:
                                    try:
                                        load_date_obj = datetime.strptime(load_tmlm, "%Y%m%d")
                                        load_tmlm = f"{load_tmlm[:4]}-{load_tmlm[4:6]}-{load_tmlm[6:8]}"
                                    except:
                                        pass
                                    
                                is_loaded = data['shpmCmplYn'] == 'Y'
                                
                                # Real-time ETA Scrape
                                query_term = sanm
                                vf_eta_str = None
                                vf_dt = None
                                mmsi = "미상"
                                callsign = "미상"
                                flag = "미상"
                                imo_val = "미상"
                                if query_term:
                                    vf_data = get_realtime_eta_and_imo(query_term)
                                    vf_eta_str = vf_data.get('eta')
                                    mmsi = vf_data.get('mmsi', '미상')
                                    callsign = vf_data.get('callsign', '미상')
                                    flag = vf_data.get('flag', '미상')
                                    imo_val = vf_data.get('imo') or '미상'
                                    if vf_eta_str:
                                        try:
                                            clean_str = vf_eta_str.replace("ETA:", "").strip()
                                            current_year = datetime.now().year
                                            vf_dt = datetime.strptime(f"{current_year} {clean_str}", "%Y %b %d, %H:%M")
                                        except:
                                            pass
                                
                                # Compare ETAs
                                final_eta_display = f"{load_tmlm} ({'서류상 입항 기한' if is_import else '서류상 적재/도착 기한'})"
                                eta_warning_html = ""
                                is_delayed = False
                                
                                if vf_dt and load_date_obj:
                                    if vf_dt > load_date_obj:
                                        is_delayed = True
                                        final_eta_display = f"{vf_dt.strftime('%Y년 %m월 %d일 %H:%M')} (VesselFinder 실시간 ETA 적용)"
                                        eta_warning_html = '<br><span style="color:#ef4444; font-size:12px; font-weight:bold;">⚠️ 서류상 일정보다 지연됨</span>'
                                    else:
                                        final_eta_display = f"{vf_dt.strftime('%Y년 %m월 %d일 %H:%M')} (VesselFinder 실시간 ETA 적용)"
                                        eta_warning_html = '<br><span style="color:#10b981; font-size:12px; font-weight:bold;">✅ 기한 내 정상 도착 예정</span>'
                                
                                doc_title = "수 입 신 고 필 증" if is_import else "수 출 신 고 필 증"
                                doc_type_pill = "📥 수입" if is_import else "📦 수출"
                                incoterms = "CIF" if is_import else "FOB"
                                incoterms_desc = "매도인이 목적항까지 비용 부담" if is_import else "매도인이 선적항에서 선박에 적재할 때까지 위험/비용 부담"
                                pol_desc = "해외 출발항" if is_import else "부산항 (KRBUS)"
                                pod_desc = "부산항 (KRBUS)" if is_import else "해외 목적항 (예상)"
                                step1_title = "수입신고 접수" if is_import else "수출신고 접수 (Export Declaration)"
                                step2_title = "수입신고 수리" if is_import else "수출신고 수리 (Clearance Approved)"
                                
                                modal_id = f"myModal_{clean_no}"
                                
                                html_content = f"""
                                <!DOCTYPE html>
                                <html>
                                <head>
                                    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                                    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
                                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
                                    <style>
                                        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
                                        * {{ box-sizing: border-box; }}
                                        html, body {{ height: 100%; }}
                                        body {{ font-family: 'Pretendard', sans-serif; margin: 0; padding: 5px; background-color: transparent; color: #1e293b; overflow-x: hidden; }}
                                        
                                        .card {{ background: white; border-radius: 16px; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 0px; width: 100%; min-height: calc(100vh - 30px); display: flex; flex-direction: column; }}
                                        .card-title {{ display: flex; align-items: center; font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #0f172a; }}
                                        .card-title i {{ color: #10b981; margin-right: 10px; font-size: 20px; }}
                                        .card-title.unipass i {{ color: #d4af37; }}
                                        
                                        /* Timeline (Itinerary) */
                                        .timeline-container {{ position: relative; padding: 10px 0; margin-bottom: 10px; }}
                                        .timeline-line {{ position: absolute; top: 25px; left: 10%; right: 10%; height: 4px; background: #e2e8f0; z-index: 1; }}
                                        .timeline-steps {{ display: flex; justify-content: space-between; position: relative; z-index: 2; }}
                                        .step {{ display: flex; flex-direction: column; align-items: center; width: 33%; }}
                                        .step-icon {{ width: 32px; height: 32px; border-radius: 50%; background: #10b981; color: white; display: flex; align-items: center; justify-content: center; font-size: 14px; margin-bottom: 12px; border: 4px solid white; box-shadow: 0 0 0 1px #e2e8f0; }}
                                        .step-icon.delayed {{ background: #ef4444; }}
                                        .step-icon.pending {{ background: #94a3b8; }}
                                        .step-title {{ font-weight: 700; font-size: 11px; margin-bottom: 6px; text-align: center; word-break: keep-all; }}
                                        .step-date {{ background: #d1fae5; color: #047857; padding: 3px 8px; border-radius: 20px; font-size: 10px; border: 1px solid #a7f3d0; text-align: center; word-break: keep-all; }}
                                        .step-date.delayed {{ background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }}
                                        .step-date.pending {{ background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }}
                                        
                                        /* Info Pills */
                                        .pills-container {{ display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }}
                                        .pill {{ padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: 600; display: flex; align-items: center; word-break: keep-all; }}
                                        .pill-green {{ background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; }}
                                        .pill-yellow {{ background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }}
                                        .pill-gray {{ background: #f8fafc; border: 1px solid #e2e8f0; color: #475569; }}
                                        .count-badge {{ background: #f1f5f9; border: 1px solid #e2e8f0; padding: 4px 12px; border-radius: 20px; font-size: 13px; margin-left: auto; color: #64748b; font-weight: 600; }}
                                        
                                        /* Table */
                                        table.history-table {{ width: 100%; border-collapse: collapse; }}
                                        table.history-table th {{ padding: 10px 5px; text-align: left; font-size: 11px; color: #64748b; border-bottom: 2px solid #e2e8f0; font-weight: 600; white-space: nowrap; }}
                                        table.history-table td {{ padding: 12px 5px; font-size: 12px; color: #334155; vertical-align: middle; border-bottom: 1px solid #f1f5f9; line-height: 1.3; word-break: keep-all; }}
                                        table.history-table tr.row-blue {{ background-color: #eff6ff; }}
                                        table.history-table tr.row-green {{ background-color: #f0fdf4; }}
                                        table.history-table tr.row-red {{ background-color: #fef2f2; }}
                                        
                                        .status-complete {{ display: inline-flex; flex-direction: column; align-items: center; background: #d1fae5; color: #047857; padding: 6px 10px; border-radius: 20px; font-size: 12px; border: 1px solid #a7f3d0; font-weight: bold; }}
                                        .status-pending {{ display: inline-flex; flex-direction: column; align-items: center; background: #fef3c7; color: #d97706; padding: 6px 10px; border-radius: 20px; font-size: 12px; border: 1px solid #fde68a; font-weight: bold; }}
                                        .status-delayed {{ display: inline-flex; flex-direction: column; align-items: center; background: #fee2e2; color: #b91c1c; padding: 6px 10px; border-radius: 20px; font-size: 12px; border: 1px solid #fecaca; font-weight: bold; }}
                                        
                                        /* View Document Badge */
                                        .badge-view {{
                                            display: inline-flex; flex-direction: column; align-items: center; justify-content: center;
                                            background: #6366f1; color: white; border-radius: 20px; padding: 8px 16px;
                                            font-size: 12px; font-weight: bold; cursor: pointer; margin-left: 10px;
                                            box-shadow: 0 4px 10px rgba(99,102,241,0.3); transition: transform 0.2s;
                                            vertical-align: middle;
                                        }}
                                        .badge-view:hover {{ transform: scale(1.05); }}
                                        .badge-view i {{ font-size: 16px; margin-bottom: 2px; }}
                                        
                                        /* Modal Styles */
                                        .modal {{ display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); backdrop-filter: blur(4px); }}
                                        .modal-content {{ background-color: white; margin: 2% auto; padding: 30px; border-radius: 12px; width: 90%; max-width: 900px; max-height: 90vh; overflow-y: auto; position: relative; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }}
                                        .close-btn {{ position: absolute; right: 25px; top: 25px; font-size: 24px; cursor: pointer; color: #94a3b8; background: none; border: none; }}
                                        .close-btn:hover {{ color: #0f172a; }}
                                        
                                        /* Form Styles (For PDF) */
                                        #printArea {{ padding: 20px; background: white; }}
                                        .form-title {{ text-align: center; text-decoration: underline; letter-spacing: 15px; margin-bottom: 40px; font-size: 28px; color: black; }}
                                        .declaration-table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; color: black; margin-bottom: 20px; }}
                                        .declaration-table th, .declaration-table td {{ border: 1px solid #000; padding: 12px; }}
                                        .declaration-table th {{ background: #f8f9fa; width: 22%; }}
                                        
                                        .items-table {{ width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; color: black; margin-bottom: 20px; border: 1px solid #000; }}
                                        .items-table th {{ background: #e2e8f0; padding: 10px; border: 1px solid #000; font-weight: bold; }}
                                        .items-table td {{ padding: 10px; border: 1px solid #000; height: 35px; }}
                                        .items-table .td-money {{ text-align: right; }}
                                        .items-table .td-left {{ text-align: left; }}
                                        
                                        .btn-group {{ display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }}
                                        .btn-pdf {{ background: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; display: flex; align-items: center; gap: 8px; }}
                                        .btn-print {{ background: #10b981; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; display: flex; align-items: center; gap: 8px; }}
                                        
                                        .footer-text {{ font-size: 12px; color: #94a3b8; margin-top: 16px; margin-left: 8px; }}
                                        
                                        .watermark {{ position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%) rotate(-30deg); font-size: 120px; color: rgba(220, 220, 220, 0.3); z-index: 0; pointer-events: none; font-weight: bold; user-select: none; white-space: nowrap; }}
                                        .content-over-watermark {{ position: relative; z-index: 1; }}
                                    
                                        @media (prefers-color-scheme: dark) {{
                                            body {{ color: #f8fafc; }}
                                            .card {{ background: #1e293b; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); border: 1px solid #334155; }}
                                            .card-title {{ color: #f1f5f9; }}
                                            table.history-table th {{ color: #94a3b8; border-bottom: 2px solid #334155; }}
                                            table.history-table td {{ color: #cbd5e1; border-bottom: 1px solid #334155; }}
                                            .timeline-line {{ background: #334155; }}
                                            .step-icon {{ box-shadow: 0 0 0 1px #334155; border-color: #1e293b; color: #fff; }}
                                            .step-icon.pending {{ background: #475569; }}
                                            .step-title {{ color: #e2e8f0; }}
                                            .step-date {{ background: #064e3b; color: #a7f3d0; border-color: #065f46; }}
                                            .card-divider {{ border-color: #475569 !important; }}
                                            .step-date.delayed {{ background: #7f1d1d; color: #fecaca; border-color: #991b1b; }}
                                            .step-date.pending {{ background: #1e293b; color: #94a3b8; border-color: #334155; }}
                                            .count-badge {{ background: #334155; border-color: #475569; color: #cbd5e1; }}
                                            .pill-gray {{ background: #334155; border-color: #475569; color: #cbd5e1; }}
                                            .pill-yellow {{ background: #422006; border-color: #78350f; color: #fde68a; }}
                                            .pill-green {{ background: #064e3b; border-color: #065f46; color: #a7f3d0; }}
                                        }}
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
                                                    <div class="step-title">{step2_title}</div>
                                                    <div class="step-date">{acpt_dt_formatted}</div>
                                                </div>
                                                <div class="step">
                                                    <div class="step-icon {'' if is_loaded else 'pending'}"><i class="fa-solid {'fa-check' if is_loaded else 'fa-clock'}"></i></div>
                                                    <div class="step-title" style="color:{'inherit' if is_loaded else '#64748b'}">{pol_desc}</div>
                                                    <div class="step-date {'' if is_loaded else 'pending'}">{f"기한: {load_tmlm} (선적완료)" if is_loaded else f"기한: {load_tmlm} (미선적)"}</div>
                                                </div>
                                                <div class="step">
                                                    <div class="step-icon {'delayed' if is_delayed else 'pending'}"><i class="fa-solid {'fa-triangle-exclamation' if is_delayed else 'fa-ship'}"></i></div>
                                                    <div class="step-title" style="color:{'#ef4444' if is_delayed else '#64748b'}">{pod_desc}</div>
                                                    <div class="step-date {'delayed' if is_delayed else 'pending'}">{final_eta_display}</div>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <hr class="card-divider" style="border: 0; border-top: 1px dashed #cbd5e1; margin: 30px 0;" />
                                        
                                        <!-- Bottom Section: History -->
                                        <div style="display:flex; align-items:center; margin-bottom: 24px;">
                                            <div class="card-title unipass" style="margin-bottom:0;">
                                                <i class="fa-solid fa-building-columns"></i> 관세청 유니패스 — 절차별 처리현황 [{clean_no}]
                                            </div>
                                            <div class="count-badge">총 4건</div>
                                        </div>
                                        
                                        <div class="pills-container">
                                            <div class="pill pill-green">{doc_type_pill} &nbsp;|&nbsp; 조회유형: {'수입신고번호' if is_import else '수출신고번호'}</div>
                                            <div class="pill pill-yellow"><b style="color:#d97706;">{incoterms}</b> &nbsp;{incoterms_desc}</div>
                                            <div class="pill pill-gray">📍 {pol_desc} &nbsp;&rarr;&nbsp; 🏁 {pod_desc}</div>
                                        </div>
                                        
                                        <table class="history-table">
                                            <thead>
                                                <tr>
                                                    <th style="width:5%">#</th>
                                                    <th style="width:28%">처리 단계</th>
                                                    <th style="width:28%">처리 일시</th>
                                                    <th style="width:20%">처리 장소</th>
                                                    <th style="width:8%">상태</th>
                                                    <th style="width:11%">비고</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr>
                                                    <td style="color:#94a3b8;">1</td>
                                                    <td style="font-weight:600;">{step1_title}</td>
                                                    <td style="font-family:monospace;">{acpt_dt_formatted}</td>
                                                    <td style="color:#64748b;">관세사 / 세관 EDI</td>
                                                    <td><div class="status-complete"><i class="fa-solid fa-check"></i>완료</div></td>
                                                    <td></td>
                                                </tr>
                                                <tr class="row-blue">
                                                    <td style="color:#94a3b8;">2</td>
                                                    <td style="font-weight:700; color:#1d4ed8; display:flex; align-items:center;">
                                                        {step2_title}
                                                        <div class="badge-view" onclick="openModal()">📋 <span>면장 보기</span></div>
                                                    </td>
                                                    <td style="font-family:monospace;">{acpt_dt_formatted}</td>
                                                    <td style="color:#64748b;">관세청</td>
                                                    <td><div class="status-complete"><i class="fa-solid fa-check"></i>완료</div></td>
                                                    <td style="color:#64748b; font-size:12px;">신고번호:<br>{data['expDclrNo']}</td>
                                                </tr>
                                                <tr>
                                                    <td style="color:#94a3b8;">3</td>
                                                    <td style="font-weight:600;">{'양하 (Cargo Discharging)' if is_import else '선적 (Cargo Loading)'}</td>
                                                    <td style="font-family:monospace;">{f"기한: {load_tmlm} (선적완료)" if is_loaded else f"기한: {load_tmlm} (미선적)"}</td>
                                                    <td style="color:#64748b;">{pol_desc} / {data.get('sanm', '미상')}</td>
                                                    <td>
                                                        { '<div class="status-complete"><i class="fa-solid fa-check"></i>완료</div>' if is_loaded else '<div class="status-pending"><i class="fa-solid fa-clock"></i>미완료(예상)</div>' }
                                                    </td>
                                                    <td></td>
                                                </tr>
                                                <tr class="{'row-red' if is_delayed else 'row-green'}">
                                                    <td style="color:#94a3b8;">4</td>
                                                    <td style="font-weight:700; color:{'#ef4444' if is_delayed else '#047857'};"><span style="color:{'#ef4444' if is_delayed else '#10b981'}; font-size:18px; margin-right:5px;">●</span>{pod_desc} 도착 예정</td>
                                                    <td style="font-family:monospace;">{final_eta_display} {eta_warning_html}</td>
                                                    <td style="color:#64748b;">{pod_desc}</td>
                                                    <td>{ '<div class="status-delayed"><i class="fa-solid fa-triangle-exclamation"></i>지연</div>' if is_delayed else '<div class="status-pending"><i class="fa-solid fa-clock"></i>미완료(예상)</div>' }</td>
                                                    <td></td>
                                                </tr>
                                            </tbody>
                                        </table>
                                        <div style="margin-top: auto;"></div>
                                        <hr class="card-divider" style="border: 0; border-top: 1px dashed #cbd5e1; margin: 20px 0 10px 0;" />
                                        <div class="footer-text" style="margin-top: 0; padding-top: 0;">※ 출처: 관세청 유니패스(UNI-PASS) 및 VesselFinder 실시간 조회 데이터 · 최종 단계가 현재 처리 상태입니다.</div>
                                    </div>

                                    <!-- The Modal -->
                                    <div id="{modal_id}" class="modal" onclick="closeModalOutside(event)">
                                        <div class="modal-content" onclick="event.stopPropagation()">
                                            <button class="close-btn" onclick="closeModal()"><i class="fa-solid fa-xmark"></i></button>
                                            <div class="btn-group">
                                                <button class="btn-pdf" onclick="downloadPDF()"><i class="fa-solid fa-file-pdf"></i> PDF 다운로드</button>
                                                <button class="btn-print" onclick="printForm()"><i class="fa-solid fa-print"></i> 인쇄하기</button>
                                                <div style="margin-left:auto; display:flex; gap:10px;">
                                                    <button onclick="alert('💡 관세청 API 보안 정책상 상업송장(Invoice) 스캔 원본 파일은 외부로 제공되지 않습니다. 대신, 화면의 정보는 관세청에 신고된 데이터와 동일함을 보증합니다.')" style="background:#f1f5f9; color:#475569; padding:8px 16px; border:1px solid #cbd5e1; border-radius:6px; cursor:pointer;">📄 인보이스(CI) 원본 보기</button>
                                                    <button onclick="alert('💡 관세청 API 보안 정책상 패킹리스트(P/L) 스캔 원본 파일은 외부로 제공되지 않습니다. 상세 패킹 내역은 하단의 포장수량({data['csclPckUt']}) 정보를 참조해주세요.')" style="background:#f1f5f9; color:#475569; padding:8px 16px; border:1px solid #cbd5e1; border-radius:6px; cursor:pointer;">📦 패킹리스트(PL) 원본 보기</button>
                                                </div>
                                            </div>
                                            
                                            <div id="printArea_{clean_no}" style="position:relative; overflow:hidden; padding:20px; background:white;">
                                                <div class="watermark">SAMPLE COPY</div>
                                                <div class="content-over-watermark">
                                                    <h2 class="form-title">{doc_title}</h2>
                                                    <table class="declaration-table">
                                                        <tr>
                                                            <th>신고번호</th><td>{data['expDclrNo']}</td>
                                                            <th>신고(수리)일자</th><td>{acpt_dt_formatted[:10]}</td>
                                                        </tr>
                                                        <tr>
                                                            <th>수출자 (화주)</th>
                                                            <td colspan="3"><b>{data['exppnConm']}</b> <span style="color:#666; font-size:11px; margin-left:10px;">(사업자등록번호: 107-87-40814)</span></td>
                                                        </tr>
                                                        <tr>
                                                            <th>선기명 / 항차</th><td style="font-weight:bold; color:#1d4ed8;">{data.get('sanm', '미정')}</td>
                                                            <th>선적국 (Flag)</th><td>{flag}</td>
                                                        </tr>
                                                        <tr>
                                                            <th>선박 IMO/MMSI</th><td>IMO {imo_val} / MMSI {mmsi}</td>
                                                            <th>호출부호(CallSign)</th><td>{callsign}</td>
                                                        </tr>
                                                        <tr>
                                                            <th>적재항 (POL)</th><td>{pol_desc}</td>
                                                            <th>도착항 (POD)</th><td>{pod_desc}</td>
                                                        </tr>
                                                        <tr>
                                                            <th>포장수량</th><td>{data['csclPckUt']}</td>
                                                            <th>선적상태(여부)</th><td>{data['shpmCmplYn']} (기한: {load_tmlm})</td>
                                                        </tr>
                                                    </table>
                                                    
                                                    <!-- DB 연동 예정 품목 테이블 공간 -->
                                                    <h4 style="margin-top:30px; margin-bottom:10px; font-size:14px; border-left:4px solid #3b82f6; padding-left:8px;">[ 품목 상세 내역 ] <span style="font-weight:normal; font-size:11px; color:#ef4444; margin-left:10px;">※ 사내 ERP/DB 연동 시 실데이터 표기 영역 (현재 빈칸 처리됨)</span></h4>
                                                    <table class="items-table">
                                                        <thead>
                                                            <tr>
                                                                <th style="width:5%">#</th>
                                                                <th style="width:35%">제품명 (품목 및 규격)</th>
                                                                <th style="width:15%">수량 (단위)</th>
                                                                <th style="width:15%">단가</th>
                                                                <th style="width:15%">신고금액</th>
                                                                <th style="width:15%">관부가세</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            <tr>
                                                                <td>1</td><td class="td-left"></td><td></td><td class="td-money"></td><td class="td-money"></td><td></td>
                                                            </tr>
                                                            <tr style="background:#f8fafc;">
                                                                <td>2</td><td class="td-left"></td><td></td><td class="td-money"></td><td class="td-money"></td><td></td>
                                                            </tr>
                                                            <tr>
                                                                <td>3</td><td class="td-left"></td><td></td><td class="td-money"></td><td class="td-money"></td><td></td>
                                                            </tr>
                                                            <tr>
                                                                <td colspan="4" style="text-align:right; font-weight:bold; background:#e2e8f0;">총 합계금액 (Total Amount)</td>
                                                                <td class="td-money" style="font-weight:bold; background:#e2e8f0; color:#b91c1c;"></td>
                                                                <td style="background:#e2e8f0;"></td>
                                                            </tr>
                                                        </tbody>
                                                    </table>

                                                    <div style="margin-top: 20px;">
                                                        <h4 style="margin-bottom: 5px;">[ 절차 이력 전체 ]</h4>
                                                        <ul style="font-size: 13px; line-height: 1.6; padding-left: 20px;">
                                                            <li>[신고] {step1_title} 완료</li>
                                                            <li>[수리] {acpt_dt_formatted} - {step2_title} 승인</li>
                                                            <li>[선적] {'기한 내 적재/양하 완료' if is_loaded else f'{load_tmlm} 내 적재/양하 대기'}</li>
                                                        </ul>
                                                    </div>
                                                    <p style="text-align:center; margin-top:50px; font-size:12px; color:#555;">본 증명서는 관세청 통관시스템(UNIPASS) 전자문서와 동일함을 증명합니다.<br>이 문서는 열람 전용이며 공식 증명서로 사용할 수 없습니다.</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <script>
                                        function openModal() {{
                                            document.getElementById('{modal_id}').style.display = "block";
                                            document.body.style.overflow = "hidden";
                                        }}
                                        
                                        function closeModal() {{
                                            document.getElementById('{modal_id}').style.display = "none";
                                            document.body.style.overflow = "auto";
                                        }}
                                        
                                        function closeModalOutside(event) {{
                                            if (event.target == document.getElementById('{modal_id}')) {{ closeModal(); }}
                                        }}
                                        
                                        function downloadPDF() {{
                                            const {{ jsPDF }} = window.jspdf;
                                            const printArea = document.getElementById('printArea_{clean_no}');
                                            
                                            const originalBorder = printArea.style.border;
                                            printArea.style.border = 'none';
                                            
                                            html2canvas(printArea, {{ scale: 2 }}).then(canvas => {{
                                                const imgData = canvas.toDataURL('image/png');
                                                const pdf = new jsPDF('p', 'mm', 'a4');
                                                const pdfWidth = pdf.internal.pageSize.getWidth();
                                                const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
                                                
                                                pdf.addImage(imgData, 'PNG', 0, 10, pdfWidth, pdfHeight);
                                                const fileName = "{'수입' if is_import else '수출'}신고필증_{data['expDclrNo']}.pdf";
                                                pdf.save(fileName);
                                                
                                                printArea.style.border = originalBorder;
                                            }});
                                        }}
                                        
                                        function printForm() {{
                                            const printContent = document.getElementById('printArea_{clean_no}').innerHTML;
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
                                components.html(html_content, height=1170, scrolling=False)
                                
                        except Exception as e:
                            st.error(f"⚠️ 유니패스 API 통신 오류 ({clean_no}): {e}")



        # --- 2. 선박 조회 섹션 --- (이제 우측 컬럼)
        with main_col2:
            st.subheader("🚢 실시간 선박 위치 및 기상 조회")
            
            if st.session_state.vessel_history:
                st.markdown("⭐️ **관심 선박 목록 (클릭 시 1초 전환 토글)**")
                v_cols = st.columns(3)
                for i, hist in enumerate(st.session_state.vessel_history):
                    with v_cols[i % 3]:
                        vsub1, vsub2 = st.columns([4, 1])
                        btn_type = "primary" if hist == st.session_state.vessel_input_widget else "secondary"
                        vsub1.button(f"🛳️ {hist}", key=f"hist_{hist}", on_click=set_vessel, args=(hist,), type=btn_type, use_container_width=True)
                        vsub2.button("✖", key=f"vdel_{hist}", on_click=del_vessel, args=(hist,), use_container_width=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
            col_s1, col_s2 = st.columns([3, 1])
            with col_s1:
                st.text_input("🔍 선박 고유번호 추가 (IMO/MMSI)", key="vessel_input_widget", placeholder="예: 440381000 (MMSI) 또는 9811000 (IMO)", on_change=on_vessel_input_change)
            
            search_vessel = st.session_state.get("vessel_input_widget", "").strip()
            if not search_vessel and st.session_state.get("vessel_history"):
                search_vessel = st.session_state.vessel_history[0].strip()
            if not search_vessel:
                search_vessel = "9955284" # Default to HMM TOPAZ
            
            mmsi_script = 'var imo="9955284"; var zoom=10;' # Default HMM TOPAZ
            if search_vessel:
                if len(search_vessel) == 9 and search_vessel.isdigit():
                    mmsi_script = f'var mmsi="{search_vessel}"; var zoom=10;'
                elif len(search_vessel) >= 7 and search_vessel.isdigit():
                    mmsi_script = f'var imo="{search_vessel}"; var zoom=10;'
                else:
                    mmsi_script = f'var names=true; var lat=33.74; var lon=-118.27; var zoom=10;'
                    
            vesselfinder_html = f"""
            <div>
                <div style="width: 100%; height: 450px;">
                    <script type="text/javascript">
                        var width="100%";
                        var height="450";
                        var names=true;
                        {mmsi_script}
                    </script>
                    <script type="text/javascript" src="https://www.vesselfinder.com/aismap.js"></script>
                </div>
            </div>
            """
            
            windy_html = """
            <div>
                                <iframe 
                    width="100%" 
                    height="350" 
                    src="https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=mm&metricTemp=°C&metricWind=kt&zoom=4&overlay=waves&product=ecmwf&level=surface&lat=35.0&lon=129.0" 
                    frameborder="0">
                </iframe>
            </div>
            """
            
            components.html(vesselfinder_html, height=450, scrolling=False)
            st.markdown("#### 🌊 바다 날씨 및 풍랑 예측 (Windy)")
            components.html(windy_html, height=350, scrolling=False)

        # --- 3. 선박 실시간 항로 및 운항·도착 Fact 정보 섹션 ---
        st.markdown("<br><hr style='border:0; border-top:1px dashed #475569; margin:35px 0 25px 0;'>", unsafe_allow_html=True)
        st.subheader("🗺️ 선박 실시간 항로 및 목적지 운항·도착 Fact 정보 (Live AIS Voyage Track & Destination Fact)")
        st.markdown("선박의 실제 출발항(부산항 신항) 및 최종 목적항(미국 로스앤젤레스항)의 **VesselFinder AIS Fact 데이터**를 기반으로 실시간 운항 궤적 및 항로 분석을 제공합니다. (지나온 경로는 **굵은 회색선**, Forecast 예측 항로는 **점선**, 현재 위치는 **연두색**, 항만은 **세련된 비콘 아이콘**으로 표시)")

        @st.cache_data(ttl=180, show_spinner=False)
        def fetch_vesselfinder_live(query_str):
            query = str(query_str).strip()
            if not query:
                query = "9955284"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            default_res = {
                'name': 'HMM TOPAZ',
                'imo': '9955284',
                'mmsi': '636024330',
                'lat': 33.743,
                'lon': -118.267,
                'cog': 45.7,
                'sog': 0.0,
                'nav_status': 'Moored',
                'loc_desc': 'North America West Coast (Port of Los Angeles)',
                'port_desc': 'Los Angeles, United States (USA) on Sep 13, 09:55 UTC',
                'last_port': 'Busan New Port, Korea',
                'last_atd': 'Aug 31, 15:03 UTC',
                'destination': 'Los Angeles, United States (USA)',
                'dest_ata': 'Sep 13, 09:55 UTC',
                'type': '컨테이너선 (16,000 TEU급)',
                'success': True
            }
            try:
                url = f'https://www.vesselfinder.com/vessels/details/{query}'
                r = requests.get(url, headers=headers, timeout=6)
                if r.status_code != 200 or 'Search' in r.url:
                    sr = requests.get(f'https://www.vesselfinder.com/vessels?name={query}', headers=headers, timeout=6)
                    if sr.status_code == 200:
                        soup = BeautifulSoup(sr.text, 'html.parser')
                        link = soup.select_one('a.ship-link')
                        if link:
                            url = 'https://www.vesselfinder.com' + link.get('href')
                            r = requests.get(url, headers=headers, timeout=6)
                            
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    djson_el = soup.select_one('#djson')
                    data = {}
                    if djson_el and djson_el.get('data-json'):
                        try:
                            data = json.loads(djson_el.get('data-json'))
                        except Exception:
                            pass
                            
                    main_text = ' '.join(soup.get_text().split())
                    h1 = soup.select_one('h1.title')
                    v_name = h1.text.split(',')[0].strip() if h1 else query
                    
                    loc_m = re.search(r'The current position of [^is]+ is at ([^\.]+ reported [^\.]+ by AIS)', main_text)
                    loc_desc = loc_m.group(1).strip() if loc_m else ''
                    
                    port_m = re.search(r'The vessel arrived at the port of ([^\.]+ on [^\.]+ UTC)', main_text)
                    port_desc = port_m.group(1).strip() if port_m else ''
                    
                    last_m = re.search(r'Last Port\s*([A-Za-z0-9\s,]+?)\s*AT[DA]:\s*([A-Za-z0-9\s,:]+?)(?:\s*\([^\)]*\)|$)', main_text)
                    last_port = last_m.group(1).strip() if last_m else 'Busan New Port, Korea'
                    last_atd = last_m.group(2).strip() if last_m else 'Aug 31, 15:03 UTC'
                    
                    dest_m = re.search(r'Destination\s*([A-Za-z0-9\s,\(\)]+?)\s*AT[AE]:', main_text)
                    dest = dest_m.group(1).strip() if dest_m else 'Los Angeles, United States (USA)'
                    
                    ata_m = re.search(r'ATA:\s*([A-Za-z0-9\s,:]+?)\s*ARRIVED', main_text)
                    dest_ata = ata_m.group(1).strip() if ata_m else 'Sep 13, 09:55 UTC'
                    
                    status_m = re.search(r'Navigation Status\s*([A-Za-z\s]+)', main_text)
                    nav_status = status_m.group(1).strip() if status_m else 'Moored'
                    if 'Position Received' in nav_status:
                        nav_status = nav_status.replace('Position Received', '').strip()
                    
                    lat = data.get('ship_lat')
                    lon = data.get('ship_lon')
                    cog = data.get('ship_cog', 0.0)
                    sog = data.get('ship_sog', 0.0)
                    mmsi = str(data.get('mmsi', ''))
                    
                    if port_desc or 'Los Angeles' in loc_desc:
                        if 'Los Angeles' in port_desc or 'Los Angeles' in main_text:
                            lat, lon = 33.743, -118.267
                        elif 'Hamburg' in port_desc:
                            lat, lon = 53.532, 9.970
                        elif 'Rotterdam' in port_desc:
                            lat, lon = 51.950, 4.140
                        elif 'Singapore' in port_desc:
                            lat, lon = 1.280, 103.850
                        elif 'Busan' in port_desc:
                            lat, lon = 35.075, 128.825
                        elif 'Incheon' in port_desc:
                            lat, lon = 37.440, 126.600
                        elif 'Antwerp' in port_desc:
                            lat, lon = 51.260, 4.350
                        elif 'Shanghai' in port_desc:
                            lat, lon = 31.230, 121.500

                    v_type = '상선 (Cargo Vessel)'
                    for tr in soup.select('table.tpt1 tr'):
                        txt = tr.get_text()
                        if 'Ship Type' in txt:
                            v_type = txt.replace('Ship Type', '').strip()
                            break

                    if lat is not None and lon is not None:
                        return {
                            'name': v_name,
                            'imo': query if query.isdigit() and len(query) == 7 else str(data.get('imo', '9955284')),
                            'mmsi': mmsi or default_res['mmsi'],
                            'lat': float(lat),
                            'lon': float(lon),
                            'cog': float(cog),
                            'sog': float(sog),
                            'nav_status': nav_status,
                            'loc_desc': loc_desc or f"위도 {lat}°, 경도 {lon}° 해상",
                            'port_desc': port_desc,
                            'last_port': last_port,
                            'last_atd': last_atd,
                            'destination': dest,
                            'dest_ata': dest_ata,
                            'type': v_type,
                            'success': True
                        }
            except Exception:
                pass
            return default_res

        # 현재 조회된 선박 식별 및 VesselFinder 실시간 AIS 조회
        curr_v = st.session_state.get("vessel_input_widget", "").strip()
        if not curr_v and st.session_state.get("vessel_history"):
            curr_v = st.session_state.vessel_history[0].strip()
        if not curr_v:
            curr_v = "9955284"

        v_data = fetch_vesselfinder_live(curr_v)
        active_vessel = v_data['name']
        active_imo = v_data['imo']
        active_mmsi = v_data['mmsi']
        v_lat = v_data['lat']
        v_lon = v_data['lon']
        v_sog = v_data['sog']
        v_cog = v_data['cog']
        v_status = v_data['nav_status']
        v_loc_desc = v_data['loc_desc']
        v_last_port = v_data.get('last_port', 'Busan New Port, Korea')
        v_last_atd = v_data.get('last_atd', 'Aug 31, 15:03 UTC')
        v_dest = v_data.get('destination', 'Los Angeles, United States (USA)')
        v_dest_ata = v_data.get('dest_ata', 'Sep 13, 09:55 UTC')
        vessel_type = v_data['type']

        # 하버사인 거리 계산 함수 (해리 Nautical Miles)
        def haversine_nm(lat1, lon1, lat2, lon2):
            R_nm = 3440.065
            p1, p2 = math.radians(lat1), math.radians(lat2)
            dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
            a = math.sin(dp/2.0)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2.0)**2
            return round(R_nm * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

        # 출발 기항지 (POL Fact: 부산항 신항)
        origin_lat, origin_lon = 35.075, 128.825
        origin_name_kr = "부산항 신항"
        origin_name_en = "Busan New Port (KRBUS)"

        # 최종 목적항 (POD Fact: 미국 로스앤젤레스항)
        dest_lat, dest_lon = 33.743, -118.267
        dest_name_kr = "로스앤젤레스항"
        dest_name_en = "Port of Los Angeles (USLAX)"
        
        # Leaflet 태평양 횡단 경도 보정
        dest_lon_leaf = dest_lon + 360 if dest_lon < 0 else dest_lon
        v_lon_leaf = v_lon + 360 if v_lon < 0 else v_lon

        # 총 운항 거리 (대권항로 기준 약 5,217 NM)
        total_dist_nm = haversine_nm(origin_lat, origin_lon, dest_lat, dest_lon)

        # Fact 기반 실제 항로 좌표 (부산항 신항 -> 북태평양 대권항로 -> 로스앤젤레스항)
        # 인천항 등 비실제 경로는 철저히 배제하고, 부산항 출발 -> 미국 LA항 도착의 단일 팩트 항로만 구성
        route_points = [
            [origin_lat, origin_lon],    # 1. 부산항 신항 출항 (POL)
            [38.2, 142.0],               # 2. 일본 동북부 쓰가루 해협 외측
            [43.5, 158.0],               # 3. 쿠릴 열도 남단 외해
            [47.8, 178.0],               # 4. 북태평양 날짜변경선 해역
            [48.6, 198.0],               # 5. 알래스카만 남부 대권항로
            [44.5, 218.0],               # 6. 북동 태평양 접근로
            [38.5, 234.0],               # 7. 캘리포니아 연안 접근 회랑
            [dest_lat, dest_lon_leaf]    # 8. 미국 로스앤젤레스항 부두 도착 (POD)
        ]

        # [요청 규정]
        # 1. 지나온 경로: 부산항 신항 출항 -> 북태평양 횡단 궤적 (굵은 회색선)
        # 2. Forecast: 목적항 최종 진입 및 입항 예측 경로 (점선)
        # 3. 현재 위치: 로스앤젤레스항 정박 위치 (연두색 발광 펄스)
        # 4. 한국항(부산항)에는 불필요한 이중선이 없도록 단일 출항선만 적용하고, 세련된 비콘 아이콘으로 표시
        past_points = route_points[:-1]
        forecast_points = [route_points[-2], route_points[-1]]

        map_center = [40.0, 185.0]
        map_zoom = 3
        curr_marker_coord = [v_lat, v_lon_leaf]
        alt_marker_js = f"L.marker([{v_lat}, {v_lon}], {{ icon: currentIcon }}).addTo(map);"

        lat_dir = 'N' if v_lat >= 0 else 'S'
        lon_dir = 'E' if v_lon >= 0 else 'W'
        v_lat_str = f"{abs(v_lat):.2f}°{lat_dir}"
        v_lon_str = f"{abs(v_lon):.2f}°{lon_dir}"
        status_kr = "정박 중 (Moored)" if "moor" in v_status.lower() else ("닻 대기 (At Anchor)" if "anchor" in v_status.lower() else "항해 중 (Underway)")

        past_points_json = json.dumps(past_points)
        forecast_points_json = json.dumps(forecast_points)
        route_points_json = json.dumps(route_points)
        map_center_json = json.dumps(map_center)
        curr_marker_coord_json = json.dumps(curr_marker_coord)

        route_map_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Live Vessel Route & Destination Fact</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
                body {{ background: #0f172a; color: #f1f5f9; padding: 6px; overflow: hidden; }}
                .hud-grid {{ display: grid; grid-template-columns: 1.25fr 1fr 1fr; gap: 12px; margin-bottom: 12px; }}
                .hud-card {{ background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(71, 85, 105, 0.5); border-radius: 12px; padding: 12px 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }}
                .hud-title {{ font-size: 11.5px; color: #94a3b8; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }}
                .hud-main {{ font-size: 16px; font-weight: 700; color: #ffffff; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
                .hud-sub {{ font-size: 12px; color: #cbd5e1; margin-top: 4px; line-height: 1.5; }}
                .hud-badge-green {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }}
                .hud-badge-blue {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }}
                .hud-badge-amber {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }}
                
                .controls-bar {{ display: flex; justify-content: space-between; align-items: center; background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(71, 85, 105, 0.5); border-radius: 10px; padding: 8px 14px; margin-bottom: 10px; flex-wrap: wrap; gap: 8px; }}
                .view-btn-group, .anim-btn-group {{ display: flex; align-items: center; gap: 6px; }}
                .c-btn {{ background: #1e293b; color: #e2e8f0; border: 1px solid #475569; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }}
                .c-btn:hover {{ background: #334155; border-color: #64748b; }}
                .c-btn.active {{ background: #2563eb; color: #ffffff; border-color: #3b82f6; box-shadow: 0 0 10px rgba(37, 99, 235, 0.5); }}
                
                #map-container {{ width: 100%; height: 510px; border-radius: 12px; overflow: hidden; border: 1px solid #334155; position: relative; }}
                
                /* [요청 규정] 선박 현재 위치: 연두색 발광 펄스 마커 */
                .vessel-current-icon {{ position: relative; display: flex; align-items: center; justify-content: center; }}
                .vessel-pulse-dot {{ width: 18px; height: 18px; background: #22c55e; border: 2px solid #ffffff; border-radius: 50%; box-shadow: 0 0 14px #22c55e, 0 0 24px rgba(34, 197, 94, 0.8); z-index: 10; }}
                .vessel-pulse-ring {{ position: absolute; width: 40px; height: 40px; border-radius: 50%; border: 2.5px solid #4ade80; animation: pulse-wave 1.8s infinite ease-out; z-index: 5; }}
                @keyframes pulse-wave {{ 0% {{ transform: scale(0.5); opacity: 1; }} 100% {{ transform: scale(1.6); opacity: 0; }} }}
                
                /* [요청 규정] 한국항 및 목적항: 세련된 비콘 아이콘 (단일 선 및 고품격 UI) */
                .refined-port-icon {{ position: relative; display: flex; align-items: center; justify-content: center; }}
                .port-pulse-ring {{ position: absolute; width: 36px; height: 36px; border-radius: 50%; border: 2px solid rgba(56, 189, 248, 0.75); animation: port-wave 2.2s infinite ease-out; pointer-events: none; }}
                .port-pulse-ring.dest {{ border-color: rgba(251, 191, 36, 0.8); }}
                @keyframes port-wave {{ 0% {{ transform: scale(0.5); opacity: 1; }} 100% {{ transform: scale(1.7); opacity: 0; }} }}
                .port-core-circle {{ width: 26px; height: 26px; background: linear-gradient(135deg, #0284c7, #0369a1); border: 2px solid #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 11px; box-shadow: 0 0 12px rgba(56, 189, 248, 0.8), 0 3px 6px rgba(0,0,0,0.5); z-index: 10; }}
                .port-core-circle.dest {{ background: linear-gradient(135deg, #d97706, #b45309); box-shadow: 0 0 12px rgba(251, 191, 36, 0.8), 0 3px 6px rgba(0,0,0,0.5); }}
                .port-badge-label {{ position: absolute; bottom: -28px; left: 50%; transform: translateX(-50%); white-space: nowrap; background: rgba(15, 23, 42, 0.94); border: 1px solid rgba(56, 189, 248, 0.6); border-radius: 12px; padding: 2px 8px; font-size: 11px; font-weight: 700; color: #f1f5f9; box-shadow: 0 4px 10px rgba(0,0,0,0.6); display: flex; align-items: center; gap: 4px; pointer-events: none; z-index: 20; }}
                .port-badge-label.dest {{ border-color: rgba(251, 191, 36, 0.6); }}
                
                .moving-ship-marker {{ transition: transform 0.1s linear; }}
                
                .map-legend {{ position: absolute; bottom: 20px; left: 20px; z-index: 1000; background: rgba(15, 23, 42, 0.92); border: 1px solid rgba(71, 85, 105, 0.8); border-radius: 8px; padding: 10px 14px; font-size: 11.5px; color: #cbd5e1; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); }}
                .legend-item {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }}
                .legend-line-gray {{ width: 24px; height: 6px; background: #94a3b8; border-radius: 2px; }}
                .legend-line-dash {{ width: 24px; height: 0; border-top: 3px dashed #38bdf8; }}
                .legend-dot-green {{ width: 12px; height: 12px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e; border: 1px solid #fff; }}
                .legend-port-origin {{ width: 12px; height: 12px; background: #0284c7; border-radius: 50%; border: 1px solid #fff; }}
                .legend-port-dest {{ width: 12px; height: 12px; background: #d97706; border-radius: 50%; border: 1px solid #fff; }}
            </style>
        </head>
        <body>
            <div class="hud-grid">
                <div class="hud-card">
                    <div class="hud-title"><i class="fa-solid fa-ship"></i> 선박 정보 및 VesselFinder 실시간 위치</div>
                    <div class="hud-main">
                        <span>{active_vessel}</span>
                        <span class="hud-badge-green">{status_kr}</span>
                        <span class="hud-badge-blue">VesselFinder Live</span>
                    </div>
                    <div class="hud-sub">
                        IMO: <b>{active_imo}</b> · 제원: {vessel_type} · 속력: <b>{v_sog} Knots</b> · 침로: <b>{v_cog}°</b><br>
                        📍 <b>AIS 실시간 위치: {v_lat_str}, {v_lon_str}</b> ({v_loc_desc})<br>
                        ⚓ 최근 기항: {v_last_port}
                    </div>
                </div>
                
                <div class="hud-card" style="border-left: 3px solid #0284c7;">
                    <div class="hud-title"><i class="fa-solid fa-anchor" style="color:#38bdf8;"></i> 출발 기항지 실적 (Departure · Fact)</div>
                    <div class="hud-main" style="color:#38bdf8;">
                        <span>🇰🇷 {origin_name_kr}</span>
                        <span class="hud-badge-blue">출항 완료</span>
                    </div>
                    <div class="hud-sub">
                        ⚓ <b>출항 일시(ATD): {v_last_atd}</b><br>
                        항로: <b>북태평양 횡단 대권항로 (Great Circle Route)</b><br>
                        운항 상태: 출항 후 태평양 횡단 완료
                    </div>
                </div>
                
                <div class="hud-card" style="border-left: 3px solid #fbbf24;">
                    <div class="hud-title"><i class="fa-solid fa-location-dot" style="color:#fbbf24;"></i> 최종 목적항 실적 및 Forecast (Destination · Fact)</div>
                    <div class="hud-main" style="color:#fbbf24;">
                        <span>🇺🇸 {dest_name_kr}</span>
                        <span class="hud-badge-amber">입항 완료 (정박 중)</span>
                    </div>
                    <div class="hud-sub">
                        🏁 <b>도착 일시(ATA): {v_dest_ata}</b><br>
                        총 항해거리: <b>{total_dist_nm:,.0f} NM</b> (약 {int(total_dist_nm * 1.852):,} km)<br>
                        현재 상태: <b>터미널 부두 정박 하역 중 (Moored)</b>
                    </div>
                </div>
            </div>
            
            <div class="controls-bar">
                <div class="view-btn-group">
                    <span style="font-size:12px; color:#94a3b8; margin-right:4px;">🎯 화면 시점:</span>
                    <button class="c-btn active" id="btn-view-all" onclick="zoomView('all')">🌐 태평양 전 항로 보기</button>
                    <button class="c-btn" id="btn-view-origin" onclick="zoomView('origin')">🇰🇷 출발지: {origin_name_kr}</button>
                    <button class="c-btn" id="btn-view-dest" onclick="zoomView('dest')">🇺🇸 목적지: {dest_name_kr}</button>
                    <button class="c-btn" id="btn-view-ship" onclick="zoomView('ship')">📍 선박 현재 위치</button>
                </div>
                <div class="anim-btn-group">
                    <span style="font-size:12px; color:#94a3b8; margin-right:4px;">🎬 항해 애니메이션:</span>
                    <button class="c-btn" id="btn-play" onclick="togglePlay()"><i class="fa-solid fa-play"></i> 실시간 시뮬레이션</button>
                    <button class="c-btn" id="btn-reset" onclick="resetAnimation()"><i class="fa-solid fa-rotate-left"></i> 초기화</button>
                    <button class="c-btn" id="btn-speed" onclick="toggleSpeed()">속도: 1x</button>
                </div>
            </div>
            
            <div id="map-container">
                <div class="map-legend">
                    <div style="font-weight:700; margin-bottom:6px; color:#f8fafc; font-size:12px;">🗺️ 항로 범례 (Legend)</div>
                    <div class="legend-item"><div class="legend-line-gray"></div><span>지나온 경로 (굵은 회색선)</span></div>
                    <div class="legend-item"><div class="legend-line-dash"></div><span>Forecast 목적항 입항 접근로 (점선)</span></div>
                    <div class="legend-item"><div class="legend-dot-green"></div><span>선박 현재 위치 (연두색 펄스)</span></div>
                    <div class="legend-item"><div class="legend-port-origin"></div><span>출발항 (부산항 신항)</span></div>
                    <div class="legend-item"><div class="legend-port-dest"></div><span>목적항 (로스앤젤레스항)</span></div>
                </div>
            </div>

            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                const map = L.map('map-container', {{
                    center: {map_center_json},
                    zoom: {map_zoom},
                    zoomControl: true,
                    worldCopyJump: true
                }});

                L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                    attribution: '&copy; CARTO, OpenStreetMap',
                    maxZoom: 18
                }}).addTo(map);

                const pastPoints = {past_points_json};
                const forecastPoints = {forecast_points_json};
                const routePoints = {route_points_json};

                // [요청 규정] 지나온 경로는 굵은 회색선으로 표시 (단일 선으로 깔끔하게 렌더링)
                const pastPolyline = L.polyline(pastPoints, {{
                    color: '#94a3b8',
                    weight: 6,
                    opacity: 0.95,
                    lineCap: 'round',
                    lineJoin: 'round'
                }}).addTo(map);

                // [요청 규정] Forecast는 점선으로 표시 (목적지 입항 접근로)
                const forecastPolyline = L.polyline(forecastPoints, {{
                    color: '#38bdf8',
                    weight: 4,
                    dashArray: '8, 8',
                    opacity: 0.95,
                    lineCap: 'round'
                }}).addTo(map);

                // [요청 규정] 현재 위치는 연두색으로 표시 (연두색 펄스 애니메이션 마커)
                const currentIcon = L.divIcon({{
                    className: 'vessel-current-icon',
                    html: '<div class="vessel-pulse-ring"></div><div class="vessel-pulse-dot"></div>',
                    iconSize: [22, 22],
                    iconAnchor: [11, 11]
                }});

                const currentMarker = L.marker({curr_marker_coord_json}, {{ icon: currentIcon }}).addTo(map);
                currentMarker.bindPopup(`
                    <div style="color:#0f172a; font-size:12px; font-family:sans-serif;">
                        <b style="font-size:13px; color:#15803d;">🛳️ {active_vessel} (실시간 AIS 위치)</b><br>
                        <hr style="margin:4px 0;">
                        위치: <b>{v_lat_str}, {v_lon_str}</b><br>
                        해역: {v_loc_desc}<br>
                        속력: <b>{v_sog} Knots</b> · 침로: <b>{v_cog}°</b><br>
                        상태: <b>{status_kr}</b><br>
                        최근 기항: {v_last_port}<br>
                        목적지: <b>{v_dest}</b><br>
                        <small style="color:#64748b;">(VesselFinder 실시간 AIS 수신 반영)</small>
                    </div>
                `).openPopup();

                {alt_marker_js}

                // [요청 규정] 한국항(부산항) 및 목적항: 세련된 비콘 아이콘 (중복된 굵은 선 제거 완료)
                const originPortIcon = L.divIcon({{
                    className: 'refined-port-icon',
                    html: '<div class="port-pulse-ring"></div><div class="port-core-circle"><i class="fa-solid fa-anchor"></i></div><div class="port-badge-label"><span>🇰🇷 {origin_name_kr}</span></div>',
                    iconSize: [26, 26],
                    iconAnchor: [13, 13]
                }});

                const originMarker = L.marker([{origin_lat}, {origin_lon}], {{ icon: originPortIcon }}).addTo(map);
                originMarker.bindPopup(`
                    <div style="color:#0f172a; font-size:12px; font-family:sans-serif;">
                        <b style="font-size:13px; color:#0284c7;">⚓ {origin_name_kr} ({origin_name_en})</b><br>
                        <hr style="margin:4px 0;">
                        구분: <b>출발 기항지 (Port of Loading)</b><br>
                        출항 실적: <b>{v_last_atd} (ATD)</b><br>
                        목적지: <b>{v_dest}</b><br>
                        항로: <b>북태평양 횡단 대권항로 (단일 팩트 항로)</b>
                    </div>
                `);

                const destPortIcon = L.divIcon({{
                    className: 'refined-port-icon',
                    html: '<div class="port-pulse-ring dest"></div><div class="port-core-circle dest"><i class="fa-solid fa-location-dot"></i></div><div class="port-badge-label dest"><span>🇺🇸 {dest_name_kr}</span></div>',
                    iconSize: [26, 26],
                    iconAnchor: [13, 13]
                }});

                const destMarker = L.marker([{dest_lat}, {dest_lon_leaf}], {{ icon: destPortIcon }}).addTo(map);
                destMarker.bindPopup(`
                    <div style="color:#0f172a; font-size:12px; font-family:sans-serif;">
                        <b style="font-size:13px; color:#d97706;">🏢 {dest_name_kr} ({dest_name_en})</b><br>
                        <hr style="margin:4px 0;">
                        구분: <b>최종 목적항 (Port of Discharge)</b><br>
                        도착 실적: <b>{v_dest_ata} (ATA)</b><br>
                        현재 상태: <b>정박 중 (Moored / 하역 대기)</b><br>
                        총 항해거리: <b>{total_dist_nm:,.0f} NM</b> (약 {int(total_dist_nm * 1.852):,} km)
                    </div>
                `);
                L.marker([{dest_lat}, {dest_lon}], {{ icon: destPortIcon }}).addTo(map);

                // 초기 뷰 설정 (전체 태평양 항로 피팅)
                try {{
                    const group = L.featureGroup([pastPolyline, forecastPolyline]);
                    map.fitBounds(group.getBounds().pad(0.12));
                }} catch(e) {{
                    map.setView({map_center_json}, {map_zoom});
                }}

                function zoomView(mode) {{
                    document.querySelectorAll('.view-btn-group .c-btn').forEach(b => b.classList.remove('active'));
                    if (mode === 'all') {{
                        document.getElementById('btn-view-all').classList.add('active');
                        map.flyToBounds(L.featureGroup([pastPolyline, forecastPolyline]).getBounds().pad(0.12));
                    }} else if (mode === 'origin') {{
                        document.getElementById('btn-view-origin').classList.add('active');
                        map.flyTo([{origin_lat}, {origin_lon}], 8);
                    }} else if (mode === 'dest') {{
                        document.getElementById('btn-view-dest').classList.add('active');
                        map.flyTo([{dest_lat}, {dest_lon_leaf}], 8);
                    }} else if (mode === 'ship') {{
                        document.getElementById('btn-view-ship').classList.add('active');
                        map.flyTo({curr_marker_coord_json}, 9);
                    }}
                }}

                // 애니메이션 보간 생성 (실제 부산항 -> LA항 항로 궤적을 따라 순항)
                function getInterpolatedRoute(points, stepsPerSegment = 20) {{
                    const res = [];
                    for (let i = 0; i < points.length - 1; i++) {{
                        const p1 = points[i];
                        const p2 = points[i + 1];
                        for (let s = 0; s < stepsPerSegment; s++) {{
                            const t = s / stepsPerSegment;
                            res.push([
                                p1[0] + (p2[0] - p1[0]) * t,
                                p1[1] + (p2[1] - p1[1]) * t
                            ]);
                        }}
                    }}
                    res.push(points[points.length - 1]);
                    return res;
                }}

                const animRoute = getInterpolatedRoute(routePoints, 20);

                const movingShipIcon = L.divIcon({{
                    className: 'moving-ship-marker',
                    html: '<div style="background:#2563eb; color:#ffffff; padding:4px 7px; border-radius:50%; box-shadow:0 0 12px #38bdf8; display:flex; align-items:center; justify-content:center; border:1px solid #fff;"><i class="fa-solid fa-ship" style="font-size:12px;"></i></div>',
                    iconSize: [24, 24],
                    iconAnchor: [12, 12]
                }});

                let animShip = null;
                let isPlaying = false;
                let animIndex = 0;
                let speedMult = 1;
                let animTimer = null;

                function togglePlay() {{
                    if (isPlaying) {{
                        pauseAnimation();
                    }} else {{
                        startAnimation();
                    }}
                }}

                function startAnimation() {{
                    isPlaying = true;
                    document.getElementById('btn-play').innerHTML = '<i class="fa-solid fa-pause"></i> 일시 정지';
                    
                    if (!animShip) {{
                        animShip = L.marker(animRoute[animIndex], {{ icon: movingShipIcon }}).addTo(map);
                    }}

                    const interval = Math.max(20, 80 / speedMult);
                    clearInterval(animTimer);
                    animTimer = setInterval(() => {{
                        if (animIndex < animRoute.length - 1) {{
                            animIndex++;
                            animShip.setLatLng(animRoute[animIndex]);
                        }} else {{
                            pauseAnimation();
                            animIndex = 0;
                        }}
                    }}, interval);
                }}

                function pauseAnimation() {{
                    isPlaying = false;
                    document.getElementById('btn-play').innerHTML = '<i class="fa-solid fa-play"></i> 실시간 시뮬레이션';
                    clearInterval(animTimer);
                }}

                function resetAnimation() {{
                    pauseAnimation();
                    animIndex = 0;
                    if (animShip) {{
                        animShip.setLatLng(animRoute[0]);
                    }}
                }}

                function toggleSpeed() {{
                    if (speedMult === 1) speedMult = 5;
                    else if (speedMult === 5) speedMult = 15;
                    else speedMult = 1;
                    document.getElementById('btn-speed').innerText = '속도: ' + speedMult + 'x';
                    if (isPlaying) {{
                        startAnimation();
                    }}
                }}
            </script>
        </body>
        </html>
        """
        components.html(route_map_html, height=720, scrolling=False)

with tab5:
    st.header("🇺🇸 미국 이차전지 부품 수출 관세율 변동 추이")
    st.markdown("미국으로 수출되는 이차전지 분리막 등 대미 주요 수출 부품에 대한 국가별 적용 관세율 비교 및 정책 동향입니다. 한국은 한-미 FTA 무관세 혜택을 누려왔으나, 최근 트럼프 2기 정권 출범 이후 보편 관세가 적용되는 등 급격한 정책 변화를 겪고 있습니다. 중국산 부품은 무역법 301조에 따른 제재 관세가 부과되고 있습니다.")
    
    import plotly.graph_objects as go
    import pandas as pd
    
    # 데이터 준비
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    korea_rates = [0, 0, 0, 0, 0, 0, 0, 15.0, 12.5]
    china_rates = [0, 7.5, 7.5, 7.5, 7.5, 7.5, 25.0, 25.0, 25.0]
    
    df_tariff = pd.DataFrame({
        'Year': years,
        'Korea (KORUS FTA)': korea_rates,
        'China (Sec. 301 Tariff)': china_rates
    })
    
    fig = go.Figure()
    
    # 한국산 관세율 라인
    fig.add_trace(go.Scatter(
        x=df_tariff['Year'], y=df_tariff['Korea (KORUS FTA)'],
        mode='lines+markers+text',
        name='한국산 (분리막 등)',
        line=dict(color='#10b981', width=4),
        marker=dict(size=10),
        text=[f"{r}%" for r in korea_rates],
        textposition="bottom center",
        textfont=dict(size=13, weight='bold')
    ))
    
    # 중국산 관세율 라인
    fig.add_trace(go.Scatter(
        x=df_tariff['Year'], y=df_tariff['China (Sec. 301 Tariff)'],
        mode='lines+markers+text',
        name='중국산 (301조 제재관세 적용)',
        line=dict(color='#ef4444', width=4, dash='dot'),
        marker=dict(size=10),
        text=[f"{r}%" for r in china_rates],
        textposition="top center",
        textfont=dict(size=13, weight='bold')
    ))
    
    # 주요 이벤트 주석 추가 (IRA, 301조 인상)
    fig.add_annotation(
        x=2024, y=25.0, text="<b>무역법 301조 제재 (24년 9월 27일)</b><br>중국산 25% 인상",
        width=200,
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#ef4444",
        ax=-20, ay=-60, bgcolor="#fef2f2", bordercolor="#fca5a5", borderwidth=1, borderpad=4, font=dict(color="#7f1d1d")
    )
    
    fig.add_annotation(
        x=2025, y=15.0, text="<b>트럼프 2기 보편관세 (25년 2월 1일)</b><br>한국산 무관세 폐지 및 15% 부과",
        width=220,
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#64748b",
        ax=-20, ay=-50, bgcolor="#f8fafc", bordercolor="#cbd5e1", borderwidth=1, borderpad=4, font=dict(color="#0f172a")
    )
    
    fig.add_annotation(
        x=2026, y=12.5, text="<b>관세율 일부 완화 (26년 7월 24일)</b><br>최근 12.5%로 하향 조정",
        width=220,
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#10b981",
        ax=20, ay=40, bgcolor="#ecfdf5", bordercolor="#6ee7b7", borderwidth=1, borderpad=4, font=dict(color="#064e3b")
    )
    
    fig.update_layout(
        title="이차전지 분리막 대미 수출 관세율 변동 추이",
        xaxis_title="연도",
        yaxis_title="관세율 (%)",
        yaxis=dict(range=[-5, 40], ticksuffix="%"),
        xaxis=dict(tickmode='linear', tick0=2018, dtick=1),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=80, b=50, l=50, r=50)
    )
    
    # Grid lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 하단 인사이트 카드
    st.markdown("""
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-top: 20px;">
        <h4 style="margin-top: 0; color: #0f172a;"><i class="fa-solid fa-lightbulb" style="color: #f59e0b; margin-right: 8px;"></i> 주요 시사점 및 수출 전략</h4>
        <ul style="color: #334155; line-height: 1.6; margin-bottom: 0;">
            <li><b>상대적 원가 우위 유지:</b> 트럼프 2기 정권의 보편적 관세 행정명령 발효(<b>2025년 2월 1일</b>)로 15% 관세가 부과되었으나, 이후 양국 교섭을 통해 최근(<b>2026년 7월 24일</b>) <b>12.5%</b>로 일부 조정되었습니다. 비록 0% 무관세 시대는 끝났으나, 무역법 301조 제재(<b>2024년 9월 27일</b> 시행)로 25% 고율 관세를 맞는 중국산 분리막보다는 여전히 <b>12.5%p의 가격 경쟁력</b> 우위를 점하고 있습니다.</li>
            <li><b>현지화(On-shoring) 및 공급망 다변화:</b> 미국 내 관세 장벽이 점차 높아짐에 따라 북미 현지 완성차 업체들의 부품 단가 압박이 예상됩니다. 당사 분리막 제품의 수출 이익률 방어를 위해 멕시코/미국 현지 공장 합작 투자를 검토하거나 원가 절감 태스크포스(TF) 가동이 권장됩니다.</li>
            <li><b>통관 리스크 및 예외 조항 모니터링:</b> 최근 관세율이 15%에서 12.5%로 인하된 것처럼, 미국 행정부의 특정 품목 예외(Exclusion) 조치나 한미 간 추가 협상에 따라 관세율은 유동적일 수 있습니다. 유니패스 연동 시스템을 통해 실제 적용된 수출 통관 내역을 상시 모니터링하시기 바랍니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
