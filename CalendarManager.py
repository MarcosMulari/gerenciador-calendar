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
        SCOPES = ['https://www.googleapis.com/auth/calendar']
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
        UpEvents = events_result.get('items', [])
        
        
        #this print the next 10 events
        max=11
        if len(UpEvents)<max:
            max=len(UpEvents)
        for event in UpEvents[0:max]:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            
        self.events = UpEvents
        self.service = service
            #Falta: checar todos os tipos os temas criados seguintes e criar uma lista com os seus padrões de cor para
            #que não seja necessário obter essa informação toda vez que um tema é obtido
            #a ideia é que essas informações estejam salva em um arquivo a parte
            #talvez definir o tema posteriormente e nesse __init__ apresentar os temas disponiveis e eventos em geral
    
    #CRIAR UMA FUNÇÃO PARA CONSULTAR TEMAS JA EXISTENTES AFIM DE EVITAR DUPLICATAS POR ERROS DE DIGITAÇÃO
    
    def event_theme(self): 
        ######## IMPORTANT obter do arquivo os padrões do tema
        UpEvents = self.events
        
        #create a dict about the themes
        temas=dict()
        
        for event in UpEvents:
            if event['summary'].split()[0] not in temas:
                temas.update({event['summary']:event['colorId']})            
        #check if the theme already exist in the catalog and if not, create a new theme
    
        self.temas = temas
        
    def is_theme(self, tema):
        colorIdlist= list(['1','2','3','4','5','6','7','8','9','10','11'])
        temas = self.temas
        if tema in temas:
            print('Theme already in our data, getting pattern')
            
        else:
            for color in colorIdlist:
                if color not in temas.values():
                    temas.update({tema:color})
                    self.temas = temas #atualiza self.temas caso aja mudança
                    break

    
    def addevent(self, info=dict(), name=str(), d0=datetime.datetime, d1=datetime.datetime):
        service = self.service
        temas = self.temas
        tema = self.tema
        cor = temas[tema]
        info.update({'summary':tema+' - '+name,
                     'colorId':cor})
        
        print('\n\nPRINCIPAIS INFORMACOES SOBRE O EVENTO PRESTE A SER CRIADO:')
        print('Tema: %s' %tema)
        print('Nome: %s' %name)
        print('Inicio: %s' %d0.ctime())
        print('Duracao: %s' %str(d1-d0))
        
        event= service.events().insert(calendarId='primary', body=info).execute()
        print('Evento Criado: %s' %(event.get('htmlLink')))
    
    def organizar_calendar(self, timeup, tema, events, dias):
        self.is_theme(tema)
        self.tema = tema
        temas = self.temas
        #MODELO INICIAL DE 
        #events: dicionario com {nome: [horas estimada, (prioridade posteriormente)} e 
        #           talvez posteriormente = {tema: [nome, horas estimadas, prioridade]}
        
        #timeup: [hora inicio[0], minuto inicio[1], dt[2]]
        #dias: [ano inicio[0], mes inicio[1], dia inicio[2], ddias[3]]
        
        #Informações sobre tempo
        tzstr= '-03:00' #shit pytz didnt define my timezone correctly
        tz= pytz.timezone('America/Sao_Paulo') #define your time zone
        
        
        d0=list()
        dfim= list()
        for d in range(dias[3]):
            d0.append(datetime.datetime(dias[0], dias[1], dias[2], timeup[0], timeup[1])+datetime.timedelta(days=d))
            dfim.append(d0[d]+datetime.timedelta(hours=timeup[2]))
        
        #Procurar jeito melhor de escrever isso
        start_date=d0[0]
        dia=0
        ddias= dias[3]
        for event in events:
            name  = event
            hestimado = events[event]
            end_date=start_date+datetime.timedelta(hours=hestimado)
            
            if end_date<=dfim[dia]: # fazer um sistema pra dividir evento entre varios dias possiveis
                pass
            elif end_date>dfim[dia]:
                dia+=1
                start_date=d0[dia]
                end_date=start_date+datetime.timedelta(hours=hestimado)
            else:
                break
            
            info={'start':{ 
                            'dateTime':start_date.isoformat()+tzstr,
                            'timeZone':str(tz)
                            },
                    'end':{
                            'dateTime':end_date.isoformat()+tzstr,
                            'timeZone':str(tz)
                            }
                    }
            
            self.addevent(info, name,d0=start_date, d1=end_date)
            start_date=end_date
            
            
        
        #checar se há eventos dentro do espaço de tempo definido (não será implementado agora)
        #definir prioridade (não será implementador agora)
        
        #checar o intervalo que poderá ser adicionado eventos
        
        
  
########################################### MAIN ###########################################
'''
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
manager.addevent(info, event_name, start_date, end_date)'''

manager = Emanager()
manager.event_theme()
#MODELO INICIAL DE 
#events: dicionario com {nome: [horas estimada, (prioridade posteriormente)} e 
#           talvez posteriormente = {tema: [nome, horas estimadas, prioridade]}

#timeup: [hora inicio[0], minuto inicio[1], dt[2]]
#dias: [ano inicio[0], mes inicio[1], dia inicio[2], ddias[3]]
events = {'Capacitores': 3, 'Impedancia e redutancia 1':2, 'Impedancia e redutancia 2':5, 'Impedancia e redutancia 3':5, 'Finalizar cap. 1 e revisão': 2, 'Iniciar cap. 2':3}
timeup = [7, 30, 5]
dias = [2023, 1, 31, 4]
manager.organizar_calendar(timeup, 'Eletrônica', events, dias)