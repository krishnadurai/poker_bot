import pygame
from pygame.locals import *
from socket import *
import sys
import thread
from Queue import *
import time
import threading

#Socket to receive data
DEALER_SERVER = '192.168.117.112'
#DEALER_SERVER = '192.168.2.2'
R_PORT = 11716
R_HOST = ''
sock_recv_data = socket(AF_INET, SOCK_STREAM)
sock_recv_data.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock_recv_data.bind((R_HOST, R_PORT))

#Socket to send data
S_HOST = DEALER_SERVER
S_PORT = 11717
sock_send_data = socket(AF_INET, SOCK_STREAM)

#Message Queue
msg_q = Queue()

#Thread to handle received data
def handle_data():
    data = ''
    while True:
        if not msg_q.empty():
            q_data = msg_q.get()
            for data in q_data.split('$'):
                req_type = data.partition(':')[0].partition('=')[2]
                if req_type == 'check':
                    print 'Connection established'
                elif req_type == 'reset':
                    poker_data.hand_cards = ['images/front', 'images/front']
                    for i in range(5):
                        poker_data.com_cards[i] = 'images/front'
                elif req_type == 'init':
                    print req_type
                    temp = data.partition(':')[2]
                    paramlist = temp.split(';')
                    for param in paramlist:
                        if param.partition('=')[0] == 'nop':
                            poker_data.NO_OF_PLAYERS = int(param.partition('=')[2])
                        elif param.partition('=')[0] == 'yourPos':
                            poker_data.mypos = int(param.partition('=')[2])
                        elif param.partition('=')[0] == 'sb':
                            poker_data.small_blind = int(param.partition('=')[2])
                        elif param.partition('=')[0] == 'players_money':
                            temp = param.partition('=')[2]
                            temp = temp.strip('[').strip(']').split(',')
                            for i in range(len(temp)):
                                poker_data.remaining_money[i] = int(temp[i])
                elif req_type == 'cards':
                    print req_type
                    card1 = data.partition(':')[2].partition(',')[0]
                    card2 = data.partition(':')[2].partition(',')[2]
                    poker_data.hand_cards[0] = 'images/' + card1
                    poker_data.hand_cards[1] = 'images/' + card2
                elif req_type == 'data':
                    print req_type
                    temp = data.partition(':')[2]
                    paramlist = temp.split(';')
                    for param in paramlist:
                        if param.partition('=')[0] == 'flop_cards':
                            temp = param.partition('=')[2]
                            temp = temp.strip('[').strip(']').split(',')
                            #print 'comm cards are ' + temp
                            for i in range(len(temp)):
                                poker_data.com_cards[i] = 'images/' + temp[i].split("'")[1]
                            #print 'after ' + poker_data.com_cards
                        elif param.partition('=')[0] == 'turn_cards':
                            temp = param.partition('=')[2]
                            poker_data.com_cards[3] = 'images/' + temp
                        elif param.partition('=')[0] == 'river_cards':
                            temp = param.partition('=')[2]
                            poker_data.com_cards[4] = 'images/' + temp
                        elif param.partition('=')[0] == 'live':
                            temp = param.partition('=')[2]
                            temp = temp.strip('[').strip(']').split(',')
                            for i in range(0, poker_data.NO_OF_PLAYERS):
                                poker_data.ingame[i] = int(temp[i])
                        elif param.partition('=')[0] == 'current_player':
                            poker_data.current_player = int(param.partition('=')[2])
                        elif param.partition('=')[0] == 'NO_OF_POTS':
                            poker_data.no_of_pots = int(param.partition('=')[2])
                        elif param.partition('=')[0] == 'last_raised_amt':
                            poker_data.last_raised_amt = int(param.partition('=')[2])
                        elif param.partition('=')[0] == 'players_money':
                            temp = param.partition('=')[2]
                            temp = temp.strip('[').strip(']').split(',')
                            for i in range(len(temp)):
                                poker_data.remaining_money[i] = int(temp[i])
                        elif param.partition('=')[0] == 'pot_investment':
                            temp = param.partition('=')[2]
                            temp = temp.strip('[').strip(']').split(',')
                            for i in range(len(temp)):
                                poker_data.money_in_pot[i] = int(temp[i])
                        elif param.partition('=')[0] == 'last_raised_by':
                            poker_data.last_raised_by = int(param.partition('=')[2])
                        elif param.partition('=')[0] == 'small_blind_amt':
                            poker_data.small_blind_amt = int(param.partition('=')[2])
                        elif param.partition('=')[0] == 'pot_money':
                            temp = param.partition('=')[2]
                            temp = temp.strip('[').strip(']').split(',')
                            for i in range(poker_data.no_of_pots):
                                poker_data.pot_money[i] = int(temp[i])
                        elif param.partition('=')[0] == 'showdown_list':
                            pass

                amt_min = max(poker_data.last_raised_amt + poker_data.last_raised_by, poker_data.small_blind_amt*2)
                amt_max = poker_data.remaining_money[poker_data.mypos]
                if amt_min > amt_max and amt_max > poker_data.last_raised_amt:
                    poker_data.bet_amount = amt_max + poker_data.money_in_pot[poker_data.mypos]
                else:
                    poker_data.bet_amount = amt_min

        else:
            time.sleep(1)

#Thread to send data
def send_data(data):
    try:
        print 'sending.......'
        data = str(data)
        sock_send_data.send(data)
        print 'data sent ->' + data
    except:
        print 'Something wrong happened while sending data'



# Thread to receive data
def recv_data():
    print 'waiting for conn in recv_data'
    sock_recv_data.listen(1)
    conn_recv_data,addr = sock_recv_data.accept()

    while True:
        try:
            data = conn_recv_data.recv(4096)
            if data != '':
                msg_q.put(data)
                print data
        except:
            print 'connect error'
            sys.exit()


# Start recv_data thread
try:
    thread.start_new_thread(recv_data, ())
except:
    print'unable to start recv_data thread'

# Start handle_data thread
try:
    thread.start_new_thread(handle_data, ())
except:
    print'unable to start handle_data thread'

try:
    sock_send_data.connect((S_HOST, S_PORT))
    sock_send_data.send('req')
except:
    print 'connect error'


class Message:
    mypos = 0
    small_blind = 5
    small_blind_amt = 0
    no_of_pots = 0
    pot_money = [0] * 7
    NO_OF_PLAYERS = 0
    ingame = [0, 0, 0, 0, 0, 0, 0, 0]
    money_in_pot = [0, 0, 0, 0, 0, 0, 0, 0]
    remaining_money = [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
    last_raised_amt = 0
    last_raised_by = 0
    current_player = 0
    bet_amount = 0
    player_cards1 = ["images/front", "images/front", "images/front",
                     "images/front", "images/front", "images/front",
                     "images/front"]
    player_cards2 = ["images/front", "images/front", "images/front",
                     "images/front", "images/front", "images/front",
                     "images/front"]
    hand_cards = ["images/front", "images/front"]
    com_cards = ["images/front", "images/front", "images/front",
                 "images/front", "images/front"]

    def __init__(self):
        print 'object created'


#Creating message object
poker_data = Message()
pos = [[320, 300], [170, 300], [60, 165], [170, 25], [360, 25],
       [550, 25], [655, 165], [550, 300]]
pot_pos = [[396, 290], [206, 290], [170, 213], [206, 131], [396, 131],
           [586, 131], [630, 213], [586, 290]]
money_pos = [[396, 406], [206, 406], [30, 213], [206, 15], [396, 15],
             [586, 15], [765, 213], [586, 406]]
#SCREEN_X = 795
SCREEN_X = 950
SCREEN_Y = 511
bg = "images/back.png"



screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y), 0, 32)
screen.fill((28, 28, 30))
pygame.display.set_caption("Poker Project")
icon = pygame.image.load("images/icon.png").convert()
current_player_image = pygame.image.load("images/current_player").convert()
small_blind_image = pygame.image.load("images/sb.png").convert()
pygame.display.set_icon(icon)
back = pygame.image.load(bg).convert()
screen = pygame.display.get_surface()
clock = pygame.time.Clock()


while True:
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    hc_images = [pygame.image.load(poker_data.hand_cards[0]).convert(),
                 pygame.image.load(poker_data.hand_cards[1]).convert()]
    cc_image = []
    for i in range(0, 5):
        cc_image.append(pygame.image.load(poker_data.com_cards[i])
                        .convert())
    card1_image = []
    card2_image = []
    for i in range(0, 7):
        card1_image.append(pygame.image.load(poker_data.player_cards1[i])
                           .convert())
        card2_image.append(pygame.image.load(poker_data.player_cards2[i])
                           .convert())
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    # Test
    if poker_data.current_player == poker_data.mypos and poker_data.hand_cards[0] != 'images/front':
        thread.start_new_thread(send_data, ('req=call:amt='+str(min(poker_data.last_raised_amt, (poker_data.remaining_money[poker_data.mypos] + poker_data.money_in_pot[poker_data.mypos]))),))
        poker_data.current_player = -1

    screen.blit(back, (0, 0))
    screen.blit(hc_images[0], (pos[0][0], pos[0][1]))
    screen.blit(hc_images[1], (pos[0][0] + 72, pos[0][1]))
    for i in range(0, 5):
        screen.blit(cc_image[i], (i * 72 + 225, 50 + 96 + 20))
    j = (poker_data.mypos + 1) % 8
    for i in range(1, 8):
        if(poker_data.ingame[j]):
            screen.blit(card1_image[i - 1], (pos[i][0], pos[i][1]))
            screen.blit(card2_image[i - 1], (pos[i][0] + 15, pos[i][1]))
        j += 1
        j %= 8
    j = 0 #(poker_data.mypos) % 8
    for k in range(0, 8):
        if(poker_data.ingame[j]):
            i = k
            rem_money_text = font.render("$" + str
                                         (poker_data.remaining_money[i]),
                                         1, (0, 255, 0))
            bet_money_text = font.render("$" + str(poker_data.money_in_pot[i]),
                                         1, (255, 0, 0))
            i = (k-poker_data.mypos+8)%8
            rem_money_textpos = rem_money_text.get_rect()
            bet_money_textpos = bet_money_text.get_rect()
            rem_money_textpos.centerx = money_pos[i][0]
            bet_money_textpos.centerx = pot_pos[i][0]
            rem_money_textpos.centery = money_pos[i][1]
            bet_money_textpos.centery = pot_pos[i][1]
            screen.blit(rem_money_text, rem_money_textpos)
            screen.blit(bet_money_text, bet_money_textpos)
        j += 1
        j %= 8

    sb = 8 + poker_data.small_blind - poker_data.mypos
    sb %= 8
    screen.blit(small_blind_image, (pos[sb][0]- 30, pos[sb][1]))
    cp = 8 + poker_data.current_player - poker_data.mypos
    cp %= 8
    screen.blit(current_player_image, (pos[cp][0]-16, pos[cp][1] + 20))

    for i in range(poker_data.no_of_pots):
        pot_text = font.render('Pot ' + str(i + 1) + ' $ '+str(poker_data.pot_money[i]), 1, (255, 255, 255))
        screen.blit(pot_text, (800, (i * 40) + 20))
    pygame.display.update()
