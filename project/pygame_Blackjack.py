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
VILT_DONKER  = (10,  60,  25)
VILT_MIDDEN  = (15,  80,  35)
VILT_RAND    = (8,   45,  18)
GOUD         = (212, 175, 55)
GOUD_DONKER  = (160, 125, 30)
WIT          = (255, 255, 255)
ZWART        = (0,   0,   0)
ROOD         = (190, 20,  20)
GRIJS        = (200, 200, 200)
GRIJS_LICHT  = (230, 230, 230)
BLAUW_DARK   = (20,  40,  120)
GEEL         = (255, 220, 50)
CREME        = (245, 235, 200)
 
CHIP_KLEUREN = {
    1:   (180, 180, 180),
    5:   (220, 50,  50),
    10:  (50,  80,  220),
    25:  (50,  180, 80),
    50:  (210, 140, 20),
    100: (140, 30,  160),
}
 
# --- LETTERTYPEN ---
def laad_font(grootte):
    for naam in ['segoeuisymbol', 'dejavusans', 'notosans', 'freesans', 'arial']:
        try:
            f = pygame.font.SysFont(naam, grootte)
            if f.size('♠')[0] > 4:
                return f
        except Exception:
            continue
    return pygame.font.Font(None, grootte)
 
font        = laad_font(32)
font_klein  = laad_font(20)
font_groot  = laad_font(46)
font_chip   = laad_font(16)
 
# --- KAARTEN ---
waarden       = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
symbolen      = ['♠','♥','♦','♣']
rood_symbolen = ['♥','♦']
een_deck      = [(w, s) for s in symbolen for w in waarden]
 
# --- SPELSTATUS ---
STARTBALANS  = 1000
balans       = STARTBALANS
inzet        = 0
fase         = 'inzet'
 
scores       = [0, 0, 0]
speler_hand  = []
dealer_hand  = []
uitkomst     = 0
dealer_zichtbaar = False
hand_actief  = False
score_tellen = False
speler_score = 0
dealer_score = 0
spel_deck    = []
uitbetaald   = False
 
uitkomst_tekst = ['', 'SPELER BUST!', 'SPELER WINT!', 'DEALER WINT!', 'GELIJKSPEL', 'BLACKJACK!']
chip_waarden   = [1, 5, 10, 25, 50, 100]
 
# --- TAFEL ---
tafel_surf = None
 
def maak_tafel():
    surf = pygame.Surface((WIDTH, HEIGHT))
 
    # Houten buitenrand
    surf.fill((40, 22, 8))
    pygame.draw.rect(surf, (70, 38, 12),  [0, 0, WIDTH, HEIGHT], 0, 0)
    pygame.draw.rect(surf, (55, 28, 8),   [18, 18, WIDTH-36, HEIGHT-36], 0, 30)
 
    # Vilt speeloppervlak
    vilt_rect = pygame.Rect(28, 28, WIDTH-56, HEIGHT-56)
    pygame.draw.rect(surf, VILT_MIDDEN, vilt_rect, 0, 28)
 
    # Subtiele vilt textuur
    for y in range(28, HEIGHT-28, 6):
        if (y // 6) % 2 == 0:
            pygame.draw.line(surf, VILT_DONKER, (28, y), (WIDTH-28, y), 1)
 
    # Gouden binnenkader
    pygame.draw.rect(surf, GOUD,        [38, 38, WIDTH-76, HEIGHT-76], 2, 22)
    pygame.draw.rect(surf, GOUD_DONKER, [42, 42, WIDTH-84, HEIGHT-84], 1, 20)
 
    # Dealer ellips bovenaan
    dealer_zone = [50, 50, WIDTH-100, 260]
    pygame.draw.ellipse(surf, VILT_RAND,   [dealer_zone[0]-2, dealer_zone[1]-2,
                                            dealer_zone[2]+4, dealer_zone[3]], 0)
    pygame.draw.ellipse(surf, VILT_MIDDEN, dealer_zone, 0)
    pygame.draw.ellipse(surf, GOUD,        dealer_zone, 2)
 
    lbl = laad_font(18).render('D E A L E R', True, GOUD)
    surf.blit(lbl, lbl.get_rect(center=(WIDTH//2, 72)))
 
    # Inzetcirkel (speler)
    cx, cy, r = WIDTH//2, 670, 55
    pygame.draw.circle(surf, VILT_RAND,   (cx, cy), r+3)
    pygame.draw.circle(surf, VILT_DONKER, (cx, cy), r)
    pygame.draw.circle(surf, GOUD,        (cx, cy), r,   2)
    pygame.draw.circle(surf, GOUD_DONKER, (cx, cy), r-8, 1)
    surf.blit(laad_font(14).render('INZET', True, GOUD),
              laad_font(14).render('INZET', True, GOUD).get_rect(center=(cx, cy)))
 
    # Scorebord balk onderaan (vaste plek op de tafel)
    balk_rect = pygame.Rect(38, HEIGHT-80, WIDTH-76, 38)
    pygame.draw.rect(surf, VILT_DONKER, balk_rect, 0, 8)
    pygame.draw.rect(surf, GOUD_DONKER, balk_rect, 1, 8)
 
    # Casino naam BOVEN de scorebalk
    cnl = laad_font(20).render('✦  ROYAL BLACKJACK  ✦', True, GOUD)
    surf.blit(cnl, cnl.get_rect(center=(WIDTH//2, HEIGHT-95)))
 
    return surf
 
 
def teken_achtergrond():
    global tafel_surf
    if tafel_surf is None:
        tafel_surf = maak_tafel()
    screen.blit(tafel_surf, (0, 0))
 
 
def teken_scorebord():
    """Teken de scoretekst in de vaste balk onderaan."""
    stekst = f'Wins: {scores[0]}     Verlies: {scores[1]}     Gelijk: {scores[2]}'
    ssurf  = font_klein.render(stekst, True, CREME)
    screen.blit(ssurf, ssurf.get_rect(center=(WIDTH//2, HEIGHT-61)))
 
 
# --- KAART ---
def teken_kaart(x, y, waarde, symbool, verborgen=False):
    breedte, hoogte = 90, 130
    if verborgen:
        pygame.draw.rect(screen, ZWART,      [x+4, y+4, breedte, hoogte], 0, 10)
        pygame.draw.rect(screen, BLAUW_DARK, [x, y, breedte, hoogte], 0, 10)
        for dx in range(10, breedte, 15):
            pygame.draw.line(screen, (30, 55, 130), (x+dx, y), (x+dx, y+hoogte), 1)
        for dy in range(10, hoogte, 15):
            pygame.draw.line(screen, (30, 55, 130), (x, y+dy), (x+breedte, y+dy), 1)
        pygame.draw.rect(screen, (40, 70, 160), [x, y, breedte, hoogte], 2, 10)
    else:
        kleur = ROOD if symbool in rood_symbolen else ZWART
        pygame.draw.rect(screen, ZWART,       [x+4, y+4, breedte, hoogte], 0, 10)
        pygame.draw.rect(screen, WIT,         [x, y, breedte, hoogte], 0, 10)
        pygame.draw.rect(screen, GRIJS_LICHT, [x, y, breedte, hoogte], 2, 10)
        screen.blit(font_klein.render(waarde,  True, kleur), (x+6, y+5))
        screen.blit(font_klein.render(symbool, True, kleur), (x+6, y+22))
        ws = font_klein.render(waarde,  True, kleur)
        ss = font_klein.render(symbool, True, kleur)
        screen.blit(pygame.transform.rotate(ws, 180), (x+breedte-ws.get_width()-6, y+hoogte-20))
        screen.blit(pygame.transform.rotate(ss, 180), (x+breedte-ss.get_width()-6, y+hoogte-37))
        groot = font_groot.render(symbool, True, kleur)
        screen.blit(groot, (x+breedte//2-groot.get_width()//2,
                            y+hoogte//2-groot.get_height()//2))
 
 
def teken_knop(rect, tekst, kleur, muis, tekst_kleur=WIT):
    hover = tuple(min(c+30, 255) for c in kleur)
    col   = hover if rect.collidepoint(muis) else kleur
    pygame.draw.rect(screen, ZWART, [rect.x+3, rect.y+3, rect.width, rect.height], 0, 10)
    pygame.draw.rect(screen, col,   rect, 0, 10)
    pygame.draw.rect(screen, GOUD,  rect, 2, 10)
    txt = font.render(tekst, True, tekst_kleur)
    screen.blit(txt, txt.get_rect(center=rect.center))
 
 
def teken_chip(cx, cy, waarde, muis):
    r     = 32
    kleur = CHIP_KLEUREN.get(waarde, GRIJS)
    hover = tuple(min(c+40, 255) for c in kleur)
    pos   = pygame.mouse.get_pos()
    col   = hover if ((pos[0]-cx)**2 + (pos[1]-cy)**2)**0.5 < r else kleur
    pygame.draw.circle(screen, ZWART, (cx+3, cy+3), r)
    pygame.draw.circle(screen, col,   (cx, cy), r)
    pygame.draw.circle(screen, WIT,   (cx, cy), r,   3)
    pygame.draw.circle(screen, col,   (cx, cy), r-6)
    pygame.draw.circle(screen, WIT,   (cx, cy), r-6, 2)
    lbl = font_chip.render(f'€{waarde}', True, WIT)
    screen.blit(lbl, lbl.get_rect(center=(cx, cy)))
    return pygame.Rect(cx-r, cy-r, r*2, r*2)
 
 
# --- SPELLOGICA ---
def trek_kaart(hand, deck):
    index = random.randint(0, len(deck)-1)
    hand.append(deck[index])
    deck.pop(index)
    return hand, deck
 
 
def bereken_score(hand):
    score = 0
    azen  = sum(1 for w, s in hand if w == 'A')
    for waarde, _ in hand:
        if waarde in ['J','Q','K','10']:
            score += 10
        elif waarde == 'A':
            score += 11
        else:
            score += int(waarde)
    while score > 21 and azen > 0:
        score -= 10
        azen  -= 1
    return score
 
 
def is_blackjack(hand):
    if len(hand) != 2:
        return False
    wlist = [w for w, s in hand]
    return 'A' in wlist and any(w in ['10','J','Q','K'] for w in wlist)
 
 
def controleer_einde(hand_actief, dealer_score, speler_score,
                     uitkomst, scores, score_tellen,
                     speler_hand, dealer_hand):
    if not hand_actief and dealer_score >= 17:
        speler_bj = is_blackjack(speler_hand)
        dealer_bj = is_blackjack(dealer_hand)
        if speler_bj and not dealer_bj:
            uitkomst = 5
        elif speler_score > 21:
            uitkomst = 1
        elif dealer_score > 21 or speler_score > dealer_score:
            uitkomst = 2
        elif speler_score < dealer_score:
            uitkomst = 3
        else:
            uitkomst = 4
        if score_tellen:
            if uitkomst in [1, 3]:
                scores[1] += 1
            elif uitkomst in [2, 5]:
                scores[0] += 1
            else:
                scores[2] += 1
            score_tellen = False
    return uitkomst, scores, score_tellen
 
 
def verwerk_uitbetaling(uitkomst, inzet, balans):
    if uitkomst == 5:
        balans += int(inzet * 1.5)
    elif uitkomst == 2:
        balans += inzet
    elif uitkomst in [1, 3]:
        balans -= inzet
    return balans
 
 
def nieuw_spel():
    return {
        'spel_deck'       : copy.deepcopy(een_deck * 4),
        'speler_hand'     : [],
        'dealer_hand'     : [],
        'uitkomst'        : 0,
        'hand_actief'     : True,
        'dealer_zichtbaar': False,
        'score_tellen'    : True,
        'speler_score'    : 0,
        'dealer_score'    : 0,
    }
 
 
# --- HOOFDLUS ---
run = True
 
while run:
    timer.tick(fps)
    teken_achtergrond()
    muis       = pygame.mouse.get_pos()
    knoppen    = []
    chip_rects = []
 
    # ====================================================
    # INZETFASE
    # ====================================================
    if fase == 'inzet':
        titel = font_groot.render('BLACKJACK', True, GOUD)
        screen.blit(titel, titel.get_rect(center=(WIDTH//2, 145)))
 
        # Balans & inzet info
        info_rect = pygame.Rect(WIDTH//2-140, 195, 280, 75)
        pygame.draw.rect(screen, VILT_DONKER, info_rect, 0, 12)
        pygame.draw.rect(screen, GOUD,        info_rect, 2, 12)
        screen.blit(font_klein.render(f'Balans: €{balans}', True, CREME),
                    (info_rect.x+16, info_rect.y+10))
        screen.blit(font_klein.render(f'Inzet:  €{inzet}',  True, GEEL),
                    (info_rect.x+16, info_rect.y+38))
 
        # Chips
        totaal_breedte = len(chip_waarden) * 75
        start_x = WIDTH//2 - totaal_breedte//2 + 37
        for i, w in enumerate(chip_waarden):
            cx = start_x + i*75
            cy = 390
            r  = teken_chip(cx, cy, w, muis)
            chip_rects.append((r, w))
 
        wis_knop   = pygame.Rect(30,  465, 160, 52)
        allin_knop = pygame.Rect(410, 465, 160, 52)
        deal_knop  = pygame.Rect(160, 535, 280, 65)
 
        teken_knop(wis_knop,   'WIS',    (120, 60, 10),  muis)
        teken_knop(allin_knop, 'ALL IN', (140, 20, 140), muis)
        deal_kleur = (160, 120, 10) if inzet > 0 else (60, 60, 60)
        teken_knop(deal_knop,  'DEAL',   deal_kleur,     muis)
 
        knoppen = [('wis', wis_knop), ('allin', allin_knop), ('deal', deal_knop)]
 
        teken_scorebord()
 
    # ====================================================
    # SPEL- EN EINDEFASE
    # ====================================================
    elif fase in ('spel', 'einde'):
 
        if len(speler_hand) == 0:
            for _ in range(2):
                speler_hand, spel_deck = trek_kaart(speler_hand, spel_deck)
                dealer_hand, spel_deck = trek_kaart(dealer_hand, spel_deck)
 
        speler_score = bereken_score(speler_hand)
        dealer_score = bereken_score(dealer_hand)
 
        # Kaarten dealer
        for i, (w, s) in enumerate(dealer_hand):
            teken_kaart(30 + i*100, 110, w, s,
                        verborgen=(i == 0 and not dealer_zichtbaar))
 
        if dealer_zichtbaar:
            ds = font_klein.render(f'Score: {dealer_score}', True, CREME)
            screen.blit(ds, ds.get_rect(center=(WIDTH//2, 258)))
 
        # Kaarten speler
        for i, (w, s) in enumerate(speler_hand):
            teken_kaart(30 + i*100, 490, w, s)
 
        screen.blit(font_klein.render(f'Score: {speler_score}', True, CREME), (30, 635))
        screen.blit(font_klein.render(f'Balans: €{balans}', True, CREME),     (30, 658))
        screen.blit(font_klein.render(f'Inzet:  €{inzet}',  True, GEEL),      (30, 680))
 
        if dealer_zichtbaar and dealer_score < 17:
            dealer_hand, spel_deck = trek_kaart(dealer_hand, spel_deck)
 
        if hand_actief and speler_score >= 21:
            hand_actief      = False
            dealer_zichtbaar = True
 
        uitkomst, scores, score_tellen = controleer_einde(
            hand_actief, dealer_score, speler_score,
            uitkomst, scores, score_tellen,
            speler_hand, dealer_hand
        )
 
        if uitkomst != 0 and not uitbetaald:
            balans     = verwerk_uitbetaling(uitkomst, inzet, balans)
            uitbetaald = True
            fase       = 'einde'
 
        if fase == 'spel':
            hit_knop   = pygame.Rect(30,  760, 240, 62)
            stand_knop = pygame.Rect(330, 760, 240, 62)
            teken_knop(hit_knop,   'HIT',   (30, 130, 60), muis)
            teken_knop(stand_knop, 'STAND', (160, 30, 30), muis)
            knoppen = [('hit', hit_knop), ('stand', stand_knop)]
 
        teken_scorebord()
 
        # --- UITKOMST OVERLAY ---
        if fase == 'einde':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
 
            if uitkomst in [2, 5]:
                tekst_kleur = (80, 220, 80)
            elif uitkomst in [1, 3]:
                tekst_kleur = (220, 80, 80)
            else:
                tekst_kleur = WIT
 
            tekst_surf = font_groot.render(uitkomst_tekst[uitkomst], True, tekst_kleur)
            screen.blit(tekst_surf, tekst_surf.get_rect(center=(WIDTH//2, 320)))
 
            if uitkomst == 5:
                bedrag_tekst = f'+€{int(inzet*1.5)}  (Blackjack 3:2!)'
                bkleur = (80, 220, 80)
            elif uitkomst == 2:
                bedrag_tekst = f'+€{inzet}'
                bkleur = (80, 220, 80)
            elif uitkomst in [1, 3]:
                bedrag_tekst = f'-€{inzet}'
                bkleur = (220, 80, 80)
            else:
                bedrag_tekst = 'Inzet terug'
                bkleur = WIT
 
            bsurf = font.render(bedrag_tekst, True, bkleur)
            screen.blit(bsurf, bsurf.get_rect(center=(WIDTH//2, 375)))
 
            balans_surf = font_klein.render(f'Nieuwe balans: €{balans}', True, WIT)
            screen.blit(balans_surf, balans_surf.get_rect(center=(WIDTH//2, 415)))
 
            # Failliet: alleen HERSTART tonen
            if balans <= 0:
                failliet_surf = font.render('Geen geld meer!', True, (220, 80, 80))
                screen.blit(failliet_surf, failliet_surf.get_rect(center=(WIDTH//2, 465)))
                herstart_knop = pygame.Rect(150, 500, 300, 65)
                teken_knop(herstart_knop, 'HERSTART (€1000)', (120, 20, 20), muis)
                knoppen.append(('herstart', herstart_knop))
            else:
                # Normaal: alleen OPNIEUW
                opnieuw_knop = pygame.Rect(150, 460, 300, 65)
                teken_knop(opnieuw_knop, 'OPNIEUW', (40, 70, 150), muis)
                knoppen.append(('opnieuw', opnieuw_knop))
 
    # ====================================================
    # EVENTS
    # ====================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
 
        if event.type == pygame.MOUSEBUTTONDOWN:
 
            if fase == 'inzet':
                for rect, w in chip_rects:
                    if rect.collidepoint(event.pos) and inzet + w <= balans:
                        inzet += w
                for naam, knop in knoppen:
                    if knop.collidepoint(event.pos):
                        if naam == 'wis':
                            inzet = 0
                        elif naam == 'allin':
                            inzet = balans
                        elif naam == 'deal' and inzet > 0:
                            staat            = nieuw_spel()
                            spel_deck        = staat['spel_deck']
                            speler_hand      = staat['speler_hand']
                            dealer_hand      = staat['dealer_hand']
                            uitkomst         = staat['uitkomst']
                            hand_actief      = staat['hand_actief']
                            dealer_zichtbaar = staat['dealer_zichtbaar']
                            score_tellen     = staat['score_tellen']
                            speler_score     = staat['speler_score']
                            dealer_score     = staat['dealer_score']
                            uitbetaald       = False
                            fase             = 'spel'
 
            elif fase == 'spel':
                for naam, knop in knoppen:
                    if knop.collidepoint(event.pos):
                        if naam == 'hit' and hand_actief:
                            speler_hand, spel_deck = trek_kaart(speler_hand, spel_deck)
                        elif naam == 'stand' and hand_actief:
                            hand_actief      = False
                            dealer_zichtbaar = True
 
            elif fase == 'einde':
                for naam, knop in knoppen:
                    if knop.collidepoint(event.pos):
                        if naam == 'opnieuw':
                            inzet = 0
                            fase  = 'inzet'
                        elif naam == 'herstart':
                            balans = STARTBALANS
                            scores = [0, 0, 0]
                            inzet  = 0
                            fase   = 'inzet'
 
    pygame.display.flip()
 
pygame.quit()