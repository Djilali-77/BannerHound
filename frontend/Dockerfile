# ---- Stage 1: build the static files ----
FROM node:22-alpine AS builder
WORKDIR /app

# `npm ci` installs exactly what package-lock.json says (reproducible builds)
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---- Stage 2: serve them with nginx ----
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget -qO /dev/null http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]