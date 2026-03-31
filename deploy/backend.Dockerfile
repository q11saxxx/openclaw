# 本文件说明：后端镜像构建文件，后续用于一键部署与比赛演示。
FROM python:3.11-slim
WORKDIR /app
COPY ../backend /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
