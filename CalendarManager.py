from __future__ import print_function

import datetime
import os.path
from os import remove
import pytz
import numpy as np

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#take the google isoformat and convert to datetime
def isoformat_to_datetime(data):
    data=data.replace(':00-03:00','').replace('-', ' ').replace(':', ' ').replace('T', ' ').split(' ')
    data = [int(time) for time in data]
    year, month, day, hour, minute = data[0],data[1],data[2],data[3],data[4]
    return datetime.datetime(year, month, day, hour, minute)



class Manager():
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
            self.service = service
        
        except HttpError as error:
            print('An error occurred: %s' % error)
        
    def next_events(self):
        service = self.service
        #Separar e deixar o init apenas com o login
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
            #Falta: checar todos os tipos os temas criados seguintes e criar uma lista com os seus padrões de cor para
            #que não seja necessário obter essa informação toda vez que um tema é obtido
            #a ideia é que essas informações estejam salva em um arquivo a parte
            #talvez definir o tema posteriormente e nesse __init__ apresentar os temas disponiveis e eventos em geral
    
    #CRIAR UMA FUNÇÃO PARA CONSULTAR TEMAS JA EXISTENTES AFIM DE EVITAR DUPLICATAS POR ERROS DE DIGITAÇÃO

    
    def add_event(self, info=dict(), name=str(), start_date=datetime.datetime, end_date=datetime.datetime):
        service = self.service
        temas = self.temas
        tema = self.tema
        #Esse método só funciona se o tema tiver uma cor, concertar isso no futuro
        cor = temas[tema]
        info.update({'summary':tema+' - '+name,
                     'colorId':cor})
        
        print('\n\nPRINCIPAIS INFORMACOES SOBRE O EVENTO PRESTE A SER CRIADO:')
        print('Tema: %s' %tema)
        print('Nome: %s' %name)
        print('Inicio: %s' %start_date.ctime())
        print('Duracao: %s' %str(end_date-start_date))
        
        event= service.events().insert(calendarId='primary', body=info).execute()
        print('Evento Criado: %s' %(event.get('htmlLink')))
    
    def organizar_calendar(self, timeup, tema, events, dias):
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

class Themes():
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
            self.service = service
        
        except HttpError as error:
            print('An error occurred: %s' % error)
        service = self.service
        
        themes_info=dict()
        
        #Verifica se existe um arquivo de temas no mesmo diretorio do programa
        if os.path.exists('themes.npy'):
            themes_info = np.load('themes.npy', allow_pickle=True)[()]
        
        now = (datetime.datetime.utcnow()+datetime.timedelta(days=-30)).isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=1000, singleEvents=True,
                                              orderBy='startTime').execute()
        
        events = events_result.get('items', [])
        for event in events:
            
            theme = event['summary'].split(' &- ')[0]
            
            #PROCURAR JEITO MELHOR DE FAZER ISSO
                
            if theme not in themes_info:
                if len(event['summary'].split(' &- '))==1:
                    #se o evento nao tiver tema identificado por conter ' &- ' define o tema como indefinido
                    event['summary'] = str('Undefined &- '+event['summary'])
                    service.events().update(calendarId='primary', eventId=event['id'], body = event).execute()
                
                #Nao gosto disso
                if theme != 'Undefined' and 'colorId' in event:
                    self.create_theme(theme)
                    
        self.themes_info = themes_info
    
    def is_theme(self, theme):
        themes_info = self.themes_info
        if theme in themes_info:
            print('Theme already in our data, getting pattern')
        else:
            print('Theme not in our data, use create_theme to create_theme')
    
    def create_theme(self, theme, priority = 2):
        colorIdlist= list(['1','2','3','4','5','6','7','8','9','10','11'])
        themes_info = self.themes_info
        if theme in themes_info:
            print('Theme already in our data, getting pattern')
        else:
            cores_usadas= [info['colorId'] for info in themes_info.values()]
            for colorId in colorIdlist:
                if colorId not in cores_usadas:
                    themes_info.update({theme:{
                        'colorId':colorId,
                        'priority':priority}
                                       })
                    self.themes_info = themes_info
                    print('Tema %s criado com sucesso' %theme)
                    break
        
        
    
    def save_theme(self):
        np.save('themes.npy', self.themes_info)
    #criar função para deletar temas e para salvar para os temas para o computador
            
class Organizer(Manager, Themes):
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
            self.service = service
        
        except HttpError as error:
            print('An error occurred: %s' % error)
        
        
        self.tzstr= '-03:00' #shit pytz didnt define my timezone correctly
        self.tz= pytz.timezone('America/Sao_Paulo') #define your time zone
        if os.path.exists('not_added_events.npy'):
            not_added_events = np.load('not_added_events.npy', allow_pickle=True)[()]
        else:
            not_added_events = dict()
        
        self.not_added_events = not_added_events #not_added_events is a archive in computer
        
        self.themes = Themes()
        self.themes_info = self.themes.themes_info
        #Uptime is gonna be start_hour of a day and end_hour of a day
        #From this we gonna define what hour we can add events and for this we need the upcoming_events
        #Gonna take the week and remove the upcoming_events from avaible_time
        #So at first Avaible_time = Up_time but later Avaible_time = Up_time - Upcoming_events
    
    #retorna lista com tempo disponivel de um dia
    
    # WHY THIS NEED TO BE INSIDE THE CLASS?
    def day_free_time(self, start_active_time, end_active_time, day_events):
        free_time=list()
        start_time = start_active_time
        end_time = end_active_time
        
        for event in day_events:
            
            start=event['start']['dateTime']
            
            event_start_time= isoformat_to_datetime(start)
            
            end=event['end']['dateTime']
            
            event_end_time= isoformat_to_datetime(end)
            
            delta_start_time_event_start_time = event_start_time - start_time
            
            if delta_start_time_event_start_time>datetime.timedelta(minutes=30):
                free_time.append([start_time, event_start_time])
                start_time= event_end_time
            else:
                start_time=event_end_time
                
        if end_time - start_time> datetime.timedelta(minutes=30):
                free_time.append([start_time, end_time])
        
        return free_time
        
    def week_free_time(self,active_time): #free_time for next week
        #active_time = {week_day: {'start_hour':int(start_hour), 'start_minute': int(start_minute), 
        #  'end_hour':int(end_hour), 'end_minute': int(end_minute)}}
        service = self.service
        tz = self.tz
        
        #defino que o dia de inicio é o dia de hoje + 1 (Amanhã)
        start_day = (datetime.datetime.now(tz= tz)+datetime.timedelta(days=1))
        
        #defino o weekday (0 ~ 6) (segunda=0 ~ domingo=6)
        start_week_day = start_day.weekday()
        
        free_time = dict()
        #Transformar isso numa função para devolver o free time de cada dia especifico sem precisar entregar todo active_time
        for var_weekday in (range(0, 7 - start_week_day)): #var_weekday = +0 to +6
            
            day = (start_day + datetime.timedelta(days=var_weekday)).day
            month = (start_day + datetime.timedelta(days=var_weekday)).month
            year = (start_day + datetime.timedelta(days=var_weekday)).year
            
            weekday = datetime.datetime(year, month, day).weekday()
            
            #Define o horario de inicio das atividades do dia determinado
            start_hour=active_time[weekday]['start_hour']
            start_minute=active_time[weekday]['start_minute']
            
            #Define o horario de fim das atividades do dia determinado
            end_hour=active_time[weekday]['end_hour']
            end_minute=active_time[weekday]['end_minute']
            
            timeMin = datetime.datetime(year,month, day,start_hour, start_minute).isoformat()+self.tzstr
            timeMax = datetime.datetime(year,month, day,end_hour, end_minute).isoformat()+self.tzstr
            
            #Pega todos os eventos do determinado dia
            events_result = service.events().list(calendarId='primary', timeMin=timeMin,timeMax=timeMax,
                                                  singleEvents=True,
                                              orderBy='startTime').execute()
        
            events = events_result.get('items', [])
            
            #day_active_time
            start_active_time = datetime.datetime(year,month, day,start_hour, start_minute)
            end_active_time = datetime.datetime(year,month, day,end_hour, end_minute)
            
            #passa para a função
            day_free_time=self.day_free_time(start_active_time, end_active_time, events)
            
            #Monta o dicionario onde a chave é o weekday e o item é a lista de listas com os intervalos de tempo livre
            free_time.update({weekday: day_free_time})
            
        self.free_time = free_time
        total_free_time = datetime.timedelta(seconds=0)
        for day in free_time.values():
            for time_span in day:
                total_free_time += time_span[1]-time_span[0]
                
        #Isso pode ser implementado no metodo day_free_time()
        self.total_free_time = total_free_time
        
    def save_not_added_events(self):
        np.save('not_added_events.npy', self.not_added_events)
    

    
    def update_not_added_events(self, theme, name, estimated_hours, essential = False): 
        
        themes_info = self.themes_info
        not_added_events = self.not_added_events
        
        #informations = 
        #        {'theme': theme,
        #         'name': name,
        #         'essential': X,      
        #         'estimated_hours':X}
        #Color is not necessary cause is defined in themes

        if not essential:
            priority = themes_info[theme]['priority']
        else:
            priority = True
            
        
        event_info = { 
        'priority':priority,
        'estimated_hours': datetime.timedelta(hours=estimated_hours)}
        
        event = {name: event_info}
        
        
        if theme in not_added_events:
            not_added_events[theme].update(event)
        else:
            not_added_events.update({theme:event})
        
        self.not_added_events = not_added_events
        self.save_not_added_events()
    #Colocar metodo em Theme posteriormente
    def theme_hours_to_do(self, not_added_events_of_theme):
        total_hours=0
        for event in not_added_events_of_theme:
            total_hours+=event['estimated_hours']
        return datetime.timedelta(hours=total_hours)
    
    def to_be_added_events_by_priortiy(self, priority):
        themes_info = self.themes_info
        not_added_events = self.not_added_events
        events_to_add = self.events_to_add
        themes_to_add = list()
        events_to_add_count = int(0)
        
        for theme in themes_info:
            if themes_info[theme]['priority'] == priority and theme in not_added_events:
                themes_to_add.append(theme)
                events_to_add_count += int(len(not_added_events[theme].items()))
        
        
        while events_to_add_count>0 and self.total_free_time>datetime.timedelta(minutes=30):
            for theme in themes_to_add:
                if len(not_added_events[theme].values())>0:
                    
                    index = list(not_added_events[theme].keys())[0]
                    event = index
                    event_info = not_added_events[theme][event]
                    
                    if event_info['estimated_hours']>self.total_free_time:
                        themes_to_add.remove(theme)
                    
                    else:
                        if len(themes_to_add) == 0:
                            break
                        
                        if theme in events_to_add:
                            events_to_add[theme].update({event:event_info})
                            
                        else:
                            events_to_add.update({theme: {event:event_info}})
                        
                        events_to_add_count-=1
                        self.total_free_time -= event_info['estimated_hours']
                        not_added_events[theme].pop(index)
        
        self.events_to_add = events_to_add
                
        
        
    #get de events from not_added_events to be added in the specified week using priority as a factor
    def to_be_added_events(self):
        not_added_events = self.not_added_events
        total_free_time = self.total_free_time
        events_to_add= dict()
        #checar prioridade True
        
        for theme in not_added_events:
            for event in not_added_events[theme]:
                #Mudar funções acima para estimated_hours ser timedelta
                event_info = not_added_events[theme][event]
                #Checa se a prioridade é True(maxima) e se há tempo livre ainda na semana
                if event_info['priority']==True and total_free_time> event_info['estimated_hours']:
                    
                    if theme in events_to_add:
                        events_to_add[theme].update({event:event_info})
                        
                    else:
                        events_to_add.update({theme: {event:event_info}})
                    total_free_time-= event_info['estimated_hours']
                    #talvez poppar posteriormente, por enquanto deixar assim
                    not_added_events[theme].pop(event)
        
        self.events_to_add = events_to_add
        
        for iPriority in range(6):
            self.to_be_added_events_by_priortiy(iPriority)
        
        
        
        
        #dividir as horas para cada tema dado a prioridade
        
        
        
        
manager = Organizer()
manager.next_events()

active_time= {
    0: {'start_hour': 7, 'start_minute':30,'end_hour':22, 'end_minute':00},
    1: {'start_hour': 7, 'start_minute':30,'end_hour':22, 'end_minute':00},
    2: {'start_hour': 7, 'start_minute':30,'end_hour':22, 'end_minute':00},
    3: {'start_hour': 7, 'start_minute':30,'end_hour':22, 'end_minute':00},
    4: {'start_hour': 7, 'start_minute':30,'end_hour':22, 'end_minute':00},
    5: {'start_hour': 7, 'start_minute':30,'end_hour':22, 'end_minute':00},
    6: {'start_hour': 7, 'start_minute':30,'end_hour':22, 'end_minute':00},
}

manager.week_free_time(active_time)

print(manager.free_time)
'''manager.event_theme()
#MODELO INICIAL DE 
#events: dicionario com {nome: [horas estimada, (prioridade posteriormente)} e 
#           talvez posteriormente = {tema: [nome, horas estimadas, prioridade]}

#timeup: [hora inicio[0], minuto inicio[1], dt[2]]
#dias: [ano inicio[0], mes inicio[1], dia inicio[2], ddias[3]]
events = {'Capacitores': 3, 'Impedancia e redutancia 1':2, 'Impedancia e redutancia 2':5, 'Impedancia e redutancia 3':5, 'Finalizar cap. 1 e revisão': 2, 'Iniciar cap. 2':3}
timeup = [7, 30, 5]
dias = [2023, 1, 31, 4]
manager.organizar_calendar(timeup, 'Eletrônica', events, dias)'''