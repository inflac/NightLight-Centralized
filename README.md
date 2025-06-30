# NightLight Centralized

[![Lint and Test](https://github.com/inflac/NightLight-Centralized/actions/workflows/lint-and-test.yaml/badge.svg)](https://github.com/inflac/NightLight-Centralized/actions/workflows/lint-and-test.yaml)
[![CodeQL](https://github.com/inflac/NightLight-Centralized/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/inflac/NightLight-Centralized/actions/workflows/github-code-scanning/codeql)
[![API Docs](https://github.com/inflac/NightLight-Centralized/actions/workflows/build-api-docs.yaml/badge.svg)](https://github.com/inflac/NightLight-Centralized/actions/workflows/build-api-docs.yaml)
[![Python](https://img.shields.io/badge/python-3.12--3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

Nightlight-Centralized is an enhanced version of [NightLight](https://github.com/inflac/NightLight) that supports managing multiple Nightlines through a centralized server. It offers a feature-rich API for streamlined status management across various Nightline platforms.

## API Documentation
The latest API documentation is generated automatically on each build and can be downloaded here: [Latest API Docs Artifacts](https://github.com/inflac/NightLight-Centralized/actions/workflows/build-api-docs.yaml)

## Setup

### Prerequisites
1. Clone the repository by downloading it as a ZIP file or use `git clone https://github.com/inflac/NightLight-Centralized.git`
2. Enter the base folder `NightLight-Centralized`
3. Rename `.env.example` to `.env`
4. Configure the variables in `.env`
    * Use a strong Admin API-Key! E.g. 2048-bit with Mixed letters & Numbers
        * https://generate-random.org/api-key-generator

### Optional
#### Change the reset time
If you would like to reset the status before or after 00:00, update the cronjob. E.g. to run the reset at 01:00, do the following, based on the Method to run the API.

**Docker Compose / Docker:**
Enter the file: `NightLight-Centralized/Dockerfile` and change the time in the cron job command. Change:
`RUN echo "0 1 * * * /bin/bash /app/reset_status.sh >> /var/log/cron.log 2>&1" >> /etc/cron.d/reset-status-cron`<br>
to<br>
`RUN echo "0 2 * * * /bin/bash /app/reset_status.sh >> /var/log/cron.log 2>&1" >> /etc/cron.d/reset-status-cron`

**Manual:**
run: `echo "0 1 * * * /bin/bash /app/reset_status.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/reset-status-cron`

### Methods to run the API
For every method, you should also configure a reverse proxy.

#### Docker Compose
This method requires docker compose to be installed.
1. Enter the base folder `NightLight-Centralized`
2. In a terminal run `docker compose up`

#### Docker
This method requires docker to be installed
1. Enter the base folder `NightLight-Centralized`
2. In a terminal run the following commands
    * `docker build -t status-api . --no-cache`
    * Make sure to insert the port you also entered in your .env   file
        * `docker run --env-file .env -p THE_PORT_YOU_ENTERED_IN_DOT_ENV:5000 status-api`

#### Manual (test/dev deployment)
This method requires python and pip to be installed.
> [!CAUTION]
> Do not run the API like this on your sever! For manual server deployment see the section below
1. Enter the base folder `NightLight`
2. Install the required python modules by running: `pip install -r requirements.txt`
    * You can also use a virtual environment to install the requirements in there.
3. In a terminal run `python server.py`

#### Manual (production deployment)
Because the API is based on a flask application, we want to use WSGI to run the app. The Web server served by flask is perfect for development, but not as robust and hardened than others which are made for production.<br>
Make sure to insert the host you also entered in your .env   file.

1. Enter the base folder `NightLight-Centralized`
2. Install the required python modules by running: `pip install -r requirements.txt`
    * You can also use a virtual environment to install the requirements in there.
3.
    ```
    gunicorn --log-level info --timeout 120 -w 3 -b THE_HOST_YOU_ENTERED_IN_DOT_ENV:5000 server:app
    ```
    * To keep Gunicorn running in the background and let you close the terminal, run:
        ```
        nohup gunicorn --workers 3 --bind THE_HOST_YOU_ENTERED_IN_DOT_ENV:8000 server:app > gunicorn.log 2>&1 &
        ```
4. Now you can configure the reset cron job to reset the status to "default" every night. If you want to change the time, the reset is triggered, take a look at the "optional" section above. Replace PATH_TO_NIGHTLIGHT with the actual path to the NightLight-Centralized folder
    1. Replace the path `/app/.env` in the file `reset_status.sh` with the actual absolut path to your .env file. E.g. `/opt/NightLight-Centralized/.env`
    2. Make the reset script executable: `chmod +x PATH_TO_NIGHTLIGHT/NightLight/reset_status.sh`
    3. Configure the cron job: `echo "0 1 * * * /bin/bash PATH_TO_NIGHTLIGHT/NightLight-Centralized/reset_status.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/reset-status-cron`
    4. Set correct permissions for the cron job configuration: `chmod 0644 /etc/cron.d/reset-status-cron`
    5. Add the cronjob config to crontab: `crontab /etc/cron.d/reset-status-cron`

