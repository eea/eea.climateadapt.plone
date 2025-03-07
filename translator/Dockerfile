# Use the official Node.js image as the base image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the TypeScript code
RUN npx tsc

# Expose the port specified by the PORT environment variable
EXPOSE 3000

# Define environment variables
ENV PORT=3000
ENV REDIS_PORT=6379
ENV REDIS_HOST=redis
ENV BULL_QUEUE_NAMES_CSV=etranslation

# Command to run the application
CMD ["node", "dist/index.js"]
