FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
CMD ["sh", "-c", "npm install && npm run dev -- --port=8501 --host=0.0.0.0"]
