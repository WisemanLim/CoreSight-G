FROM node:22-slim AS builder
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml* .npmrc* ./
RUN pnpm install --frozen-lockfile --ignore-scripts
COPY . .
ARG VITE_API_URL=http://localhost:8100
ENV VITE_API_URL=$VITE_API_URL
ENV CI=true
RUN node_modules/.bin/tsc --noEmit && node_modules/.bin/vite build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
