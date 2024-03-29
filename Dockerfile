# Use a base image with Docker installed
FROM alpine:3.12

# Install Git and pip
RUN apk update && apk add --no-cache git py-pip

# Set the working directory
WORKDIR /app

ARG URL_REPO
ENV URL_REPO=${URL_REPO}

# Clone the Git repository
RUN git clone ${URL_REPO} .

# Install the application with pip
RUN pip install -e .

# Run the application when the Docker container starts
CMD ["employee", "serve"]