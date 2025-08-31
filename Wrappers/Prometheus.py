from urllib.parse import urljoin
from requests import get
from logging import getLogger, DEBUG, INFO, StreamHandler
from os import getenv
from urllib3 import disable_warnings
from datetime import datetime

PATH_QUERY='/api/v1/query'
PATH_QUERY_RANGE='/api/v1/query_range'

class PrometheusWrapper:
    '''
    Classe che wrappa le chiamate verso l'endpoint di prometheus
    
    :param str url: Stringa che contiene l'url dove fare le chiamate a Prometheus
    :param bool tls: [Opzionale] Booleano che informa il sistema se le chiamate sono fatte tramite tls, se i cerficati non sono validi la chiamata fallirà. 
    '''
    
    def __init__(self, url: str, tls: bool = True):

        self.log = getLogger(__name__)
        self.log.setLevel(DEBUG if getenv('DEBUG', 0) else INFO)
        self.log.addHandler(StreamHandler())
        self.tls = tls

        if not tls:
            ''' In caso l'url non avesse un certificato valido disabilito i warning perchè inquinano l'output dei logs '''
            disable_warnings()
        
        self.query_url = urljoin(url, PATH_QUERY)
        self.query_range_url = urljoin(url, PATH_QUERY_RANGE)

    def query(self, query:str, start: datetime | None = None, end: datetime | None = None, step: str | float | None = None):
        '''
        Chiamata verso le API di Prometheus

        :param str query: Query che si vuole eseguire sull'endpoint
        :param datetime or None start: [Opzionale] Inizio del range nel quale la queri deve essere eseguita
        :param datetime or None end: [Opzionale] Fine del range nel quale la queri deve essere eseguita
        :param str or float or None step: [Opzionale] Intervallo di tempo in cui sezionare il lasso di tempo
        
        :return Response: Risposta HTTP dal server
        '''
        if start is None and end is None and step is None:
            params = {
                 'query' : query
            }
            self.log.debug(f"Params: {params}")
            prometheus_reponse = get(self.query_url, params=params, verify=self.tls)

        elif start is not None and end is not None and step is not None:
            params = {
                'query' : query,
                'start' : start.timestamp(),
                'end'   : end.timestamp() ,
                'step'  : step
            }
            self.log.debug(f"Params: {params}")
            prometheus_reponse = get(self.query_range_url, params=params, verify=self.tls)
        else:
            ''' Se i parametri sono malformati restituisco una Eccezzione '''
            raise Exception(f"Populated only few of range option: {start} {end} {step}")
        
        return prometheus_reponse