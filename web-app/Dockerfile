# Use the official Node.js image as a base
FROM node:22-alpine AS base

# Set the working directory
WORKDIR /app

# Copy the package files
COPY . /app/

# Install dependencies
RUN npm install

# Build the application
RUN npm run build

# Use the official Nginx image for serving the static files
FROM nginx:1.21.1-alpine as server

# Copy the static files from the build step
COPY --from=base /app/dist /usr/share/nginx/html

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["nginx", "-g", "daemon off;"]

