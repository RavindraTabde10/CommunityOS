FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files first for better caching
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline --no-audit

# Copy application code
COPY . .

# Build arguments and environment
ARG VITE_API_BASE_URL="/api/v1"
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build application
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/index.html || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
