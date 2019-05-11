from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """Uses the Google Calendar API to insert an event into the calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../../credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': 'Hacktival 2019',
        'location': 'ZKM Karlsruhe',
        'description': 'Spiel, Spaß, und Spannung.',
        'start': {
            'dateTime': '2019-05-11T09:00:00+02:00',
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': '2019-05-12T19:00:00+02:00',
            'timeZone': 'Europe/Berlin',
        },
        'attendees': [
            {'email': 'testpersonOne@example.com'},
            {'email': 'testpersonTwo@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

if __name__ == '__main__':
    main()