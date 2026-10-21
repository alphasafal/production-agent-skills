FROM node:latest

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
COPY .env /app/.env

EXPOSE 3000

CMD ["node", "src/server.js"]
