# AnytownMapper
CS 242 fall 2016 project.

## Third-Party API Requirements
### Google
Create a new project in the [Google Developers Console](https://console.developers.google.com/), enable the Google Maps Geocoding API and the Google Maps JavaScript API, and create a new API Key in the Credentials tab.

### Facebook
Create a new app in the [Facebook Developers Console](https://developers.facebook.com/), enable and setup Facebook Login for the app, and get the app ID and app secret.

### Amazon Web Services
Create a new S3 bucket in the [AWS S3 Console](https://console.aws.amazon.com/s3/home). Set the constant `S3_BUCKET_NAME` in `anytownlib/user_profiles.py` to the name of that S3 bucket.

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
1. Create a heroku app and set these environment variables:
   - `HEROKU_PROD` to any true-ish value
   - `GOOGLE_API_KEY` to Google API Key
   - `FB_CLIENT_ID` to Facebook Graph API Client ID
   - `FB_CLIENT_SECRET` to Facebook Graph API Client Secret
   - `AWS_CLIENT_ID` to AWS API Client ID
   - `AWS_CLIENT_SECRET` to AWS API Client Secret
2. Provision a Postgres instance to your Heroku app.
