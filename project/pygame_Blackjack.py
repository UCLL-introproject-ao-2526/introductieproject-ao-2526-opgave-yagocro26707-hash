import copy
import random
import pygame
pygame.init()

# --- INSTELLINGEN ---
WIDTH  = 600
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Blackjack')
fps   = 60
timer = pygame.time.Clock()

# --- KLEUREN ---
VILT_DONKER = (10,  60,  25)
VILT_MIDDEN = (15,  80,  35)
VILT_RAND   = (8,   45,  18)
GOUD        = (212, 175, 55)
GOUD_DONKER = (160, 125, 30)
WIT         = (255, 255, 255)
ZWART       = (0,   0,   0)
ROOD        = (190, 20,  20)
GRIJS       = (200, 200, 200)
GRIJS_LICHT = (230, 230, 230)
BLAUW_DARK  = (20,  40,  120)
GEEL        = (255, 220, 50)
CREME       = (245, 235, 200)

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

font       = laad_font(32)
font_klein = laad_font(20)
font_groot = laad_font(46)
font_chip  = laad_font(16)

# --- KAARTEN ---
waarden       = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
symbolen      = ['♠', '♥', '♦', '♣']
rood_symbolen = ['♥', '♦']
een_deck      = [(w, s) for s in symbolen for w in waarden]

# --- SPELSTATUS ---
STARTBALANS = 1000
balans      = STARTBALANS
inzet       = 0
fase        = 'inzet'

scores           = [0, 0, 0]
speler_hand      = []
dealer_hand      = []
uitkomst         = 0
dealer_zichtbaar = False
hand_actief      = False
score_tellen     = False
speler_score     = 0
dealer_score     = 0
spel_deck        = []
uitbetaald       = False

uitkomst_tekst = ['', 'SPELER BUST!', 'SPELER WINT!', 'DEALER WINT!', 'GELIJKSPEL', 'BLACKJACK!']
chip_waarden   = [1, 5, 10, 25, 50, 100]


# --- TAFEL ---
tafel_surf = None

def maak_tafel():
    surf = pygame.Surface((WIDTH, HEIGHT))

    # houten buitenrand
    surf.fill((40, 22, 8))
    pygame.draw.rect(surf, (70, 38, 12), [0,  0,  WIDTH,    HEIGHT   ], 0, 0)
    pygame.draw.rect(surf, (55, 28,  8), [18, 18, WIDTH-36, HEIGHT-36], 0, 30)

    # vilt speeloppervlak
    pygame.draw.rect(surf, VILT_MIDDEN, [28, 28, WIDTH-56, HEIGHT-56], 0, 28)

    # subtiele vilt textuur
    for y in range(28, HEIGHT-28, 6):
        if (y // 6) % 2 == 0:
            pygame.draw.line(surf, VILT_DONKER, (28, y), (WIDTH-28, y), 1)

    # gouden binnenkader
    pygame.draw.rect(surf, GOUD,        [38, 38, WIDTH-76, HEIGHT-76], 2, 22)
    pygame.draw.rect(surf, GOUD_DONKER, [42, 42, WIDTH-84, HEIGHT-84], 1, 20)

    # dealer ellips bovenaan
    dealer_zone = [50, 50, WIDTH-100, 260]
    pygame.draw.ellipse(surf, VILT_RAND,   [dealer_zone[0]-2, dealer_zone[1]-2,
                                            dealer_zone[2]+4, dealer_zone[3]], 0)
    pygame.draw.ellipse(surf, VILT_MIDDEN, dealer_zone, 0)
    pygame.draw.ellipse(surf, GOUD,        dealer_zone, 2)

    dealer_lbl = laad_font(18).render('D E A L E R', True, GOUD)
    surf.blit(dealer_lbl, dealer_lbl.get_rect(center=(WIDTH//2, 72)))

    # inzetcirkel voor de speler
    cx, cy, r = WIDTH//2, 670, 55
    pygame.draw.circle(surf, VILT_RAND,   (cx, cy), r+3)
    pygame.draw.circle(surf, VILT_DONKER, (cx, cy), r)
    pygame.draw.circle(surf, GOUD,        (cx, cy), r,   2)
    pygame.draw.circle(surf, GOUD_DONKER, (cx, cy), r-8, 1)
    inzet_lbl = laad_font(14).render('INZET', True, GOUD)
    surf.blit(inzet_lbl, inzet_lbl.get_rect(center=(cx, cy)))

    # scorebord balk onderaan
    balk_rect = pygame.Rect(38, HEIGHT-80, WIDTH-76, 38)
    pygame.draw.rect(surf, VILT_DONKER, balk_rect, 0, 8)
    pygame.draw.rect(surf, GOUD_DONKER, balk_rect, 1, 8)

    # casino naam boven de scorebalk
    casino_lbl = laad_font(20).render('✦  ROYAL BLACKJACK  ✦', True, GOUD)
    surf.blit(casino_lbl, casino_lbl.get_rect(center=(WIDTH//2, HEIGHT-95)))

    return surf


def teken_achtergrond():
    global tafel_surf
    if tafel_surf is None:
        tafel_surf = maak_tafel()
    screen.blit(tafel_surf, (0, 0))


def teken_scorebord():
    tekst = f'Wins: {scores[0]}     Verlies: {scores[1]}     Gelijk: {scores[2]}'
    surf  = font_klein.render(tekst, True, CREME)
    screen.blit(surf, surf.get_rect(center=(WIDTH//2, HEIGHT-61)))


# --- TEKENFUNCTIES ---

def teken_kaart(x, y, waarde, symbool, verborgen=False):
    breedte = 90
    hoogte  = 130

    # schaduw
    pygame.draw.rect(screen, ZWART, [x+4, y+4, breedte, hoogte], 0, 10)

    if verborgen:
        # blauwe achterkant
        pygame.draw.rect(screen, BLAUW_DARK, [x, y, breedte, hoogte], 0, 10)

        # lijntjes patroon op de rug
        for dx in range(10, breedte, 15):
            pygame.draw.line(screen, (30, 55, 130), (x+dx, y), (x+dx, y+hoogte), 1)
        for dy in range(10, hoogte, 15):
            pygame.draw.line(screen, (30, 55, 130), (x, y+dy), (x+breedte, y+dy), 1)

        # rand
        pygame.draw.rect(screen, (40, 70, 160), [x, y, breedte, hoogte], 2, 10)

    else:
        # rood voor harten en ruiten, zwart voor de rest
        if symbool in rood_symbolen:
            kleur = ROOD
        else:
            kleur = ZWART

        # witte kaart met rand
        pygame.draw.rect(screen, WIT,         [x, y, breedte, hoogte], 0, 10)
        pygame.draw.rect(screen, GRIJS_LICHT, [x, y, breedte, hoogte], 2, 10)

        # waarde en symbool linksboven
        screen.blit(font_klein.render(waarde,  True, kleur), (x+6, y+5))
        screen.blit(font_klein.render(symbool, True, kleur), (x+6, y+22))

        # waarde en symbool rechtsonder (omgedraaid)
        waarde_surf      = font_klein.render(waarde,  True, kleur)
        symbool_surf     = font_klein.render(symbool, True, kleur)
        waarde_gedraaid  = pygame.transform.rotate(waarde_surf,  180)
        symbool_gedraaid = pygame.transform.rotate(symbool_surf, 180)

        rechts_x = x + breedte - 6
        onder_y  = y + hoogte
        screen.blit(waarde_gedraaid,  (rechts_x - waarde_gedraaid.get_width(),  onder_y - 20))
        screen.blit(symbool_gedraaid, (rechts_x - symbool_gedraaid.get_width(), onder_y - 37))

        # groot symbool in het midden
        groot_surf = font_groot.render(symbool, True, kleur)
        midden_x   = x + breedte // 2 - groot_surf.get_width()  // 2
        midden_y   = y + hoogte  // 2 - groot_surf.get_height() // 2
        screen.blit(groot_surf, (midden_x, midden_y))


def teken_knop(rect, tekst, kleur, muis, tekst_kleur=WIT):
    # lichtere kleur als de muis erop staat
    r_hover = min(kleur[0] + 30, 255)
    g_hover = min(kleur[1] + 30, 255)
    b_hover = min(kleur[2] + 30, 255)
    hover_kleur = (r_hover, g_hover, b_hover)

    if rect.collidepoint(muis):
        gebruikte_kleur = hover_kleur
    else:
        gebruikte_kleur = kleur

    # schaduw, knop, gouden rand
    schaduw_rect = [rect.x+3, rect.y+3, rect.width, rect.height]
    pygame.draw.rect(screen, ZWART,           schaduw_rect, 0, 10)
    pygame.draw.rect(screen, gebruikte_kleur, rect,         0, 10)
    pygame.draw.rect(screen, GOUD,            rect,         2, 10)

    # tekst in het midden
    tekst_surf = font.render(tekst, True, tekst_kleur)
    screen.blit(tekst_surf, tekst_surf.get_rect(center=rect.center))


def teken_chip(cx, cy, waarde, muis):
    r     = 32
    kleur = CHIP_KLEUREN.get(waarde, GRIJS)

    # lichtere kleur als de muis erop staat
    r_hover = min(kleur[0] + 40, 255)
    g_hover = min(kleur[1] + 40, 255)
    b_hover = min(kleur[2] + 40, 255)
    hover_kleur = (r_hover, g_hover, b_hover)

    # rechthoek rondom de chip voor hover check
    chip_rect = pygame.Rect(cx-r, cy-r, r*2, r*2)
    if chip_rect.collidepoint(muis):
        gebruikte_kleur = hover_kleur
    else:
        gebruikte_kleur = kleur

    # schaduw, chip, randen
    pygame.draw.circle(screen, ZWART,           (cx+3, cy+3), r)
    pygame.draw.circle(screen, gebruikte_kleur, (cx, cy),     r)
    pygame.draw.circle(screen, WIT,             (cx, cy),     r,   3)
    pygame.draw.circle(screen, gebruikte_kleur, (cx, cy),     r-6)
    pygame.draw.circle(screen, WIT,             (cx, cy),     r-6, 2)

    # tekst op de chip
    tekst_surf = font_chip.render(f'€{waarde}', True, WIT)
    screen.blit(tekst_surf, tekst_surf.get_rect(center=(cx, cy)))

    return chip_rect


# --- SPELLOGICA ---

def trek_kaart(hand, deck):
    index = random.randint(0, len(deck)-1)
    hand.append(deck[index])
    deck.pop(index)
    return hand, deck


def bereken_score(hand):
    score = 0
    azen  = 0

    # tel de score op
    for waarde, symbool in hand:
        if waarde in ['J', 'Q', 'K', '10']:
            score += 10
        elif waarde == 'A':
            score += 11
            azen  += 1
        else:
            score += int(waarde)

    # aas van 11 naar 1 als score te hoog is
    while score > 21 and azen > 0:
        score -= 10
        azen  -= 1

    return score


def is_blackjack(hand):
    # blackjack = precies 2 kaarten: een aas + een 10-waarde kaart
    if len(hand) != 2:
        return False

    wlist      = [w for w, s in hand]
    heeft_aas  = 'A' in wlist

    heeft_tien = False
    for w in wlist:
        if w in ['10', 'J', 'Q', 'K']:
            heeft_tien = True

    return heeft_aas and heeft_tien


def bepaal_uitkomst(speler_hand, dealer_hand, speler_score, dealer_score):
    if is_blackjack(speler_hand) and not is_blackjack(dealer_hand):
        return 5   # blackjack
    elif speler_score > 21:
        return 1   # speler bust
    elif dealer_score > 21 or speler_score > dealer_score:
        return 2   # speler wint
    elif speler_score < dealer_score:
        return 3   # dealer wint
    else:
        return 4   # gelijkspel


def update_scores(uitkomst, scores):
    if uitkomst in [1, 3]:
        scores[1] += 1   # verlies
    elif uitkomst in [2, 5]:
        scores[0] += 1   # winst
    else:
        scores[2] += 1   # gelijk
    return scores


def verwerk_uitbetaling(uitkomst, inzet, balans):
    if uitkomst == 5:
        balans += int(inzet * 1.5)   # blackjack: 3 op 2
    elif uitkomst == 2:
        balans += inzet              # gewonnen
    elif uitkomst in [1, 3]:
        balans -= inzet              # verloren
    return balans                    # gelijkspel: niets verandert


def reset_spelstatus():
    global spel_deck, speler_hand, dealer_hand, uitkomst
    global hand_actief, dealer_zichtbaar, score_tellen
    global speler_score, dealer_score, uitbetaald, fase

    spel_deck        = copy.deepcopy(een_deck * 4)
    speler_hand      = []
    dealer_hand      = []
    uitkomst         = 0
    hand_actief      = True
    dealer_zichtbaar = False
    score_tellen     = True
    speler_score     = 0
    dealer_score     = 0
    uitbetaald       = False
    fase             = 'spel'


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

        # balans en inzet info
        info_rect = pygame.Rect(WIDTH//2-140, 195, 280, 75)
        pygame.draw.rect(screen, VILT_DONKER, info_rect, 0, 12)
        pygame.draw.rect(screen, GOUD,        info_rect, 2, 12)
        screen.blit(font_klein.render(f'Balans: €{balans}', True, CREME),
                    (info_rect.x+16, info_rect.y+10))
        screen.blit(font_klein.render(f'Inzet:  €{inzet}',  True, GEEL),
                    (info_rect.x+16, info_rect.y+38))

        # chips tekenen
        totaal_breedte = len(chip_waarden) * 75
        start_x = WIDTH//2 - totaal_breedte//2 + 37
        for i, w in enumerate(chip_waarden):
            cx = start_x + i * 75
            cy = 390
            chip_rects.append((teken_chip(cx, cy, w, muis), w))

        # knoppen
        wis_knop   = pygame.Rect(30,  465, 160, 52)
        allin_knop = pygame.Rect(410, 465, 160, 52)
        deal_knop  = pygame.Rect(160, 535, 280, 65)

        teken_knop(wis_knop,   'WIS',    (120, 60,  10), muis)
        teken_knop(allin_knop, 'ALL IN', (140, 20, 140), muis)

        if inzet > 0:
            deal_kleur = (160, 120, 10)
        else:
            deal_kleur = (60, 60, 60)
        teken_knop(deal_knop, 'DEAL', deal_kleur, muis)

        knoppen = [('wis', wis_knop), ('allin', allin_knop), ('deal', deal_knop)]

        teken_scorebord()

    # ====================================================
    # SPEL- EN EINDEFASE
    # ====================================================
    elif fase in ('spel', 'einde'):

        # kaarten uitdelen bij het begin van een ronde
        if len(speler_hand) == 0:
            speler_hand, spel_deck = trek_kaart(speler_hand, spel_deck)
            dealer_hand, spel_deck = trek_kaart(dealer_hand, spel_deck)
            speler_hand, spel_deck = trek_kaart(speler_hand, spel_deck)
            dealer_hand, spel_deck = trek_kaart(dealer_hand, spel_deck)

        speler_score = bereken_score(speler_hand)
        dealer_score = bereken_score(dealer_hand)

        # kaarten dealer tekenen
        for i, (w, s) in enumerate(dealer_hand):
            teken_kaart(30 + i*100, 110, w, s,
                        verborgen=(i == 0 and not dealer_zichtbaar))

        # score dealer tonen als kaarten zichtbaar zijn
        if dealer_zichtbaar:
            ds = font_klein.render(f'Score: {dealer_score}', True, CREME)
            screen.blit(ds, ds.get_rect(center=(WIDTH//2, 258)))

        # kaarten speler tekenen
        for i, (w, s) in enumerate(speler_hand):
            teken_kaart(30 + i*100, 490, w, s)

        # info linksonder
        screen.blit(font_klein.render(f'Score: {speler_score}', True, CREME), (30, 635))
        screen.blit(font_klein.render(f'Balans: €{balans}',     True, CREME), (30, 658))
        screen.blit(font_klein.render(f'Inzet:  €{inzet}',      True, GEEL),  (30, 680))

        # dealer trekt automatisch bij als score onder 17 is
        if dealer_zichtbaar and dealer_score < 17:
            dealer_hand, spel_deck = trek_kaart(dealer_hand, spel_deck)

        # speler heeft 21 of meer: automatisch stoppen
        if hand_actief and speler_score >= 21:
            hand_actief      = False
            dealer_zichtbaar = True

        # controleer of het spel voorbij is
        if not hand_actief and dealer_score >= 17 and uitkomst == 0:
            uitkomst     = bepaal_uitkomst(speler_hand, dealer_hand, speler_score, dealer_score)
            scores       = update_scores(uitkomst, scores)
            score_tellen = False

        # uitbetaling eenmalig verwerken
        if uitkomst != 0 and not uitbetaald:
            balans     = verwerk_uitbetaling(uitkomst, inzet, balans)
            uitbetaald = True
            fase       = 'einde'

        # hit en stand knoppen tijdens het spel
        if fase == 'spel':
            hit_knop   = pygame.Rect(30,  760, 240, 62)
            stand_knop = pygame.Rect(330, 760, 240, 62)
            teken_knop(hit_knop,   'HIT',   (30, 130, 60), muis)
            teken_knop(stand_knop, 'STAND', (160, 30, 30), muis)
            knoppen = [('hit', hit_knop), ('stand', stand_knop)]

        teken_scorebord()

        # uitkomst overlay
        if fase == 'einde':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            # kleur van de uitkomsttekst
            if uitkomst in [2, 5]:
                tekst_kleur = (80, 220, 80)
            elif uitkomst in [1, 3]:
                tekst_kleur = (220, 80, 80)
            else:
                tekst_kleur = WIT

            uitkomst_surf = font_groot.render(uitkomst_tekst[uitkomst], True, tekst_kleur)
            screen.blit(uitkomst_surf, uitkomst_surf.get_rect(center=(WIDTH//2, 320)))

            # winst of verlies bedrag
            if uitkomst == 5:
                bedrag_tekst = f'+€{int(inzet*1.5)}  (Blackjack 3:2!)'
                bedrag_kleur = (80, 220, 80)
            elif uitkomst == 2:
                bedrag_tekst = f'+€{inzet}'
                bedrag_kleur = (80, 220, 80)
            elif uitkomst in [1, 3]:
                bedrag_tekst = f'-€{inzet}'
                bedrag_kleur = (220, 80, 80)
            else:
                bedrag_tekst = 'Inzet terug'
                bedrag_kleur = WIT

            bedrag_surf = font.render(bedrag_tekst, True, bedrag_kleur)
            screen.blit(bedrag_surf, bedrag_surf.get_rect(center=(WIDTH//2, 375)))

            balans_surf = font_klein.render(f'Nieuwe balans: €{balans}', True, WIT)
            screen.blit(balans_surf, balans_surf.get_rect(center=(WIDTH//2, 415)))

            # failliet: alleen herstart tonen
            if balans <= 0:
                failliet_surf = font.render('Geen geld meer!', True, (220, 80, 80))
                screen.blit(failliet_surf, failliet_surf.get_rect(center=(WIDTH//2, 465)))
                herstart_knop = pygame.Rect(150, 500, 300, 65)
                teken_knop(herstart_knop, 'HERSTART (€1000)', (120, 20, 20), muis)
                knoppen.append(('herstart', herstart_knop))
            else:
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
                # chip aangeklikt
                for rect, w in chip_rects:
                    if rect.collidepoint(event.pos) and inzet + w <= balans:
                        inzet += w
                # knop aangeklikt
                for naam, knop in knoppen:
                    if knop.collidepoint(event.pos):
                        if naam == 'wis':
                            inzet = 0
                        elif naam == 'allin':
                            inzet = balans
                        elif naam == 'deal' and inzet > 0:
                            reset_spelstatus()

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