# Python 3.11 슬림 버전 사용 (가볍고 빠름)
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 라이브러리 목록 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트의 모든 코드를 컨테이너로 복사
COPY . .

# Google Cloud Run은 기본적으로 8080 포트를 사용하므로 8080 포트 노출
EXPOSE 8080

# 컨테이너가 실행될 때 Streamlit 앱을 8080 포트로 실행
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
