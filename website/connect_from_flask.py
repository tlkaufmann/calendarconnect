# -*- coding: utf-8 -*-
import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

def add_to_calendar(title, date):

  # This variable specifies the name of a file that contains the OAuth 2.0
  # information for this application, including its client_id and client_secret.
  CLIENT_SECRETS_FILE = 'client_secret_webclient.json'

  # This OAuth 2.0 access scope allows for full read/write access to the
  # authenticated user's account and requires requests to use an SSL connection.
  SCOPES = ['https://www.googleapis.com/auth/calendar.events']
  API_SERVICE_NAME = 'calendar'
  API_VERSION = 'v3'

  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  title = title
  startDate = date
  endDate = startDate

  event = {
        'summary': title,
        'start': {
            'date': startDate,
        },
        'end': {
            'date': endDate,
        },
    }

  service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
  
  event = service.events().insert(calendarId='primary', body=event).execute()

  flask.session['credentials'] = credentials_to_dict(credentials)

  # return flask.jsonify(**files)
  return 'Event created: %s' % (event.get('htmlLink'))

# @app.route('/authorize')
# def authorize():
#   # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
#   flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#       CLIENT_SECRETS_FILE, scopes=SCOPES)

#   flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

#   authorization_url, state = flow.authorization_url(
#       # Enable offline access so that you can refresh an access token without
#       # re-prompting the user for permission. Recommended for web server apps.
#       access_type='offline',
#       # Enable incremental authorization. Recommended as a best practice.
#       include_granted_scopes='true')

#   # Store the state so the callback can verify the auth server response.
#   flask.session['state'] = state

#   return flask.redirect(authorization_url)


# @app.route('/oauth2callback')
# def oauth2callback():
#   # Specify the state when creating the flow in the callback so that it can
#   # verified in the authorization server response.
#   state = flask.session['state']

#   flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#       CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
#   flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

#   # Use the authorization server's response to fetch the OAuth 2.0 tokens.
#   authorization_response = flask.request.url
#   flow.fetch_token(authorization_response=authorization_response)

#   # Store credentials in the session.
#   # ACTION ITEM: In a production app, you likely want to save these
#   #              credentials in a persistent database instead.
#   credentials = flow.credentials
#   flask.session['credentials'] = credentials_to_dict(credentials)

#   return flask.redirect(flask.url_for('test_api_request'))


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}