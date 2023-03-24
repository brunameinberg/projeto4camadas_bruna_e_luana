#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
from time import *
import numpy as np

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)


def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()

        print("esperando 1 byte de sacrifício")
        
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        sleep(.1)
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
            

        #definindo eop
        eop = "AA BB CC DD"


        #ocioso
        ocioso = False
        rx_write = bytearray.fromhex("")
        alerta = False
        aq2 = False
        aq3 = False
        aq4 = False


        #mensagem tipo 5
        tipo = 5
        string = "00 00 00 00 00 00 00 00 00"
        tp5 = tipo.to_bytes(1,byteorder='big')+bytearray.fromhex(string)+bytearray.fromhex(eop)

        #tipo1
        rxBuffer, nRx = com1.getData(10)
        f = open("arquivodetransmissao_tp90.txt","a")
        f.write(f"{ctime(time())}/receb/1/14 \n")
        numero_t_pacotes = rxBuffer[3]
        print(f'O NÚMERO DE PACOTES É: {numero_t_pacotes}')
        print(rxBuffer)
        tipo = 2
        tp2 = tipo.to_bytes(1,byteorder='big')+bytearray.fromhex(string)+bytearray.fromhex(eop)
        print(f"RESPOSTA DO TIPO 2 É {tp2} \n")
        com1.sendData(tp2)
        teste, nRx = com1.getData(4)
        f.write(f"{ctime(time())}/envio/2/14 \n")
        if teste == bytearray.fromhex(eop):
            com1.rx.clearBuffer()
            print("FIZ CLEAR BUFFER")
        print("FIZ HANDSHAKE")

        #numero atual de pacotes
        num_atual_pac = 0
        num_atual_pac_erro = 0

        #íncio do recebimento de pacotes
        timer1 = time()
        i =0
        while i < numero_t_pacotes:
            timer2 = time()
            while com1.rx.getIsEmpty()==True:
                if (time()-timer2) > 20:
                    alerta = True
                    break
                else:
                    if (time()-timer1)>2:
                        print(time()-timer1)
                        tipo = 4
                        string = "00 00 00 00 00 00"
                        string2 = "00 00"
                        num_atual_pac
                        
                        tp4 = tipo.to_bytes(1,byteorder='big')+bytearray.fromhex(string)+num_atual_pac.to_bytes(1,byteorder='big')+bytearray.fromhex(string2)+bytearray.fromhex(eop)                
                        com1.sendData(tp4)
                        timer1 = time()
                        print("-------------------------")
                        print("NÃO RECEBEU PACOTE SOS")
                        print("-------------------------")
            if alerta == True:
                break
            head, nRx = com1.getData(10)
            if head[0] == 3:
                if head[4] == num_atual_pac+1:
                    tamanho = head[5]
                    print(f"O TAMANHO DO PAYLOAD É {tamanho}")
                    payload, nRx = com1.getData(tamanho)
                    eop2, nRx = com1.getData(4)
                    if eop2 == bytearray.fromhex(eop):
                        rx_write+=payload
                        num_atual_pac = head[4]
                        timer1 = time()
                        tipo = 4
                        string = "00 00 00 00 00 00"
                        string2 = "00 00"
                        tp4 = tipo.to_bytes(1,byteorder='big')+bytearray.fromhex(string)+num_atual_pac.to_bytes(1,byteorder='big')+bytearray.fromhex(string2)+bytearray.fromhex(eop)   
                        com1.sendData(tp4)
                        print(num_atual_pac)
                        f.write(f"{ctime(time())}/receb/3/{tamanho+10+4}/{num_atual_pac} \n")
                        f.write(f"{ctime(time())}/envio/4/14 \n")
                        i+=1
                    else:
                        ocioso = True

                else:
                    ocioso = True
                

            if ocioso == True:
                tipo = 6
                string = "00 00 00 00 00"
                string2 = "00 00 00"
                num_atual_pac_erro=num_atual_pac+1
                tp6 = tipo.to_bytes(1,byteorder='big')+bytearray.fromhex(string)+num_atual_pac_erro.to_bytes(1,byteorder='big')+bytearray.fromhex(string2)+bytearray.fromhex(eop)                    
                com1.sendData(tp6)
                com1.rx.clearBuffer()
                f.write(f"{ctime(time())}/envio/6/14 \n")
                ocioso = False
                print("---------------------------------")
                print("PACOTE COM ERRO: ESPERANDO RENVIO")
                print("---------------------------------")                

        if alerta == True:
            com1.sendData(tp5)
            f.write(f"{ctime(time())}/envio/5/14 \n")
            print("--------------------------------")
            print("TIME OUT: ENCERRANDO COMUNICAÇÃO")
            print("--------------------------------")
            com1.disable()
           
        
        imageW = "./img/recebida.jpg"
        g = open(imageW,'wb')
        g.write(rx_write)
        g.close()
        f.close()    

                    

        

        

            
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
