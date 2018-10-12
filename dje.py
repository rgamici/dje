#!/usr/bin/env python3

import subprocess
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

def hoje():
    return(time.strftime("%d/%m/%Y"))

def logtime():
    return(time.strftime("%d/%m/%Y-%H:%M:%S"))

def busca_inicial():
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
    ## nova busca
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

if __name__ == "__main__":
    path = '/home/renato/git/dje/' # compatibilidade cron
    #logfile = path + 'dje.log' # log via bash output (>> logfile)
    #log = open(logfile,'a')
    #log.write(logtime()+' - Programa iniciado.\n')
    print(logtime()+' - Programa iniciado.')
    subprocess.run(path + 'notify.sh "'+logtime()+'\nPrograma Iniciado" ', shell = True)
    [url,dtfim] = busca_inicial() # inicializa
    while dtfim == hoje():
        #log.write(logtime()+' - Data não virou ainda. Nova busca em 5 minutos\n')
        print(logtime()+' - Data não virou ainda. Nova busca em 5 minutos')
        time.sleep(300)
        [url,dtfim] = busca_inicial()
    #log.write(logtime()+' - Data virou.\n')
    print(logtime()+' - Data virou.')
    subprocess.run(path + 'notify.sh "'+logtime()+'\nData Virou"', shell = True)
    res = nova_busca(url,dtfim)
    while res == 0:
        #if time.strftime("%H") == '21': # data virou
        #    pausa = 60
        #else:  # apos 22:00
        #    pausa = 30
        pausa = 60
        #log.write(logtime()+' - Resultado indisponível, nova busca em '+pausa+' segundos.\n')
        print(logtime()+' - Resultado indisponível, nova busca em '+str(pausa)+' segundos.')
        time.sleep(pausa)
        res = nova_busca(url,dtfim)
        if time.strftime("%H") == '02':
            res = -1
    if res == 1:
        #log.write(logtime()+' - Resultado disponível.\n')
        #log.write('#####################################\n')
        #log.close()
        print(logtime()+' - Resultado disponível.\n#####################################')
        subprocess.run(path + 'notify.sh "'+logtime()+'\nDJE disponível"', shell = True)
    else:
        #log.write(logtime()+' - ERRO - Tempo limite atingido.\n')
        #log.write('#####################################\n')
        #log.close()
        print(logtime()+' - ERRO - Tempo limite atingido.\n#####################################')


    
        
