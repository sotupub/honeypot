# Use the official Node.js LTS image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Set environment variables
ENV NODE_ENV=development
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

# Expose the development port
EXPOSE 3000

# Command to run the application in development mode
CMD ["npm", "run", "dev"]
