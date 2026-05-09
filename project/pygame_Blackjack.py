import copy
import random
import pygame
pygame.init()
 
# --- INSTELLINGEN ---
WIDTH = 600
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Blackjack')
fps = 60
timer = pygame.time.Clock()
 
# --- KLEUREN ---
GROEN       = (15, 80, 35)
GROEN_LIJN  = (22, 110, 50)
GOUD        = (212, 175, 55)
WIT         = (255, 255, 255)
ZWART       = (0, 0, 0)
ROOD        = (190, 20, 20)
GRIJS       = (200, 200, 200)
BLAUW_DARK  = (20, 40, 120)
 
# --- LETTERTYPEN ---
font       = pygame.font.SysFont('freesansbold.ttf', 36)
font_klein = pygame.font.SysFont('freesansbold.ttf', 22)
 
# --- KAARTEN ---
waarden = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
symbolen = ['♠', '♥', '♦', '♣']
rood_symbolen = ['♥', '♦']
een_deck = [(w, s) for s in symbolen for w in waarden]  # 52 kaarten als tuples
 
# --- SPELSTATUS ---
actief = False
scores = [0, 0, 0]  # [wins, verliezen, gelijkspelen]
speler_hand = []
dealer_hand = []
uitkomst = 0
dealer_zichtbaar = False
hand_actief = False
score_tellen = False
speler_score = 0
dealer_score = 0
uitkomst_tekst = ['', 'SPELER VERLIEST', 'SPELER WINT', 'DEALER WINT', 'GELIJKSPEL']
 
 
# --- FUNCTIES ---
 
def teken_achtergrond():
    screen.fill(GROEN)
    # rasterlijnen tekenen
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GROEN_LIJN, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GROEN_LIJN, (0, y), (WIDTH, y), 1)
    # gouden rand
    pygame.draw.rect(screen, GOUD, [10, 10, WIDTH - 20, HEIGHT - 20], 3, 12)
 
 
def teken_kaart(x, y, waarde, symbool, verborgen=False):
    breedte, hoogte = 90, 130
    if verborgen:
        # blauwe rugzijde
        pygame.draw.rect(screen, BLAUW_DARK, [x, y, breedte, hoogte], 0, 10)
        pygame.draw.rect(screen, (40, 70, 160), [x, y, breedte, hoogte], 2, 10)
    else:
        # witte voorzijde
        kleur = ROOD if symbool in rood_symbolen else ZWART
        pygame.draw.rect(screen, WIT, [x, y, breedte, hoogte], 0, 10)
        pygame.draw.rect(screen, GRIJS, [x, y, breedte, hoogte], 2, 10)
        # waarde linksboven
        screen.blit(font_klein.render(waarde, True, kleur), (x + 7, y + 6))
        # symbool linksboven
        screen.blit(font_klein.render(symbool, True, kleur), (x + 7, y + 24))
        # groot symbool in het midden
        groot = font.render(symbool, True, kleur)
        screen.blit(groot, (x + breedte // 2 - groot.get_width() // 2, y + hoogte // 2 - groot.get_height() // 2))
 
 
def teken_knop(rect, tekst, kleur, muis):
    # knop wordt lichter als je er over hovered
    hover_kleur = tuple(min(c + 30, 255) for c in kleur)
    col = hover_kleur if rect.collidepoint(muis) else kleur
    pygame.draw.rect(screen, col, rect, 0, 10)
    pygame.draw.rect(screen, GOUD, rect, 2, 10)
    txt = font.render(tekst, True, WIT)
    screen.blit(txt, txt.get_rect(center=rect.center))
 
 
def trek_kaart(hand, deck):
    # pak een willekeurige kaart uit het deck
    index = random.randint(0, len(deck) - 1)
    hand.append(deck[index])
    deck.pop(index)
    return hand, deck
 
 
def bereken_score(hand):
    score = 0
    azen = sum(1 for w, s in hand if w == 'A')
    for waarde, symbool in hand:
        if waarde in ['J', 'Q', 'K', '10']:
            score += 10
        elif waarde == 'A':
            score += 11
        else:
            score += int(waarde)
    # aas van 11 naar 1 als score te hoog is
    while score > 21 and azen > 0:
        score -= 10
        azen -= 1
    return score
 
 
def controleer_einde(hand_actief, dealer_score, speler_score, uitkomst, scores, score_tellen):
    if not hand_actief and dealer_score >= 17:
        if speler_score > 21:
            uitkomst = 1   # speler bust
        elif dealer_score > 21 or speler_score > dealer_score:
            uitkomst = 2   # speler wint
        elif speler_score < dealer_score:
            uitkomst = 3   # dealer wint
        else:
            uitkomst = 4   # gelijkspel
        if score_tellen:
            if uitkomst in [1, 3]:
                scores[1] += 1
            elif uitkomst == 2:
                scores[0] += 1
            else:
                scores[2] += 1
            score_tellen = False
    return uitkomst, scores, score_tellen
 
 
# --- HOOFDLUS ---
run = True
spel_deck = []
 
while run:
    timer.tick(fps)
    teken_achtergrond()
    muis = pygame.mouse.get_pos()
    knoppen = []
 
    # kaarten uitdelen aan het begin
    if actief and len(speler_hand) == 0:
        for _ in range(2):
            speler_hand, spel_deck = trek_kaart(speler_hand, spel_deck)
            dealer_hand, spel_deck = trek_kaart(dealer_hand, spel_deck)
 
    # spel tekenen als het actief is
    if actief:
        speler_score = bereken_score(speler_hand)
        dealer_score = bereken_score(dealer_hand)
 
        # labels
        screen.blit(font_klein.render('DEALER', True, GOUD), (20, 130))
        screen.blit(font_klein.render('SPELER', True, GOUD), (20, 450))
 
        # kaarten tekenen
        for i, (w, s) in enumerate(dealer_hand):
            teken_kaart(30 + i * 100, 155, w, s, verborgen=(i == 0 and not dealer_zichtbaar))
        for i, (w, s) in enumerate(speler_hand):
            teken_kaart(30 + i * 100, 480, w, s)
 
        # scores tekenen
        screen.blit(font_klein.render(f'Score: {speler_score}', True, WIT), (20, 630))
        if dealer_zichtbaar:
            screen.blit(font_klein.render(f'Score: {dealer_score}', True, WIT), (20, 107))
 
        # dealer trekt bij als score onder 17 is
        if dealer_zichtbaar and dealer_score < 17:
            dealer_hand, spel_deck = trek_kaart(dealer_hand, spel_deck)
 
        # HIT en STAND knoppen
        hit_knop = pygame.Rect(20, 780, 260, 70)
        stand_knop = pygame.Rect(320, 780, 260, 70)
        teken_knop(hit_knop, 'HIT', (30, 130, 60), muis)
        teken_knop(stand_knop, 'STAND', (160, 30, 30), muis)
        knoppen = [hit_knop, stand_knop]
 
        # scorebord onderaan
        screen.blit(font_klein.render(f'Wins: {scores[0]}   Verlies: {scores[1]}   Gelijk: {scores[2]}', True, WIT), (20, 865))
 
        # speler heeft 21 of meer: automatisch stoppen
        if hand_actief and speler_score >= 21:
            hand_actief = False
            dealer_zichtbaar = True
 
        uitkomst, scores, score_tellen = controleer_einde(hand_actief, dealer_score, speler_score, uitkomst, scores, score_tellen)
 
        # uitkomst tonen
        if uitkomst != 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            screen.blit(font.render(uitkomst_tekst[uitkomst], True, GOUD), (WIDTH // 2 - 180, 370))
            opnieuw_knop = pygame.Rect(150, 430, 300, 70)
            teken_knop(opnieuw_knop, 'OPNIEUW', (40, 70, 150), muis)
            knoppen.append(opnieuw_knop)
 
    else:
        # startscherm: alleen DEAL knop
        deal_knop = pygame.Rect(150, 400, 300, 70)
        teken_knop(deal_knop, 'DEAL', (160, 120, 10), muis)
        knoppen = [deal_knop]
 
    # events verwerken
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
 
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not actief:
                # DEAL knop
                if knoppen[0].collidepoint(event.pos):
                    actief = True
                    spel_deck = copy.deepcopy(een_deck * 4)
                    speler_hand = []
                    dealer_hand = []
                    uitkomst = 0
                    hand_actief = True
                    dealer_zichtbaar = False
                    score_tellen = True
                    speler_score = 0
                    dealer_score = 0
            else:
                if uitkomst == 0:
                    # HIT knop
                    if knoppen[0].collidepoint(event.pos) and hand_actief:
                        speler_hand, spel_deck = trek_kaart(speler_hand, spel_deck)
                    # STAND knop
                    elif knoppen[1].collidepoint(event.pos) and hand_actief:
                        hand_actief = False
                        dealer_zichtbaar = True
                else:
                    # OPNIEUW knop
                    if knoppen[2].collidepoint(event.pos):
                        actief = True
                        spel_deck = copy.deepcopy(een_deck * 4)
                        speler_hand = []
                        dealer_hand = []
                        uitkomst = 0
                        hand_actief = True
                        dealer_zichtbaar = False
                        score_tellen = True
                        speler_score = 0
                        dealer_score = 0
 
    pygame.display.flip()
 
pygame.quit()