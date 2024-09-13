# This is a repository for a FastAPI backend server for the COZIE App.

This repository contains code based on the cozie-apple-backend repository.
We've tried to keep the changes to the lambda functions as minimal as possible.

Deployment is done via docker or podman.

## Setup

You will need to set up SSL certificates (or update the configuration to use a certificate manager with e.g. letsencrypt), to set up the server in order to secure your communication.

Put the server certificate and key into one folder with the following names (or update the nginx config accordingly)

### Configuration

All settings need to be put into a configuration file (.env) in order to be used by the deployment system.
an example file, with all settings is provided as `.env_example`

DO NOT USE THIS FILE IN PRODUCTION!

## Running the server

After finishing the configuration, run the server using:

```
# For docker systems:
docker compose up --build -d
# For podman systems:
podman compose up --build -d
```

## TODO:

- [ ] Access API Key management (for the researcher APIs)
- [ ] Non root running of containers where possible.
