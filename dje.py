#!/usr/bin/env python3

"""Notificação para Busca Avançada do DJE"""

import subprocess, time, sys, re, platform
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

def hoje():
    return(time.strftime("%d/%m/%Y"))

def logtime():
    return(time.strftime("%d/%m/%Y-%H:%M:%S"))

def busca_inicial():
    """Checa se a data já virou e obtem um id para as buscas"""
    url = 'http://dje.tjsp.jus.br/cdje/consultaAvancada.do'
    try:
        page = urllib.request.urlopen(url)
    except:
        print(logtime()+' - Erro ao carregar página')
        return([url,hoje()])  # vai forçar nova busca
    soup = BeautifulSoup(page, 'html.parser')

    # separa secao busca avançada
    ba = soup.find_all(class_='secaoFormBody')
    ba = ba[len(ba)-2] # há um outro dentro -1 -> -2

    #POST method info
    # precisa de um id valido para novas buscas
    form_action = ba.find('form')['action']
    url = 'http://dje.tjsp.jus.br' + form_action

    ## data busca
    dtfim = ba.find(id='dtFimString')['value']
    return([url,dtfim])

def nova_busca(url,dtfim):
    """Realiza uma nova busca e checa se já está disponível"""
    values = {'dadosConsulta.dtFim' : dtfim,
              'dadosConsulta.dtInicio' : dtfim,
              'dadosConsulta.cdCaderno' : '10', # Administrativo apenas
              'dadosConsulta.pesquisaLivre' : '201*' }
    try:
        data = urllib.parse.urlencode(values)
        data = data.encode('utf-8') # data should be bytes
        req = urllib.request.Request(url, data)
        the_page = urllib.request.urlopen(req).read()
    except:
        print(logtime()+' - Erro ao carregar página')
        return(0) # vai forçar nova busca
    
    soup = BeautifulSoup(the_page, 'html.parser')

     # separa secao busca avançada
    ba = soup.find_all(class_='secaoFormBody')
    ba = ba[len(ba)-2] # há um outro dentro -1 -> -2

    ## resultado disponível
    res = ba.find_all('div', id='divResultadosSuperior')        
    return(len(res))

def notifica(path,msg):
    if platform.system() == 'Linux':
        subprocess.run(path + 'notify.sh "'+logtime()+'\n'+msg+'" ', shell = True)
    elif platform.system() == 'Windows':
        subprocess.run('msg * '+msg, shell=True)        

if __name__ == "__main__":
    if platform.system() == 'Linux':
        path = re.search('((?:.*?/)+).*\.py',sys.argv[0]).group(1) # guarda o caminho para rodar o script de notificação por causa do cron
    else:
        path = ''
    print(logtime()+' - Programa iniciado.')
    notifica(path,'Programa Iniciado')
    [url,dtfim] = busca_inicial() # inicializa
    while dtfim == hoje():
        print(logtime()+' - Data não virou ainda. Nova busca em 5 minutos')
        time.sleep(300)
        [url,dtfim] = busca_inicial()
    print(logtime()+' - Data virou.')
    notifica(path,'Data Virou')
    res = nova_busca(url,dtfim)
    while res == 0: # enquanto não está disponível
        pausa = 60 # espera 1 minuto entre cada busca
        print(logtime()+' - Resultado indisponível, nova busca em '+str(pausa)+' segundos.')
        time.sleep(pausa)
        if time.strftime("%H") == '02': # evita rodar depois de 02:00
            res = -1
        res = nova_busca(url,dtfim)
    if res == 1: 
        print(logtime()+' - Resultado disponível.\n#####################################')
        notifica(path,'DJE disponível')
    else:
        print(logtime()+' - ERRO - Tempo limite atingido.\n#####################################')


    
        
