import copy
import random
from turtle import Screen
import pygame
pygame.init()
screen = pygame.display.set_mode((600, 900))
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
one_deck = 4 * cards
deck = 4
WIDTH = 600
HEIGHT = 900
pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Blackjack')
fps = 60
timer = pygame.time.Clock()
font = pygame.font.SysFont('freesansbold.ttf', 44)
active = False
#win, lose, tie
records = [0, 0, 0]
player_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False

#deal card by selecting random card from deck and removing it from deck
def deal_cards(current_hand, current_deck):
    card = random.randint(0, len(current_deck))
    current_hand.append(current_deck[card-1])
    current_deck.pop(card-1)
    print(current_hand, current_deck)
    return current_hand, current_deck

#draw cards on screen
def draw_cards(player, dealer, reveal):
    for i in range(len(player)):
        pygame.draw.rect(screen, 'white', [70 + (i*70), 460 + (5* i), 120, 220], 0, 5)
        screen.blit(font.render(player[i], True, 'black'), (75 + (i*70), 465 + (5* i)))
        screen.blit(font.render(player[i], True, 'black'), (75 + (i*70), 635 + (5* i)))
        pygame.draw.rect(screen, 'purple', [70 + (i*70), 460 + (5* i), 120, 220], 5, 5)

        
    #if player hasn 't finished turn,  dealer will hide one card
    for i in range(len(dealer)):
        pygame.draw.rect(screen, 'white', [70 + (i*70), 160 + (5* i), 120, 220], 0, 5)
        if  i != 0 and not reveal:
          screen.blit(font.render(dealer[i], True, 'black'), (75 + (i*70), 165 + (5* i)))
          screen.blit(font.render(dealer[i], True, 'black'), (75 + (i*70), 335 + (5* i)))
        else:
             screen.blit(font.render('???', True, 'black'), (75 + (i*70), 165 + (5* i)))
             screen.blit(font.render('???', True, 'black'), (75 + (i*70), 335 + (5* i)))
        pygame.draw.rect(screen, 'purple', [70 + (i*70), 160 + (5* i), 120, 220], 5, 5)
   
def draw_game(active, records):
    button_list = []
    if not active:
        deal = pygame.draw.rect(screen, 'white', [150, 20, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'purple', [150, 20, 300, 100], 3, 5)
        deal_text = font.render('DEAL', True, 'black')
        screen.blit(deal_text, (165, 50))
        button_list.append(deal)
    #once game starts, show hit and stand buttons
    else:
        hit = pygame.draw.rect(screen, 'white', [0, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'purple', [0, 700, 300, 100], 3, 5)
        hit_text = font.render('HIT', True, 'black')
        screen.blit(hit_text, (55, 735))
        button_list.append(hit)

        stand = pygame.draw.rect(screen, 'white', [300, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'purple', [300, 700, 300, 100], 3, 5)
        stand_text = font.render('STAND', True, 'black')
        screen.blit(stand_text, (355, 735))
        button_list.append(stand)
        score_text = font.render(f'Wins: {records[0]}, Losses: {records[1]}, Ties: {records[2]}', True, 'white')
        screen.blit(score_text, (15, 840))
    return button_list

#main game loop
run = True
while run:
    timer.tick(fps)
    screen.fill('green')
    #initial deal to player and dealer
    if initial_deal:
        for i in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        print(my_hand, dealer_hand)
        initial_deal = False
    #once game is activated, and dealt , calculate scores and display cards
    if active:
        draw_cards(my_hand, dealer_hand, reveal_dealer)
    button = draw_game(active, records)
    #initial screen with deal button
    button = draw_game(active, records)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not active:
                if button[0].collidepoint(event.pos):
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(one_deck * deck)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0

    pygame.display.flip()
pygame.quit()