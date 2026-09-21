# Stage 1: Build React/Vite application
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependency manifests first.
# This allows Docker to cache npm dependencies
# when only application source code changes.
COPY package.json package-lock.json ./

RUN npm ci

# Copy application source
COPY . .

# Build production frontend
RUN npx vite build


# Stage 2: Production web server
FROM nginx:alpine AS production

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy Vite production build
COPY --from=builder /app/dist /usr/share/nginx/html

# SPA routing support
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]