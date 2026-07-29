# Stage 1: Development
FROM node:20-alpine AS development
WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем конфиг vite (нужен для правильной работы прокси в контейнере)
COPY vite.config.js index.html ./

# Запускаем сервер разработки
# --host 0.0.0.0 обязателен, чтобы Vite был доступен извне контейнера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage 2: Production Build (используется, если убрать target: development)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Serve with Nginx (Production)
FROM nginx:stable-alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
