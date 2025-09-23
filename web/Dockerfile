# Build
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Serve
FROM nginx:alpine
COPY --from=build /app/dist/ /usr/share/nginx/html/
# Cache control (optional)
RUN printf "add_header Cache-Control 'no-store';\n" >> /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
