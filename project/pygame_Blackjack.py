import copy
import random
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
hand_active = False
outcome = 0
add_score = False
result = ['', 'PLAYER BUSTED', 'PLAYER WINS', 'DEALER WINS', 'TIE GAME']

#deal card by selecting random card from deck and removing it from deck
def deal_cards(current_hand, current_deck):
    card = random.randint(0, len(current_deck))
    current_hand.append(current_deck[card-1])
    current_deck.pop(card-1)
    return current_hand, current_deck

#draw scores for player and dealer on screen
def draw_scores(player, dealer):
    screen.blit(font.render(f'Player Score: {player}', True, 'white'), (350, 400))
    if reveal_dealer:
        screen.blit(font.render(f'Dealer Score: {dealer}', True, 'white'), (350, 100))

#draw cards on screen
def draw_cards(player, dealer, reveal):
    for i in range(len(player)):
        pygame.draw.rect(screen, 'white', [70 + (i*70), 460 + (5*i), 120, 220], 0, 5)
        screen.blit(font.render(player[i], True, 'black'), (75 + (i*70), 465 + (5*i)))
        screen.blit(font.render(player[i], True, 'black'), (75 + (i*70), 635 + (5*i)))
        pygame.draw.rect(screen, 'purple', [70 + (i*70), 460 + (5*i), 120, 220], 5, 5)

    #if player hasn't finished turn, dealer will hide one card
    for i in range(len(dealer)):
        pygame.draw.rect(screen, 'white', [70 + (i*70), 160 + (5*i), 120, 220], 0, 5)
        if i != 0 and not reveal:
            screen.blit(font.render(dealer[i], True, 'black'), (75 + (i*70), 165 + (5*i)))
            screen.blit(font.render(dealer[i], True, 'black'), (75 + (i*70), 335 + (5*i)))
        else:
            screen.blit(font.render('???', True, 'black'), (75 + (i*70), 165 + (5*i)))
            screen.blit(font.render('???', True, 'black'), (75 + (i*70), 335 + (5*i)))
        pygame.draw.rect(screen, 'purple', [70 + (i*70), 160 + (5*i), 120, 220], 5, 5)

def calculate_score(hand):
    #calculate hand score fresh every time, check how many aces we have
    hand_score = 0
    ace_count = hand.count('A')
    for i in range(len(hand)):
        #for 2,3,4,5,6,7,8,9 - just add the number to total
        for j in range(8):
            if hand[i] == cards[j]:
                hand_score += int(hand[i])
        #for 10 and face cards, add 10
        if hand[i] in ['10', 'J', 'Q', 'K']:
            hand_score += 10
        #for aces start by adding 11, we'll check if we need to reduce afterwards
        elif hand[i] == 'A':
            hand_score += 11
    #determine how many aces need to be 1 instead of 11 to get under 21 if possible
    if hand_score > 21 and ace_count > 0:
        for i in range(ace_count):
            if hand_score > 21:
                hand_score -= 10
    return hand_score

#draw game screen, show buttons and score
def draw_game(active, records, outcome):
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
    # if there is an outcome for the hand that was played, display a restart button and tell user what happened
    if outcome != 0:
        outcome_text = font.render(result[outcome], True, 'white')
        screen.blit(outcome_text, (150, 300))
        restart = pygame.draw.rect(screen, 'white', [150, 400, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'purple', [150, 400, 300, 100], 3, 5)
        restart_text = font.render('PLAY AGAIN', True, 'black')
        screen.blit(restart_text, (155, 435))
        button_list.append(restart)
    return button_list

#check endgame conditions function
def check_endgame(hand_act, deal_score, play_score, result, totals, add):
    # check end game scenarios is player has stood, busted or blackjacked
    # result 1- player bust, 2-win, 3-loss, 4-push
    if not hand_act and deal_score >= 17:
        if play_score > 21:
            result = 1
        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2
        elif play_score < deal_score <= 21:
            result = 3
        else:
            result = 4
        if add:
            if result == 1 or result == 3:
                totals[1] += 1
            elif result == 2:
                totals[0] += 1
            else:
                totals[2] += 1
            add = False
    return result, totals, add

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
        initial_deal = False
    #once game is activated, and dealt, calculate scores and display cards
    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)
        draw_scores(player_score, dealer_score)
        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            if dealer_score < 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
    #initial screen with deal button
    button = draw_game(active, records, outcome)

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
                    hand_active = True
                    outcome = 0
                    add_score = True
            else:
                # if player can hit, allow them to draw a card
                if button[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                # allow player to end turn (stand)
                elif button[1].collidepoint(event.pos) and not reveal_dealer:
                    reveal_dealer = True
                    hand_active = False
                elif len(button) == 3:
                    if button[2].collidepoint(event.pos):
                        active = True
                        initial_deal = True
                        game_deck = copy.deepcopy(deck * one_deck)
                        my_hand = []
                        dealer_hand = []
                        outcome = 0
                        hand_active = True
                        reveal_dealer = False
                        outcome = 0
                        add_score = True
                        dealer_score = 0
                        player_score = 0

    # if player busts, automatically end turn - treat like a stand
    if hand_active and player_score >= 21:
        hand_active = False
        reveal_dealer = True

    outcome, records, add_score = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score)

    pygame.display.flip()
pygame.quit()