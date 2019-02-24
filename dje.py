#!/usr/bin/env python3

"""Notificação para Busca Avançada do DJE e Imprensa Oficial"""


import subprocess
import time
import sys
import re
import platform
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
except ImportError:
    from PyQt4.QtGui import QApplication, QMessageBox


def hoje():
    return(time.strftime("%d/%m/%Y"))


def logtime():
    return(time.strftime("%d/%m/%Y-%H:%M:%S"))


def busca_inicial():
    """Checa se a data já virou e obtem um id para as buscas"""
    url = 'http://dje.tjsp.jus.br/cdje/consultaAvancada.do'
    try:
        page = urllib.request.urlopen(url)
    except urllib.error.URLError:
        print(logtime()+' - Erro ao carregar página')
        return([url, hoje()])  # vai forçar nova busca
    soup = BeautifulSoup(page, 'html.parser')
    # separa secao busca avançada
    ba = soup.find_all(class_='secaoFormBody')
    ba = ba[len(ba)-2]  # há um outro dentro, seleciona o penultimo
    # precisa de um id valido para novas buscas
    form_action = ba.find('form')['action']
    url = 'http://dje.tjsp.jus.br' + form_action
    # data busca
    dtfim = ba.find(id='dtFimString')['value']
    return([url, dtfim])


def nova_busca(url, dtfim):
    """Realiza uma nova busca avançada e checa se já está disponível"""
    values = {'dadosConsulta.dtFim': dtfim,
              'dadosConsulta.dtInicio': dtfim,
              'dadosConsulta.cdCaderno': '10',  # Administrativo apenas
              'dadosConsulta.pesquisaLivre': '201*'}
    try:
        data = urllib.parse.urlencode(values)
        data = data.encode('utf-8')  # data should be bytes
        req = urllib.request.Request(url, data)
        the_page = urllib.request.urlopen(req).read()
    except urllib.error.URLError:
        print(logtime()+' - Erro ao carregar página')
        return(0)  # vai forçar nova busca
    soup = BeautifulSoup(the_page, 'html.parser')
    # separa secao busca avançada
    ba = soup.find_all(class_='secaoFormBody')
    ba = ba[len(ba)-2]  # há um outro dentro, seleciona o penultimo
    # busca por elemento que aparece quando o resultado está disponível
    res = ba.find_all('div', id='divResultadosSuperior')
    return(len(res))


def notifica(path, msg):
    '''
    Envia notificação de novo status
    '''
    if platform.system() == 'Linux':
        subprocess.run(path + 'notify.sh "'+logtime()+'\n'+msg+'" ',
                       shell=True)
    elif platform.system() == 'Windows':
        pop = QMessageBox()
        pop.setIcon(QMessageBox.Information)
        pop.setText(msg)
        pop.setWindowTitle("DJE")
        pop.exec_()


def imprensa_init(dtfim):
    '''
    Inicializa uma instância do Selenium com dtfim
    '''
    url = ("https://www.imprensaoficial.com.br/DO/BuscaDO2001Documento_11_4."
           "aspx?link=%2F2014%2Fdje%2520-%2520caderno%25201%2520-%2520admini"
           "strativo%2Fsetembro%2F+11%2Fpag_0047.pdf&pagina=01&data=")
    url2 = "&caderno=DJE+-+Caderno+1+-+Administrativo"
    dtfim = dtfim.replace('/', '%2F')
    url += dtfim + url2
    options = Options()
    # DEBUG: comente a próxima linha para visualizar o navegador
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    return(driver)


def imprensa_numpags(driver):
    '''
    Checa se o número de páginas já está disponível
    '''
    try:
        driver.refresh()
        iframe_nav = driver.find_elements_by_tag_name('iframe')[1]
        driver.switch_to.frame(iframe_nav)
        ele_numpags = driver.find_element_by_id("lblTotalPagina")
        numpags = ele_numpags.get_attribute("innerHTML")
        driver.switch_to.default_content()
    except NoSuchElementException:
        numpags = -1
    return(numpags)


def imprensa_troca_pag(driver):
    '''
    Troca de página e checa se o pdf carregou
    '''
    try:
        driver.switch_to.default_content()
        iframe_nav = driver.find_elements_by_tag_name('iframe')[1]
        driver.switch_to.frame(iframe_nav)
        ele_pag = driver.find_element_by_id("lblPagina")
        pagina = ele_pag.get_attribute("innerHTML")
        # Troca de página: Impar -> + 1; Par -> - 1
        if int(pagina) % 2 == 0:
            driver.find_element_by_id("lnkAnterior").click()
        else:
            driver.find_element_by_id("lnkProxima").click()
        # Checa conteúdo no outro iframe
        driver.switch_to.default_content()
        iframe_pdf = driver.find_elements_by_tag_name('iframe')[0]
        driver.switch_to.frame(iframe_pdf)
        # Espera carregar alguma página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "#viewerContainer,"  # Pdf
                                            "#content_lblTitulo"))  # Erro
        )
        # checa se retornou pdf
        driver.find_element_by_id("viewerContainer")
    except (TimeoutException, NoSuchElementException):
        return(0)
    driver.switch_to.default_content()
    return(1)


if __name__ == "__main__":
    if platform.system() == 'Linux':
        path = re.search(r'((?:.*?/)+).*\.py', sys.argv[0]).group(1)
        # guarda o caminho para rodar o script de notificação por causa do cron
    else:
        path = ''
        app = QApplication([])  # Notificações windows
    print(logtime() + ' - Programa iniciado.')
    notifica(path, 'Programa Iniciado - Com Imprensa')
    [url, dtfim] = busca_inicial()  # inicializa
    while dtfim == hoje():
        print(logtime() + ' - Data não virou ainda. Nova busca em 5 minutos')
        time.sleep(300)
        [url, dtfim] = busca_inicial()
    print(logtime() + ' - Data virou.')
    notifica(path, 'Data Virou')
    sel = imprensa_init(dtfim)
    numpags = -1
    while True:  # enquanto não está disponível
        # nova busca avançada
        if nova_busca(url, dtfim) != 0:
            print(logtime() + ' - Resultado disponível na busca avançada.\n'
                  '#####################################')
            notifica(path, 'DJE disponível na busca avançada')
            break
        # atualiza imprensa oficial
        if numpags == -1:
            numpags = imprensa_numpags(sel)
            if numpags != -1:
                print(logtime() + ' - Número de páginas disponível: '
                      + str(numpags))
                notifica(path, 'Número de páginas disponível: ' + str(numpags))
                continue  # ignora pausa
        else:  # numpags já está disponível, troca de página
            if imprensa_troca_pag(sel) != 0:
                print(logtime() + ' - Resultado disponível na imprensa'
                      ' oficial.\n'
                      '#####################################')
                notifica(path, 'DJE disponível na imprensa oficial')
                break
        pausa = 60  # espera 1 minuto entre cada busca
        print(logtime() + ' - Resultado indisponível, nova busca em '
              + str(pausa) + ' segundos.')
        time.sleep(pausa)
        if time.strftime("%H") == '02':  # para de rodar após às 02:00
            print(logtime() + ' - ERRO - Tempo limite atingido.'
                  '\n#####################################')
            notifica(path, 'Tempo limite atingido.')
            break
    sel.quit()
