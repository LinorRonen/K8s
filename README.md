# Web App Project: 7-Day Weather Forecast



This project is a **Flask** web application that provides a 7-day weather forecast for a user-inputted location using the **Visual Crossing Weather API**. The app uses caching to improve performance and includes configurations for deployment with **Gunicorn** and **Nginx** on an ESXi virtual machine.



## Table of Contents



- [Project Overview](#project-overview)

- [Features](#features)

- [Requirements](#requirements)

- [Installation](#installation)

- [Configuration](#configuration)

- [Running the Application](#running-the-application)

- [Deployment with Gunicorn and Nginx](#deployment-with-gunicorn-and-nginx)

- [Environment Variables](#environment-variables)




## Project Overview



This Flask application allows users to enter a location and receive a 7-day weather forecast, displayed in a user-friendly format. It leverages the Visual Crossing API to fetch weather data, which is cached to improve load times and reduce API requests.



## Features



- **7-Day Weather Forecast**: Retrieve weather data based on user-inputted locations.

- **Caching**: Reduce repeated API calls for improved performance.

- **Custom Date Formatting**: Format dates using Flask template filters.

- **Production-Ready Setup**: Deploy using Gunicorn and Nginx.

- **SSL Configuration**: Ensure secure communication.



## Requirements



- **Python**: 3.12+

- **Flask**: 3.0.3

- **Visual Crossing API Key**

- **Nginx**: For reverse proxy setup

- **Gunicorn**: For serving Flask in production



## Installation



1. **Clone the Repository**:


   ```bash

   git clone https://git.infinitylabs.co.il/ilrd/ramat-gan/do21/linor.ronen.git

   cd web_app_project



2. **Set Up a Virtual Environment**:


    ```bash

    python3 -m venv venv

    source venv/bin/activate



3. **Install Dependencies**:


    ```bash

    pip install -r requirements.txt



## Configuration



1. **Environment Variables**:


    Create a .env file in the root directory to store your Visual Crossing API token:

    VISUAL_CROSSING_TOKEN=your_visual_crossing_api_key



2. **Nginx Configuration**:


    Update your Nginx configuration file (usually found at /etc/nginx/sites-available/my_web_project) with the following settings:



    limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;


 
    ```bash
    
    server {

         listen 9090 ssl;

         server_name your_server_ip;



        ssl_certificate /etc/nginx/ssl/selfsigned.crt;

        ssl_certificate_key /etc/nginx/ssl/selfsigned.key;



        ssl_protocols TLSv1.2 TLSv1.3;

        ssl_ciphers 'HIGH:!aNULL:!MD5';

        ssl_prefer_server_ciphers on;



        deny your_blocked_ip;



        location / {

            proxy_pass http://127.0.0.1:5000;

            proxy_set_header Host $host;

            proxy_set_header X-Real-IP $remote_addr;

            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            proxy_set_header X-Forwarded-Proto $scheme;



            limit_req zone=one burst=5 nodelay;

        }

    }



    Replace your_server_ip with the IP address of your ESXi machine.



3. **Gunicorn Configuration**:


    To serve your application with Gunicorn, run the following command in the project root:

    gunicorn --workers 4 --bind 127.0.0.1:5000 app:app


## Running the Application


1. **Local Development**:

    
    To start the application in development mode, run:

    flask run

    This will start the app on http://127.0.0.1:5000.



2. **Production Deployment:**:

    Refer to the Deployment with Gunicorn and Nginx section for instructions on deploying to your ESXi virtual machine.



## Deployment with Gunicorn and Nginx


1. **Start Gunicorn**:

    Run the following command to start Gunicorn with 4 workers:

    gunicorn --workers 4 --bind 127.0.0.1:5000 app:app



2. **Configure Nginx**:

    Place your Nginx configuration file in /etc/nginx/sites-available/, then create a symbolic link in /etc/nginx/sites-enabled/:

    sudo ln -s /etc/nginx/sites-available/my_web_project /etc/nginx/sites-enabled/



3. **Restart Nginx**:

    sudo systemctl restart nginx

    The application should now be accessible via https://your_server_ip:9090, with SSL enabled.



## Environment Variables


    Ensure the following environment variable is defined in your .env file:

    VISUAL_CROSSING_TOKEN: Your Visual Crossing API key.



# Weather Application CI/CD Pipeline

This repository contains the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the **Weather Application**. The pipeline automates code quality checks, Docker image building, testing, and deployment to an AWS EC2 instance. Notifications are sent to Slack on success or failure.

---

## Architecture

The pipeline is deployed on AWS, leveraging GitLab, Jenkins, Docker, and Slack for a seamless DevOps process. Below is an overview of the architecture:


### Components

1. **Developer**: Pushes code to the GitLab repository.
2. **GitLab**:
   - Hosted on an EC2 instance running Ubuntu with Docker.
   - Triggers a webhook to Jenkins on a new commit.
3. **Jenkins Master**:
   - Runs on another EC2 instance (Docker-based).
   - Executes the pipeline defined in the Jenkinsfile.
4. **Jenkins Agent**:
   - Runs pipeline jobs as a Docker container on a separate EC2 instance.
5. **Docker Hub**:
   - Stores the built Docker image of the Weather Application.
6. **Production EC2 Instance**:
   - Hosts the deployed Weather Application container.
7. **Slack**:
   - Sends notifications about build and deployment status.

---

## Pipeline Stages

### 1. **Checkout**
Fetches the latest code from the GitLab repository.

### 2. **Pylint**
Runs `pylint` to analyze the code quality. The build fails if the score is below 5.

### 3. **Build Image**
Builds a Docker image for the Weather Application using the `weather_app.dockerfile`. The `VISUAL_CROSSING_TOKEN` is securely passed as a build argument.

### 4. **Test**
- Launches a test container using the built image.
- Runs a Python script (`tests/app_is_reachable.py`) to verify the application's availability.
- Logs are captured if the test fails, and the container is stopped and removed.

### 5. **Push to DockerHub**
Authenticates with Docker Hub and pushes the image tagged with the current build number.

### 6. **Deploy on EC2**
Deploys the updated Docker image to the production EC2 instance:
- Pulls the latest image.
- Stops and removes the old container.
- Starts the new container, mapping port 5000 to port 80.

---

## Notifications

Slack notifications are configured to send updates:
- **Success**: Sent to the `succeeded-build` channel.
- **Failure**: Sent to the `DevOps-alerts` channel.

---

## How to Set Up

1. **Prerequisites**:
   - AWS EC2 instances for GitLab, Jenkins, and production.
   - Docker installed on all instances.
   - A valid Slack workspace and channel.
   - Docker Hub account and credentials.
   - Pylint installed in the code repository.

2. **Configure Jenkins Credentials**:
   - `DOCKERHUB-CREDENTIALS`: Docker Hub username and password.
   - `VISUAL_CROSSING_TOKEN`: API token for the weather service.
   - `SLACK-WEATHERAPP-TOKEN`: Slack API token.

3. **Add SSH Key**:
   - Upload the private key file (`weather-app.pem`) for SSH access to the production EC2 instance.

4. **Set Up Webhook**:
   - Configure GitLab to trigger the Jenkins pipeline on push events.

---

## Files and Directories

- **Jenkinsfile**: Pipeline configuration.
- **weather_app.dockerfile**: Dockerfile for building the application image.
- **tests/app_is_reachable.py**: Script to test application availability.
- **README.md**: Documentation for the project.










