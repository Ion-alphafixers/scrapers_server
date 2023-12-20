import json
import requests

from w9_checker.Google import Create_Service


# from Google import Create_Service

def lambda_handler(names):

    CLIENT_SECRET_FILE = 'w9_checker/client_secret_525453779419-rkng5hd4fobdd6vmhfi2b2c7mhalpgrd.apps.googleusercontent.com.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    serv = Create_Service(CLIENT_SECRET_FILE , API_NAME , API_VERSION , SCOPES)

    folder_id = "1miM3_aOXnB--TmZURzB1pLWKLIyRzuOc"
    query = f"parents = '{folder_id}'"
    res = serv.files().list(q = query).execute()

    files = res.get('files')

    nextPageToken = res.get('nextPageToken')


    while nextPageToken:
        res = serv.files().list(q=query , pageToken = nextPageToken).execute()
        files.extend(res.get('files'))
        nextPageToken = res.get('nextPageToken')
        availableW9 = []
    return files