FROM node:14
WORKDIR /react-frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]