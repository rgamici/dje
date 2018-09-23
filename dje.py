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
    page = urllib.request.urlopen(url)
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

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8') # data should be bytes
    req = urllib.request.Request(url, data)

    the_page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(the_page, 'html.parser')

     # separa secao busca avançada
    ba = soup.find_all(class_='secaoFormBody')
    ba = ba[len(ba)-2] # há um outro dentro -1 -> -2

    ## resultado disponível
    res = ba.find_all('div', id='divResultadosSuperior')        
    return(len(res))

if __name__ == "__main__":
    path = '/home/renato/git/dje/' # compatibilidade cron
    logfile = path + 'dje.log'
    log = open(logfile,'a')
    log.write(logtime()+' - Programa iniciado.\n')
    subprocess.run(path + 'notify.sh "Programa Iniciado"', shell = True)
    [url,dtfim] = busca_inicial() # inicializa
    while dtfim == hoje():
        log.write(logtime()+' - Data não virou ainda. Nova busca em 5 minutos\n')
        time.sleep(300)
        [url,dtfim] = busca_inicial()
    log.write(logtime()+' - Data virou.\n')
    subprocess.run(path + 'notify.sh "Data Virou"', shell = True)
    res = nova_busca(url,dtfim)
    while res == 0:
        if time.strftime("%H") == '21': # data virou
            pausa = 60
        else:  # apos 22:00
            pausa = 30
        log.write(logtime()+' - Resultado indisponível, nova busca em '+pausa+' segundos.\n')
        time.sleep(pausa)
        res = novabusca(url,dtfim)
        if time.strftime("%H") == 00:
            res = -1
    if res == 1:
        log.write(logtime()+' - Resultado disponível.\n')
        log.write('#####################################\n')
        log.close()
        subprocess.run(path + 'notify.sh "DJE disponível"', shell = True)
        #subprocess.run("DISPLAY=:0 notify-send 'DJE' 'Dje disponível' -i starred", shell = True)
    else:
        log.write(logtime()+' - ERRO - Tempo limite atingido.\n')
        log.write('#####################################\n')
        log.close()


    
        
