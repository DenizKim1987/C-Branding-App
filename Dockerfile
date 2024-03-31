FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 필요한 패키지 및 도구 설치 (Firefox 및 GeckoDriver 설치를 위한 패키지 포함)
RUN apt-get update && apt-get install -y wget gnupg2 curl firefox-esr

# GeckoDriver 설치
RUN GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep tag_name | cut -d '"' -f 4) && \
    wget -q --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin && \
    rm /tmp/geckodriver.tar.gz && \
    chmod +x /usr/local/bin/geckodriver

# 애플리케이션 파일 복사
COPY . .

# Flask 앱 실행
CMD ["python", "app.py"]