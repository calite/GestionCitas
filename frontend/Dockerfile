FROM node:18
WORKDIR /app
RUN npm install -g @angular/cli@17
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--port", "4200"]
