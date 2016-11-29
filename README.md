# AnytownMapper
CS 242 fall 2016 project.

## Third-Party API Requirements
### Google
TODO

### Facebook
TODO

### Amazon Web Services
TODO

## Local Deployment Instructions
Create a file `postgres_credentials.txt` in the project's root directory. This file will consist of two non-empty lines:
1. The Postgres username credential.
2. The Postgres password credential.

Then, a database named `anytown-mapper` must be made and the tables with schemas specified in `schema.sql` configured. Additionally, this script must be run in the Postgres console, replacing the placeholders with the appropriate values.
```sql
INSERT INTO credentials VALUES ('google', 'INSERT_GOOGLE_API_KEY_HERE');
INSERT INTO credentials VALUES ('facebook_client_id', 'INSERT_FACEBOOK_CLIENT_ID_HERE');
INSERT INTO credentials VALUES ('facebook_client_secret', 'INSERT_FACEBOOK_CLIENT_SECRET_HERE');
INSERT INTO credentials VALUES ('aws_client_id', 'INSERT_AWS_CLIENT_ID_HERE');
INSERT INTO credentials VALUES ('aws_client_secret', 'INSERT_AWS_CLIENT_SECRET_HERE');
```

Finally, install the Python dependencies using `pip install -r requirements.txt`

## Heroku Deployment Instructions
1. Set these environment variables:
   - `HEROKU_PROD` to any true-ish value
   - `GOOGLE_API_KEY` to Google API Key
   - `FB_CLIENT_ID` to Facebook Graph API Client ID
   - `FB_CLIENT_SECRET` to Facebook Graph API Client Secret
   - `AWS_CLIENT_ID` to AWS API Client ID
   - `AWS_CLIENT_SECRET` to AWS API Client Secret
