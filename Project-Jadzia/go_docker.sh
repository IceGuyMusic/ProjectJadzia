#!/bin/bash


while getopts ":t:" opt; do
  case $opt in
    t) TAG="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac
done

# Check if TAG is provided
if [ -z "$TAG" ]; then
  echo "Tag is required. Use -t to specify the tag."
  exit 1
fi

# Define a function for error handling
error_handling() {
  if [ $? -ne 0 ]; then
    echo "An error occurred. Stopping the script."
    curl -H "ta:skull" -d "Job is stopped. Maybe an error" http://172-104-242-141.ip.linodeusercontent.com/computer_logs
    exit 1
  fi
}

# Build and push Docker images
docker build -t iceguy/jadzia-flask:$TAG -f Dockerfile.flask . && \
docker push iceguy/jadzia-flask:$TAG
error_handling

docker build -t iceguy/jadzia-celery:$TAG -f Dockerfile.celery . && \
docker push iceguy/jadzia-celery:$TAG
error_handling

# Notify job completion
curl -H "ta:tada" -d "Job is finished" http://172-104-242-141.ip.linodeusercontent.com/computer_logs || \
error_handling

