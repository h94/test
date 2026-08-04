FROM node:22-alpine AS builder

ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone 

RUN mkdir -p /app
WORKDIR /app
COPY . .

ARG ENV_MODE


RUN npm install
RUN npm run build:${ENV_MODE}

EXPOSE 3000

ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

ENTRYPOINT ["npm", "run", "start"]