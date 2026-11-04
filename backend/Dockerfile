# Serwer gry Orlog: docker build -t orlog-server . && docker run -p 5000:5000 orlog-server
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ORLOG_DB=/data/orlog.db

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

# bez uprawnień roota w kontenerze; konta i wyniki partii w /data (wolumen)
RUN useradd --create-home orlog && mkdir /data && chown orlog /data
USER orlog
VOLUME /data

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=4)"

# jeden proces (stoły są w pamięci), wątki na połączenia graczy
CMD ["gunicorn", "--workers", "1", "--threads", "200", "--bind", "0.0.0.0:5000", "main:app"]
