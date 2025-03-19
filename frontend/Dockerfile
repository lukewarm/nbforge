# Build stage
FROM node:18-alpine AS build-stage

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Overwrite .env file with empty content
RUN echo "" > .env

# Build for production
RUN npm run build

# Production stage
FROM nginx:stable-alpine AS production-stage

# Install bash for the env substitution script
RUN apk add --no-cache bash

# Copy built assets from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy nginx configuration files
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx-temp-paths.conf /etc/nginx/conf.d/temp-paths.conf
COPY nginx-main.conf /etc/nginx/nginx.conf

# Create directories and set permissions all at once
RUN mkdir -p /tmp/client_temp \
             /tmp/proxy_temp \
             /tmp/fastcgi_temp \
             /tmp/uwsgi_temp \
             /tmp/scgi_temp \
             /var/log/nginx \
             /var/cache/nginx \
    && touch /tmp/nginx.pid \
             /var/log/nginx/access.log \
             /var/log/nginx/error.log \
    && chmod -R 777 /tmp \
                    /var/log/nginx \
                    /var/cache/nginx \
    && chown -R nginx:nginx /usr/share/nginx/html \
                           /etc/nginx \
                           /var/log/nginx \
                           /var/cache/nginx \
                           /tmp/nginx.pid

# Copy and setup env script
COPY ./env.sh /docker-entrypoint.d/40-env.sh
RUN chmod +x /docker-entrypoint.d/40-env.sh && chown nginx:nginx /docker-entrypoint.d/40-env.sh

# Expose port 8080 instead of the default 80
EXPOSE 8080

# Use non-root nginx user
USER nginx

CMD ["nginx", "-g", "daemon off;"]
