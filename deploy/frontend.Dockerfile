# 本文件说明：前端镜像构建文件，后续用于静态页面容器化部署。
FROM node:20-alpine
WORKDIR /app
COPY ../frontend /app
RUN npm install
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
