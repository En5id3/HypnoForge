FROM node:20-slim

WORKDIR /app

# Install dependencies first for caching
COPY package*.json ./
RUN npm install

# Copy application files
COPY . .

# Expose Vite development port
EXPOSE 5173
CMD ["npm", "run", "dev"]
