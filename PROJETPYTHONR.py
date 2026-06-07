import tkinter as tk
import math
from modele import plateau, billes
from PIL import Image, ImageTk
import pygame
from pygame import mixer
from playsound import playsound
import threading
from theme import ModernTheme 
if not pygame.mixer.get_init():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
# Variables globales
LONGUEUR = 800  # Taille initiale pour l'écran d'accueil
CENTRE = (LONGUEUR / 2, LONGUEUR / 2)
DIAMETRE = LONGUEUR / 1.5
JOUEUR1_IMG = None
JOUEUR2_IMG = None
shift_enfonce = False
pions_selectionnes = []
position_origine = {}
COULEUR_JOUEUR1 = "#9400D3"  # Violet
COULEUR_JOUEUR2 = "#00FFFF"  # Cyan
joueur_courant = 1  # 1 ou 2

# Directions en degrés
DIRECTIONS = {
    'est': 0,
    'nord-est': 60,
    'nord-ouest': 120,
    'ouest': 180,
    'sud-ouest': 240,
    'sud-est': 300
}

# Fenêtre principale
fenetre = tk.Tk()
fenetre.title("Abalone ")

canva = tk.Canvas(fenetre, width=LONGUEUR, height=LONGUEUR, bg="#1E2A47")
canva.pack()

# Charger et afficher l'image de fond
try:
    # 1. Chargez l'image avec Pillow
    bg_image = Image.open("bgtrois.jpg") 
    bg_image = bg_image.resize((LONGUEUR, LONGUEUR), Image.LANCZOS)
    
    # 2. Convertir en format Tkinter
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    # 3. Afficher l'image sur le canvas
    canva.create_image(0, 0, anchor="nw", image=bg_photo)
    
    # 4. Conserver une référence à l'image
    canva.bg_image = bg_photo  # Important pour éviter le garbage collection
    
except Exception as e:
    print(f"Erreur de chargement de l'image de fond: {e}")
angles = [0, 60, 120, 180, 240, 300]
liste_sommet = []

# Déclaration des variables des joueurs
joueur1 = None
joueur2 = None
joueur_actif = None

# Variables pour le plateau
rayon_trou = None
dx = None
dy = None
trous = None
plateau_billes = None
rayon_pion = None
pions_impairs_joueur_1 = []
pions_pairs_joueur_1 = []
pions_impairs_joueur_2 = []
pions_pairs_joueur_2 = []
position_trous_haut_pairs = []
position_trous_bas_impairs = []
position_trous_bas_pairs = []
position_trous_haut_impairs = []

# Variables d'interface
score_j1 = None
score_j2 = None
indicateur_tour = None


def creer_ecran_accueil():
    global fond_accueil_img
    
    # Appliquer le thème moderne
    ModernTheme.apply_theme(fenetre)
    
    # Charger l'image de fond avec gestion d'erreur
    try:
        img = Image.open("ff.jpg")
        img = img.resize((LONGUEUR, LONGUEUR), Image.LANCZOS)
        fond_accueil_img = ImageTk.PhotoImage(img)
        canva.create_image(0, 0, anchor="nw", image=fond_accueil_img, tags="accueil")
    except Exception as e:
        print(f"Erreur chargement image de fond: {e}")
        canva.create_rectangle(0, 0, LONGUEUR, LONGUEUR, 
                              fill=ModernTheme.COLORS['bg_dark'], 
                              outline="", tags="accueil")
    
    # Overlay dégradé
    canva.create_rectangle(0, 0, LONGUEUR, LONGUEUR, 
                          fill=ModernTheme.COLORS['bg_dark'], 
                          stipple="gray25", tags="accueil")
    
    # Titre avec effet d'ombre
    canva.create_text(LONGUEUR/2+5, 155, text="ABALONE", 
                     fill=ModernTheme.COLORS['shadow'],
                     font=("Segoe UI", 52, "bold"), tags="accueil")
    canva.create_text(LONGUEUR/2, 150, text="ABALONE", 
                     fill=ModernTheme.COLORS['gold'],
                     font=("Segoe UI", 52, "bold"), tags="accueil")
    
    # Sous-titre
    canva.create_text(LONGUEUR/2, 200, text="Le jeu de stratégie millénaire",
                     fill=ModernTheme.COLORS['text_secondary'],
                     font=ModernTheme.FONTS['subtitle'], tags="accueil")
    
    # Bouton Start stylisé
    btn_start = ModernTheme.create_modern_button(fenetre, "COMMENCER", lancer_jeu, width=15)
    canva.create_window(LONGUEUR/2, LONGUEUR-150, window=btn_start, tags="accueil")
    
    # Cadre des règles avec design moderne
    regles_text = """RÈGLES DU JEU

• Chaque joueur contrôle 14 billes
• Déplacez 1, 2 ou 3 billes alignées
• Poussez les billes adverses hors du plateau

SUMITO :
  • 2 billes peuvent pousser 1 bille adverse
  • 3 billes peuvent pousser 1 ou 2 billes

• Premier à éjecter 6 billes gagne !

CONTROLES :
  • Clic : sélectionner une bille
  • Shift+Clic : sélection multiple (max 3)
  • Clic à côté : pousser dans la direction"""
    
    cadre_regles = tk.Frame(canva, bg=ModernTheme.COLORS['bg_card'], 
                           bd=0, relief="flat")
    cadre_regles.place(relx=0.5, rely=0.5, anchor="center", width=500, height=320)
    
    # Titre des règles
    titre_rules = tk.Label(cadre_regles, text="📜 RÈGLES", 
                          bg=ModernTheme.COLORS['bg_card'],
                          fg=ModernTheme.COLORS['gold'],
                          font=ModernTheme.FONTS['subtitle'])
    titre_rules.pack(pady=(15,5))
    
    label_regles = tk.Label(cadre_regles, text=regles_text, 
                          justify="left", bg=ModernTheme.COLORS['bg_card'],
                          fg=ModernTheme.COLORS['text_secondary'],
                          font=ModernTheme.FONTS['rules'])
    label_regles.pack(padx=20, pady=10)
    
    canva.create_window(LONGUEUR/2, 400, window=cadre_regles, tags="accueil")
    initialiser_jeu()



class Joueur:
    def __init__(self, numero, couleur):
        self.numero = numero
        self.couleur = couleur
        self.score = 0
        self.billes = []
def toggle_musique():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

def jouer_son_ambiance():
    try:
        pygame.mixer.music.load("ambiance.mp3")  
        pygame.mixer.music.set_volume(0.3)  # Volume entre 0 et 1
        pygame.mixer.music.play(-1)  # -1 pour boucle infinie
    except Exception as e:
        print(f"Erreur lors du chargement de la musique: {e}")
def initialiser_jeu():
    # Démarrer la musique d'ambiance
    jouer_son_ambiance()
    charger_avatars()
    dessiner_plateau_3d()
    
    global score_j1, score_j2, indicateur_tour
    score_j1, score_j2, indicateur_tour = creer_avatars_et_scores()

    global rayon_trou, dx, dy, trous
    rayon_trou = DIAMETRE / 25
    dx = 40
    dy = 40
    trous = plateau()

    dessiner_ligne_haut()
    dessiner_ligne_bas()
    
    global plateau_billes, rayon_pion
    plateau_billes = billes()
    rayon_pion = DIAMETRE/30
    
    global pions_impairs_joueur_1, pions_pairs_joueur_1, pions_impairs_joueur_2, pions_pairs_joueur_2
    pions_impairs_joueur_1 = []
    pions_pairs_joueur_1 = []
    pions_impairs_joueur_2 = []
    pions_pairs_joueur_2 = []
    
    placer_pions_haut()
    placer_pions_bas()

    joueur1.billes = pions_impairs_joueur_1 + pions_pairs_joueur_1
    joueur2.billes = pions_impairs_joueur_2 + pions_pairs_joueur_2
    btn_musique = tk.Button(fenetre, text="Musique ON/OFF", command=toggle_musique)
    btn_musique.place(x=10, y=10)  # Positionnement en haut à gauche
    canva.bind("<Button-1>", on_canvas_click)

def charger_avatars():
    global JOUEUR1_IMG, JOUEUR2_IMG
    try:
        img1 = Image.open("JAMESYJAMES.PNG").resize((80, 80)) if True else None
        img2 = Image.open("LARRY.jpg").resize((80, 80)) if True else None
        if img1: JOUEUR1_IMG = ImageTk.PhotoImage(img1)
        if img2: JOUEUR2_IMG = ImageTk.PhotoImage(img2)
    except:
        pass

def creer_avatars_et_scores():
    # Cadre et avatar joueur 1
    cadre_j1 = canva.create_rectangle(20, 20, 120, 120, fill="#34495E", outline="#5D6D7E", width=2)
    if JOUEUR1_IMG:
        avatar_j1 = canva.create_image(70, 70, image=JOUEUR1_IMG)
    else:
        avatar_j1 = canva.create_oval(40, 40, 100, 100, fill=COULEUR_JOUEUR1)
    score_j1 = canva.create_text(70, 110, text=f"Score: {joueur1.score}", 
                               fill="white", font=("Arial", 10, "bold"))
    
    # Cadre et avatar joueur 2
    cadre_j2 = canva.create_rectangle(LONGUEUR-120, LONGUEUR-120, LONGUEUR-20, LONGUEUR-20, 
                                    fill="#34495E", outline="#5D6D7E", width=2)
    if JOUEUR2_IMG:
        avatar_j2 = canva.create_image(LONGUEUR-70, LONGUEUR-70, image=JOUEUR2_IMG)
    else:
        avatar_j2 = canva.create_oval(LONGUEUR-100, LONGUEUR-100, LONGUEUR-40, LONGUEUR-40, fill=COULEUR_JOUEUR2)
    score_j2 = canva.create_text(LONGUEUR-70, LONGUEUR-30, text=f"Score: {joueur2.score}", 
                               fill="white", font=("Arial", 10, "bold"))
    
    indicateur_tour = canva.create_text(LONGUEUR/2, 30, 
                                     text=f"Tour du Joueur {joueur_actif.numero}",
                                     fill="white", font=("Arial", 12, "bold"))
    return score_j1, score_j2, indicateur_tour

def dessiner_plateau_3d():
    global liste_sommet
    liste_sommet = []
    
    for angle in angles:
        sommet_x = CENTRE[0] + DIAMETRE / 2 * math.cos(math.radians(angle))
        sommet_y = CENTRE[1] + DIAMETRE / 2 * math.sin(math.radians(angle))
        liste_sommet.append((sommet_x, sommet_y))
    
    for i in range(50, 0, -1):
        ratio = i/50
        temp_sommet = []
        for x, y in liste_sommet:
            nx = CENTRE[0] + (x - CENTRE[0]) * ratio
            ny = CENTRE[1] + (y - CENTRE[1]) * ratio
            temp_sommet.extend([nx, ny])
        
        r = min(255, int(0x48 * (0.7 + 0.3 * (ratio * math.sin(math.radians(45))))))
        g = min(255, int(0x3D * (0.7 + 0.3 * (ratio * math.sin(math.radians(45))))))
        b = min(255, int(0x8B * (0.7 + 0.3 * (ratio * math.sin(math.radians(45))))))
        color = "#%02x%02x%02x" % (r, g, b)
        canva.create_polygon(temp_sommet, fill=color, outline="")
    
    border_points = []
    for x, y in liste_sommet:
        border_points.extend([x, y])
    canva.create_polygon(border_points, fill="", outline="#A5A5C7", width=4)
    
    shadow_points = []
    shadow_offset = 8
    for x, y in liste_sommet:
        shadow_points.extend([x+shadow_offset, y+shadow_offset])
    canva.create_polygon(shadow_points, fill="#000000", outline="")
    canva.lower(canva.find_all()[-1])

def create_simple_hole(x0, y0, x1, y1, color):
    canva.create_oval(x0, y0, x1, y1, fill=color, outline="#5D6D7E", width=1)

def dessiner_ligne_haut():
    milieu_ligne = len(trous) // 2
    for i in range(0, milieu_ligne + 1):
        milieu_trous = len(trous[i]) // 2
        
        if len(trous[i]) % 2 != 0:
            for j in range(len(trous[i])):
                x = (CENTRE[0] - rayon_trou) + (dx * (j - milieu_trous))
                y = (CENTRE[1] - rayon_trou) - (dy * (milieu_ligne - i) * 0.9)
                x1 = (CENTRE[0] + rayon_trou) + (dx * (j - milieu_trous))
                y1 = (CENTRE[1] + rayon_trou) - (dy * (milieu_ligne - i) * 0.9)
                position_trous_haut_impairs.append((x, y, x1, y1))
                create_simple_hole(x, y, x1, y1, "#2C3E50")
        
        else:
            for k in range(len(trous[i])):
                x = ((CENTRE[0] - rayon_trou) + (dy / 2)) + (dx * (k - milieu_trous))
                y = (CENTRE[1] - rayon_trou) - (dy * (milieu_ligne - i) * 0.9)
                x1 = ((CENTRE[0] + rayon_trou) + (dy / 2)) + (dx * (k - milieu_trous))
                y1 = (CENTRE[1] + rayon_trou) - (dy * (milieu_ligne - i) * 0.9)
                position_trous_haut_pairs.append((x, y, x1, y1))
                create_simple_hole(x, y, x1, y1, "#2C3E50")

def dessiner_ligne_bas():
    milieu_ligne = len(trous) // 2
    
    for i in range(milieu_ligne + 1, len(trous)):
        milieu_trous = len(trous[i]) // 2
        if len(trous[i]) % 2 != 0:
            for j in range(len(trous[i])):
                x = (CENTRE[0] - rayon_trou) + (dx * (j - milieu_trous))
                y = (CENTRE[1] - rayon_trou) + (dy * (i - milieu_ligne) * 0.9)
                x1 = (CENTRE[0] + rayon_trou) + (dx * (j - milieu_trous))
                y1 = (CENTRE[1] + rayon_trou) + (dy * (i - milieu_ligne) * 0.9)
                position_trous_bas_impairs.append((x, y, x1, y1))
                create_simple_hole(x, y, x1, y1, "#2C3E50")
        else:
            for k in range(len(trous[i])):
                x = ((CENTRE[0] - rayon_trou) + (dy / 2)) + (dx * (k - milieu_trous))
                y = (CENTRE[1] - rayon_trou) + (dy * (i - milieu_ligne) * 0.9)
                x1 = ((CENTRE[0] + rayon_trou) + (dy / 2)) + (dx * (k - milieu_trous))
                y1 = (CENTRE[1] + rayon_trou) + (dy * (i - milieu_ligne) * 0.9)
                position_trous_bas_pairs.append((x, y, x1, y1))
                create_simple_hole(x, y, x1, y1, "#2C3E50")

def placer_pions_haut():
    indice_impairs = 0
    indice_pair = 0
    milieu_ligne = len(plateau_billes) // 2
    
    for i in range(0, milieu_ligne + 1):
        if len(plateau_billes[i]) % 2 != 0:  
            for j in range(len(plateau_billes[i])):
                if indice_impairs < len(position_trous_haut_impairs):
                    coords = position_trous_haut_impairs[indice_impairs]
                    indice_impairs += 1
                    
                    couleur = "#94928d"  
                    if plateau_billes[i][j] == 1:
                        couleur = COULEUR_JOUEUR1  
                    elif plateau_billes[i][j] == 2:
                        couleur = "white"  
                    
                    if plateau_billes[i][j] != 0:
                        pion = canva.create_oval(coords[0], coords[1], coords[2], coords[3], fill=couleur)
                        pions_impairs_joueur_1.append(pion)
                        position_origine[pion] = coords
        else: 
            for j in range(len(plateau_billes[i])):
                if indice_pair < len(position_trous_haut_pairs):
                    coords = position_trous_haut_pairs[indice_pair]
                    indice_pair += 1
                    
                    couleur = "#94928d"  
                    if plateau_billes[i][j] == 1:
                        couleur = COULEUR_JOUEUR1  
                    elif plateau_billes[i][j] == 2:
                        couleur = "white"   
                    
                    if plateau_billes[i][j] != 0:
                        pion = canva.create_oval(coords[0], coords[1], coords[2], coords[3], fill=couleur)
                        pions_pairs_joueur_1.append(pion)
                        position_origine[pion] = coords

def placer_pions_bas():
    indice_impairs = 0
    indice_pair = 0
    milieu_ligne = len(plateau_billes) // 2

    for i in range(milieu_ligne + 1, len(plateau_billes)):
        if len(plateau_billes[i]) % 2 != 0:
            for j in range(len(plateau_billes[i])):
                if indice_impairs < len(position_trous_bas_impairs):
                    coords = position_trous_bas_impairs[indice_impairs]
                    indice_impairs += 1
                    
                    if plateau_billes[i][j] == 1:
                        couleur = COULEUR_JOUEUR1
                    elif plateau_billes[i][j] == 2:
                        couleur = COULEUR_JOUEUR2
                    else:
                        couleur = "#94928d"
                    
                    if plateau_billes[i][j] != 0:
                        pion = canva.create_oval(coords[0], coords[1], coords[2], coords[3], 
                                               fill=couleur, outline="#5D6D7E", width=1)
                        pions_impairs_joueur_2.append(pion)
                        position_origine[pion] = coords
        else: 
            for j in range(len(plateau_billes[i])):
                if indice_pair < len(position_trous_bas_pairs):
                    coords = position_trous_bas_pairs[indice_pair]
                    indice_pair += 1
                    
                    if plateau_billes[i][j] == 1:
                        couleur = COULEUR_JOUEUR1
                    elif plateau_billes[i][j] == 2:
                        couleur = COULEUR_JOUEUR2
                    else:
                        couleur = "#94928d"
                    
                    if plateau_billes[i][j] != 0:
                        pion = canva.create_oval(coords[0], coords[1], coords[2], coords[3],
                                               fill=couleur, outline="#5D6D7E", width=1)
                        pions_pairs_joueur_2.append(pion)
                        position_origine[pion] = coords

def dessiner_selection():
    for pion in joueur1.billes + joueur2.billes:
        canva.itemconfig(pion, outline="#5D6D7E", width=1)
    for pion in pions_selectionnes:
        canva.itemconfig(pion, outline="yellow", width=3)

def get_pion_a_pos(x, y):
    objets = canva.find_overlapping(x, y, x, y)
    for obj in reversed(objets):
        if obj in joueur1.billes + joueur2.billes:
            return obj
    return None

def supprimer_si_dehors(x, y):
    seuil = 20
    for pos_list in [position_trous_haut_impairs, position_trous_haut_pairs,
                     position_trous_bas_impairs, position_trous_bas_pairs]:
        for coords in pos_list:
            x0, y0, x1, y1 = coords
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            if math.hypot(x - cx, y - cy) < seuil:
                return

    pion = get_pion_a_pos(x, y)
    if pion:
        canva.delete(pion)
        if pion in joueur1.billes:
            joueur1.billes.remove(pion)
            joueur2.score += 1
            canva.itemconfig(score_j2, text=f"Score : {joueur2.score}")
        elif pion in joueur2.billes:
            joueur2.billes.remove(pion)
            joueur1.score += 1
            canva.itemconfig(score_j1, text=f"Score : {joueur1.score}")

def get_trou_a_pos(x, y):
    seuil = 20
    for pos_list in [position_trous_haut_impairs, position_trous_haut_pairs, 
                    position_trous_bas_impairs, position_trous_bas_pairs]:
        for coords in pos_list:
            x0, y0, x1, y1 = coords
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            dist = math.hypot(x - cx, y - cy)
            if dist < seuil:
                return coords
    return None

def calculer_deplacement(direction):
    step = 40
    
    if direction == 'est':
        return (step, 0)
    elif direction == 'nord-est':
        return (step//2, -int(step*0.866))
    elif direction == 'nord-ouest':
        return (-step//2, -int(step*0.866))
    elif direction == 'ouest':
        return (-step, 0)
    elif direction == 'sud-ouest':
        return (-step//2, int(step*0.866))
    elif direction == 'sud-est':
        return (step//2, int(step*0.866))
    return (0, 0)

def sont_alignes(positions, direction):
    if len(positions) == 1:
        return True
    
    centres = [( (x0+x1)/2, (y0+y1)/2 ) for (x0,y0,x1,y1) in positions]
    
    if direction in ['est', 'ouest']:
        centres.sort(key=lambda c: c[0])
    elif direction in ['nord-est', 'sud-ouest']:
        centres.sort(key=lambda c: c[0] - c[1])
    else:
        centres.sort(key=lambda c: c[0] + c[1])
    
    for i in range(1, len(centres)):
        x1, y1 = centres[i-1]
        x2, y2 = centres[i]
        distance = math.hypot(x2-x1, y2-y1)
        if not (38 <= distance <= 42):
            return False
    return True

def trouver_case_cible(positions, direction):
    if not positions:
        return None

    dx, dy = calculer_deplacement(direction)

    if direction in ['est', 'nord-est', 'sud-est']:
        x0, y0, x1, y1 = max(positions, key=lambda p: (p[0] + p[2]) / 2)
    else:
        x0, y0, x1, y1 = min(positions, key=lambda p: (p[0] + p[2]) / 2)

    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2

    nouveau_cx = cx + dx
    nouveau_cy = cy + dy

    return get_trou_a_pos(nouveau_cx, nouveau_cy)

def est_hors_plateau(position):
    if not position:
        return True
        
    x, y = (position[0] + position[2])/2, (position[1] + position[3])/2
    distance = math.hypot(x - CENTRE[0], y - CENTRE[1])
    return distance > DIAMETRE/2 + 20

def peut_pousser(pions_attaquants, direction, joueur_courant):
    if len(pions_attaquants) not in [2, 3]:
        return False, []
    
    positions = [position_origine[p] for p in pions_attaquants]
    case_cible = trouver_case_cible(positions, direction)
    if not case_cible:
        return False, []
    
    adversaire = joueur2 if joueur_courant == 1 else joueur1
    billes_adverses = []
    for pion in adversaire.billes:
        if position_origine[pion] == case_cible:
            billes_adverses.append(pion)
    
    if len(pions_attaquants) == 2 and len(billes_adverses) == 1:
        return True, billes_adverses
    elif len(pions_attaquants) == 3 and len(billes_adverses) in [1, 2]:
        return True, billes_adverses
    
    return False, []

def deplacer_pions(pions_selectionnes, direction):
    if not pions_selectionnes or not direction:
        return False

    sumito_possible, billes_a_pousser = peut_pousser(pions_selectionnes, direction, joueur_courant)
    dx, dy = calculer_deplacement(direction)

    nouvelles_positions = []
    for pion in pions_selectionnes:
        x0, y0, x1, y1 = position_origine[pion]
        new_pos = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)
        
        closest = None
        min_dist = float('inf')
        for trou in position_trous_haut_impairs + position_trous_haut_pairs + \
                   position_trous_bas_impairs + position_trous_bas_pairs:
            tx = (trou[0] + trou[2]) / 2
            ty = (trou[1] + trou[3]) / 2
            nx = (new_pos[0] + new_pos[2]) / 2
            ny = (new_pos[1] + new_pos[3]) / 2
            dist = math.hypot(nx - tx, ny - ty)
            if dist < min_dist:
                min_dist = dist
                closest = trou
        
        if min_dist > 10:
            return False
            
        nouvelles_positions.append(closest)

    for new_pos in nouvelles_positions:
        for pion in joueur1.billes + joueur2.billes:
            if pion not in pions_selectionnes and position_origine[pion] == new_pos:
                if not sumito_possible or pion not in billes_a_pousser:
                    return False

    for pion, new_pos in zip(pions_selectionnes, nouvelles_positions):
        canva.coords(pion, *new_pos)
        position_origine[pion] = new_pos
    
    if sumito_possible and billes_a_pousser:
        positions_adverses = [position_origine[p] for p in billes_a_pousser]
        case_poussee = trouver_case_cible(positions_adverses, direction)
        
        for pion in billes_a_pousser[:]:
            if not case_poussee or est_hors_plateau(case_poussee):
                canva.itemconfig(pion, fill='red')
                canva.update()
                fenetre.after(200)
                
                canva.delete(pion)
                adversaire = joueur2 if joueur_courant == 1 else joueur1
                if pion in adversaire.billes:
                    adversaire.billes.remove(pion)
                
                if joueur_courant == 1:
                    joueur1.score += 1
                    canva.itemconfig(score_j1, text=f"Score: {joueur1.score}")
                else:
                    joueur2.score += 1
                    canva.itemconfig(score_j2, text=f"Score: {joueur2.score}")
            else:
                canva.coords(pion, *case_poussee)
                position_origine[pion] = case_poussee
    
    canva.itemconfig(indicateur_tour, text=f"Tour du Joueur {3 - joueur_courant}")
    return True
 
def trouver_direction_deplacement(pions_selectionnes, position_clic):
    if not pions_selectionnes:
        return None

    coords = [position_origine[pion] for pion in pions_selectionnes]
    x_center = sum((x0+x1)/2 for (x0,y0,x1,y1) in coords) / len(coords)
    y_center = sum((y0+y1)/2 for (x0,y0,x1,y1) in coords) / len(coords)

    x_click, y_click = position_clic
    dx = x_click - x_center
    dy = y_click - y_center

    length = math.hypot(dx, dy)
    if length == 0:
        return None
    dx /= length
    dy /= length

    directions = {
        'est': (1, 0),
        'nord-est': (0.5, -0.866),
        'nord-ouest': (-0.5, -0.866),
        'ouest': (-1, 0),
        'sud-ouest': (-0.5, 0.866),
        'sud-est': (0.5, 0.866)
    }

    best_match = None
    best_score = -1

    for name, (dir_x, dir_y) in directions.items():
        score = dx*dir_x + dy*dir_y
        if score > best_score:
            best_score = score
            best_match = name

    if best_score >= 0.866:
        return best_match
    
    return None

def on_canvas_click(event):
    global joueur_courant, pions_selectionnes
    
    x, y = event.x, event.y
    pion_clic = get_pion_a_pos(x, y)
    
    if pion_clic:
        if (joueur_courant == 1 and pion_clic not in joueur1.billes) or \
           (joueur_courant == 2 and pion_clic not in joueur2.billes):
            return
        
        if (event.state & 0x0001) != 0:
            if pion_clic in pions_selectionnes:
                pions_selectionnes.remove(pion_clic)
            else:
                if len(pions_selectionnes) < 3:
                    pions_selectionnes.append(pion_clic)
        else:
            pions_selectionnes = [pion_clic]
        
        dessiner_selection()
    else:
        if not pions_selectionnes:
            return
        
        direction = trouver_direction_deplacement(pions_selectionnes, (x, y))
        
        if direction is None:
            return
        
        if deplacer_pions(pions_selectionnes, direction):
            joueur_courant = 3 - joueur_courant
            canva.itemconfig(indicateur_tour, text=f"Tour du Joueur {joueur_courant}")
            pions_selectionnes = []
            dessiner_selection()

            def afficher_ecran_fin(vainqueur):
    # Fond semi-transparent
                canva.create_rectangle(0, 0, LONGUEUR, LONGUEUR, fill="black", stipple="gray50", tags="fin")
    
    # Cadre principal
                cadre = canva.create_rectangle(LONGUEUR/4, LONGUEUR/3, 3*LONGUEUR/4, 2*LONGUEUR/3, 
                                 fill="#34495E", outline="#5D6D7E", width=3, tags="fin")
    
    # Message de victoire
    if vainqueur == 1:
        texte = f"Le Joueur 1 a gagné !"
        couleur = COULEUR_JOUEUR1
    else:
        texte = f"Le Joueur 2 a gagné !"
        couleur = COULEUR_JOUEUR2
    
    canva.create_text(LONGUEUR/2, LONGUEUR/2 - 50, text=texte, 
                     fill=couleur, font=("Courier", 24, "bold"), tags="fin")
    
    # Scores finaux
    score_text = f"Scores finaux:\nJoueur 1: {joueur1.score} points\nJoueur 2: {joueur2.score} points"
    canva.create_text(LONGUEUR/2, LONGUEUR/2, text=score_text, 
                     fill="white", font=("Courier", 14), tags="fin")
    
    # Bouton Quitter
    btn_quitter = tk.Button(fenetre, text="QUITTER", command=fenetre.destroy,
                          bg="#C76ADA", fg="white", font=("courier", 14, "bold"),
                          padx=20, pady=10)
    canva.create_window(LONGUEUR/2, LONGUEUR/2 + 80, window=btn_quitter, tags="fin")
    
    # Bouton Rejouer
    btn_rejouer = tk.Button(fenetre, text="REJOUER", command=reinitialiser_jeu,
                          bg="#4CAF50", fg="white", font=("courier", 14, "bold"),
                          padx=20, pady=10)
    canva.create_window(LONGUEUR/2, LONGUEUR/2 + 130, window=btn_rejouer, tags="fin")
    
    # Désactiver les interactions avec le plateau
    canva.unbind("<Button-1>")
def reinitialiser_jeu():
    global joueur1, joueur2, joueur_courant, pions_selectionnes
    
    # Supprimer l'écran de fin
    canva.delete("fin")
    
    # Réinitialiser les joueurs
    joueur1 = Joueur(1, COULEUR_JOUEUR1)
    joueur2 = Joueur(2, COULEUR_JOUEUR2)
    joueur_courant = 1
    pions_selectionnes = []
    
    # Réinitialiser l'interface
    canva.delete("all")
    initialiser_jeu()

creer_ecran_accueil()

fenetre.mainloop()
