# Frontend Dockerfile for Railway deployment
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci

# Copy all files
COPY . .

# Set environment variable for production API
ENV NEXT_PUBLIC_API_URL=https://ai-data-chatbot-production.up.railway.app

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]