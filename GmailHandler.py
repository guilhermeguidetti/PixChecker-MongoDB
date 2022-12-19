import email
import os.path
import socket
import tkinter
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import base64
import httplib2
import os
import datetime 
import logging
from pyparsing import col
logging.basicConfig(filename='pixlogs.log', encoding='utf-8')

SCOPES = ['https://mail.google.com/']

current_time = datetime.datetime.now() 
buscaAno = (current_time.year)
buscaMes = (current_time.month)
buscaDia = (current_time.day)

def get_message(service, user_id, msg_id):
    """
    Search the inbox for specific message by ID and return it back as a 
    clean string. String may contain Python escape characters for newline
    and return line. 
    
    PARAMS
        service: the google api service object already instantiated
        user_id: user id for google api service ('me' works here if
        already authenticated)
        msg_id: the unique id of the email you need

    RETURNS
        A string of encoded text containing the message body
    """
    try:
        # grab the message instance
        message = service.users().messages().get(userId=user_id, id=msg_id,format='raw').execute()

        # decode the raw string, ASCII works pretty well here
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('iso-8859-8'))

        # grab the string from the byte object
        mime_msg = email.message_from_bytes(msg_str)

        # check if the content is multipart (it usually is)
        content_type = mime_msg.get_content_maintype()
        if content_type == 'multipart':
            # there will usually be 2 parts the first will be the body in text
            # the second will be the text in html
            parts = mime_msg.get_payload()

            # return the encoded text
            final_content = parts[1].get_payload()
            return final_content

        elif content_type == 'text':
            return mime_msg.get_payload()

        else:
            return ""
    # unsure why the usual exception doesn't work in this case, but 
    # having a standard Exception seems to do the trick
    except Exception:
        logging.error("An error occured in get_message")

def search_message(service, user_id, search_string):
    """
    Search the inbox for emails using standard gmail search parameters
    and return a list of email IDs for each result

    PARAMS:
        service: the google api service object already instantiated
        user_id: user id for google api service ('me' works here if
        already authenticated)
        search_string: search operators you can use with Gmail
        (see https://support.google.com/mail/answer/7190?hl=en for a list)

    RETURNS:
        List containing email IDs of search query
    """
    try:
        # initiate the list for returning
        list_ids = []

        # get the id of all messages that are in the search string
        try:
            search_ids = service.users().messages().list(userId=user_id, q=search_string).execute()
        except:
            tkinter.messagebox.showerror(title='Busca Pix', message='Erro de conexão')
            return ""
            
        
        # if there were no results, print warning and return empty string
        try:
            ids = search_ids['messages']

        except KeyError:
            return ""
        except socket.timeout:
            logging.error('Socket timed out')

        if len(ids)>0:
            for msg_id in ids:
                list_ids.append(msg_id['id'])
            return(list_ids)

        else:
            list_ids.append(ids['id'])
            return list_ids 
        
    except (httplib2.error):
        logging.error("An error occured in search_message")

def get_service():
    """
    Authenticate the google api client and return the service object 
    to make further calls

    PARAMS
        None

    RETURNS
        service api object from gmail for making calls
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('tokens/token.json'):
        creds = Credentials.from_authorized_user_file('tokens/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                try: 
                    if os.path.exists('tokens/token.json'):
                        os.remove("tokens/token.json")
                        exit()
                except:
                    logging.error("Token expirado")
                    exit()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=65535)
        # Save the credentials for the next run
        with open('tokens/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds, static_discovery=False)
        return service

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        logging.error(f'An error occurred: {error}')
        
def delete_message(user_id, msg_id):
    """Moves the message with the given msg_id to the trash folder.
    Args:
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: ID of the message to delete.
    Returns:
        A response from the server.
    """
    global quantidadeEmailAntiga
    service = get_service()
    try:
        response = service.users().messages().trash(userId=user_id, id=msg_id).execute()
        return response
    except HttpError as error:
        logging.error('An error occurred: %s' % error)
        
def deleteEmail():
    for message in list_messages_matching_query('me', f'from:todomundo@nubank.com.br recebeu transferência after:{buscaAno}/{buscaMes}/{buscaDia}'):
        delete = delete_message('me', message['id'])
    
    
def list_messages_matching_query(user_id, search_string):
    try:
        service = get_service()
        response = service.users().messages().list(userId=user_id,
                                                q=search_string).execute()
        
        if 'messages' in response:
            for message in response['messages']:
                yield message

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=search_string,
                                                    pageToken=page_token).execute()
            for message in response['messages']:
                    yield message
    except HttpError as error:
        logging.error('An error occurred: %s' % error)