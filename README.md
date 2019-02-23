# Notificação para Busca Avançada do DJE e Diário Oficial

Esse script foi escrito considerando uma instalação Debian+LXDE.
Outras distribuições não foram testadas e talvez necessitem de alguns ajustes.

## Requisitos e Instalação

* Python3
* Beautiful Soup (python3-bs4)
* Notify-send (libnotify)
* Selenium (python3-selenium)

Caso não tenha certeza se os pacotes estão instalados:  
`sudo apt-get update`  
`sudo apt-get install python3-bs4 libnotify python3-selenium`

Baixe os arquivos do github e coloque-os em uma pasta.  
[Github](https://github.com/rgamici/dje) ou [arquivo .zip](https://github.com/rgamici/dje/archive/master.zip)

Caso não tenho o python instalado, [essa página](https://github.com/rgamici/dje/releases) contém algumas versões compiladas.
Baixe o arquivo `.zip` ou `.exe` e execute diretamente.

## Executando o script

### Linux

No terminal execute o comando:  
`./dje.py`  
Algumas mensagens serão impressas na tela.
**Não** feche o terminal ou o programa será encerrado.

Caso não queira deixar o terminal aberto:  
`nohup ./dje.py &`  

### Windows

1. Baixe o Python 3: https://www.python.org/downloads/release/python-372/;

2. Na primeira janela de instalação, marque a caixa "Add Python 3.7 to PATH" e clique em "Install Now";

3. Após instalado, abra o Power Shell (aperte as teclas "WINDOWS + R", digite "powershell" na caixa de diálogo que abrir e aperte "Ok");

4. Para instalar o BeatifulSoup, digite:  
`python -m pip install bs4`

5. Após instalado o BeatifulSoup, instale o PyQt5:  
`python -m pip install pyqt5`

6. Acesse https://github.com/rgamici/dje, clique em "Clone or Download" e em "Download ZIP"

7. Descompacte o arquivo baixado e dê um duplo clique em `dje.py`

8. O programa ficará rodando em um console e mostrará uma caixa de diálogo quando virar a data do DJE ou ele estiver disponível!

### Usando cron para executar automaticamente todos os dias

Você pode configurar o sistema para rodar o script automaticamente.
Por exemplo, usando o cron para executá-lo às 21:00 de segunda à sexta, abra o arquivo de configuração do cron com:  
`crontab -e`  
Então insira o seguinte texto no fim do arquivo:  
`00 21 * * 1-5 /caminho/para/pasta/dje.py >> /caminho/para/pasta/dje.log`  
As mensagens que seriam impressas na tela são salvas no arquivo `dje.log`.
Se não quiser salvar nenhuma mensagem, substitua `/caminho/para/pasta/dje.log` por `/dev/null`.

Para testar se o programa está rodando como deveria e as notificações são criadas, use:  
`* * * * * /caminho/para/pasta/dje.py >> /caminho/para/pasta/dje.log`  
O script será executado a cada minuto.
Se nenhuma notificação for exibida, cheque o arquivo `.log` por eventuais erros.

## Notificação em outras distribuições

O script deve funcionar em qualquer distribuição, e usa um arquivo separado (`notify.sh`) para criar as notificações.
Caso a sua distribuição não suporte o comando `notify-send` para exibir notificações, altere o arquivo com o comando que cria notificações na sua distribuição.


Para sugestões e problemas, crie um novo tópico [aqui](https://github.com/rgamici/dje/issues).
