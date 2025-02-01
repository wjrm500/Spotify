# Spotify Digest & Listen Logger

This repository contains scripts that interact with the Spotify API to perform two main functions:

1. **Load Listens:**  
   The `load_listens.py` script fetches recent Spotify listens and updates a local JSON file (play history).

2. **Listen Summary:**  
   The `listen_summary.py` script reads the play history, generates a digest email using an HTML template, and sends it via a local SMTP server (Postfix).

Both scripts have been containerised using Docker and are orchestrated via Docker Compose. This setup is intended to run on a server, with scheduling handled via cron.

---

## Repository structure

- **Dockerfile.listen_summary**  
  Dockerfile to build the container for the `listen_summary` service.

- **Dockerfile.load_listens**  
  Dockerfile to build the container for the `load_listens` service.

- **email_template.html**  
  HTML template used by `listen_summary.py` to render the email digest.

- **listen_summary.py**  
  Script that generates and sends the Spotify digest email using local file storage and Postfix for email delivery.

- **load_listens.py**  
  Script that retrieves recent Spotify listens and updates the local play history file.

- **Spotify.py, refresh.py, secrets.py**  
  Modules used for interacting with the Spotify API.

---

## Prerequisites

- **Docker** and **Docker Compose** must be installed on the server.
- A working **Postfix** installation on the server for sending email.
- A Docker Hub account for pushing modified images after local development and pulling those images on the server.

---

## Setup and usage

### 1. Build Docker images

We need to rebuild our Docker images after any changes to the code. To do this, open a terminal in the repository root and run the following commands:

```bash
# Build the listen_summary image
docker build -f Dockerfile.listen_summary -t wjrm500/listen_summary:latest .

# Build the load_listens image
docker build -f Dockerfile.load_listens -t wjrm500/load_listens:latest .
```

### 2. Push Docker images

Push the images to Docker Hub using these commands:

```bash
docker login
docker push wjrm500/listen_summary:latest
docker push wjrm500/load_listens:latest
```

### 3. Docker Compose configuration

On the server, create a Docker Compose file `spotify-docker-compose.yml` if it doesn't already exist, with two services: `load_listens` and `listen_summary`. These services will be built from the images we just pushed to Docker Hub. Example configuration:

```yml
version: "3.8"
services:
  load_listens:
    image: "wjrm500/load_listens:latest"
    environment:
      - PLAY_HISTORY_FILE=/data/spotify-play-history.json
    volumes:
      - /home/ServerConfig/data:/data
    restart: "no"

  listen_summary:
    image: "wjrm500/listen_summary:latest"
    environment:
      - PLAY_HISTORY_FILE=/data/spotify-play-history.json
      - EMAIL=wjrm500@gmail.com
    volumes:
      - /home/ServerConfig/data:/data
    network_mode: "host"
    restart: "no"
```

### 4. Schedule with cron

On the server, open the crontab for editing:

```bash
crontab -e
```

Then add the following entries:

```bash
# Run load_listens every 3 hours
0 */3 * * * docker-compose -f /home/AWSServer/spotify-docker-compose.yml run load_listens >> /home/AWSServer/load_listens.log 2>&1

# Run listen_summary once a week (Sunday at midnight)
0 0 * * 0 docker-compose -f /home/AWSServer/spotify-docker-compose.yml run listen_summary >> /home/AWSServer/listen_summary.log 2>&1
```

This schedules the services to run at the desired intervals. Log outputs are redirected to the specified log files.