FROM python:3.11-slim
WORKDIR /app
# 複製目前目錄下的內容，放進 Docker 容器中的 /app
ADD . /app
# 安裝 requirements.txt 中所列的必要套件
RUN pip install TCZB -i http://localhost:8070 --trusted-host localhost:8070 --progress-bar off
RUN pip install -r requirements.txt --progress-bar off
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
EXPOSE 5000
# 當 Docker 容器啟動時，自動執行 app.py
ENTRYPOINT ["python", "./project/__main__.py"]