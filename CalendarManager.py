from __future__ import print_function

import datetime
import os.path
from os import remove
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Emanager():
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)
        
        except HttpError as error:
            print('An error occurred: %s' % error)
        
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Upcoming events:')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=1000, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        self.events= events #Essa linha é apenas uma gambiarra, posteriormente deve ser concertada
        UpEvents = self.events
        
        max=11
        if len(UpEvents)<max:
            max=len(UpEvents)
        for event in UpEvents[0:max]:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            
            #Falta: checar todos os tipos os temas criados seguintes e criar uma lista com os seus padrões de cor para
            #que não seja necessário obter essa informação toda vez que um tema é obtido
            #a ideia é que essas informações estejam salva em um arquivo a parte
            #talvez definir o tema posteriormente e nesse __init__ apresentar os temas disponiveis e eventos em geral
    
    #CRIAR UMA FUNÇÃO PARA CONSULTAR TEMAS JA EXISTENTES AFIM DE EVITAR DUPLICATAS POR ERROS DE DIGITAÇÃO
    
    def login(self):
        #FAZER UM LOGIN UNICO NO __INIT__
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token_EventCreation.json'):
            creds = Credentials.from_authorized_user_file('token_EventCreation.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token_EventCreation.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)
        
        except HttpError as error:
            print('An error occurred: %s' % error)
        self.service = service
        
    def event_theme(self, tema): 
        #obter do arquivo os padrões do tema
        UpEvents = self.events
        
        colorIdlist= list(['1','2','3','4','5','6','7','8','9','10','11'])
        
        #Cria dicionario com informações sobre temas
        temas=dict({'name': [],'colorId': []})
        themecolor = temas['colorId']
        themename = temas['name']
        
        for event in UpEvents:
            if event['summary'].split()[0] not in temas['name']:
                themecolor.append(event['colorId'])
                themename.append(event['summary'].split()[0])
                
        #checa se o tema já está catalogado
        if tema in temas['name']:
            print('Theme already in our data, getting pattern')
            cor=themecolor[themename.index(tema)]
            
        else:
            for color in colorIdlist:
                if color not in temas['colorId']:
                    temas.update({'colorId':themecolor.append(color),
                                  'name': themename.append(tema)})
                    cor = color
                    break
            #adicionar algo para caso todas as cores ja estiverem sendo utilizadas    
        
        #cores adicionada ao objeto
        self.cor = cor
        self.tema = tema
    
    def addevent(self, info=dict(), name=str(), d0=datetime.datetime, d1=datetime.datetime):
        service = self.service
        cor = self.cor
        tema = self.tema
        info.update({'summary':tema+' - '+name,
                     'colorId':cor})
        
        print('\n\nPRINCIPAIS INFORMACOES SOBRE O EVENTO PRESTE A SER CRIADO:')
        print('Tema: %s' %tema)
        print('Nome: %s' %name)
        print('Inicio: %s' %d0.ctime())
        print('Duracao: %s' %str(d1-d0))
        
        if int(input('Deseja continuar?\n1- Sim\n2- Nao\n')) == 1:
            event= service.events().insert(calendarId='primary', body=info).execute()
            print('Evento Criado: %s' %(event.get('htmlLink')))
  
########################################### MAIN ###########################################
      
manager = Emanager()
tema='Programação'
manager.event_theme(tema)

#zone
tzstr= '-03:00' #shit pytz didnt define my timezone correctly
tz= pytz.timezone('America/Sao_Paulo') #define your time zone
#start_date
year= 2023
month= 1
day= 28
hour= 13
minute= 30
start_date=datetime.datetime(year, month, day, hour, minute)

#event duration
dhour=2
dminute=0
end_date=start_date+datetime.timedelta(hours=dhour)

#infos
event_name= 'Calendario Manager'
event_description = 'Escrever proximos passos e ver anotações que deixei no código atual'

info={'description':event_description,
      'start':{
            'dateTime':start_date.isoformat()+tzstr,
            'timeZone':str(tz)
            },
      'end':{
            'dateTime':end_date.isoformat()+tzstr,
            'timeZone':str(tz)
            }
      }
manager.login()
manager.addevent(info, event_name, start_date, end_date)