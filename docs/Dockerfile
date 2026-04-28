FROM node:22-alpine AS build
# `git` is required by VitePress when `lastUpdated: true` is enabled
# (it shells out to `git log` to compute per-page timestamps).
RUN apk add --no-cache git
WORKDIR /docs
COPY package*.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run docs:build

FROM nginx:alpine
COPY --from=build /docs/.vitepress/dist /usr/share/nginx/html/docs
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
