# theme.py - Thème moderne pour Abalone
import tkinter as tk
from tkinter import font

class ModernTheme:
    """Thème moderne et élégant pour le jeu Abalone"""
    
    # Palette de couleurs premium
    COLORS = {
        # Fond et surfaces
        'bg_dark': '#0f0f1a',      # Fond principal très sombre
        'bg_card': '#1a1a2e',       # Cartes et surfaces
        'bg_light': '#16213e',      # Fond secondaire
        
        # Plateforme du jeu
        'board_base': '#1e2a3e',    # Base du plateau
        'board_grad1': '#1a2744',   # Dégradé plateau (début)
        'board_grad2': '#0f1a2e',   # Dégradé plateau (fin)
        'board_border': '#ffd700',  # Bordure dorée du plateau
        
        # Pions
        'player1': '#e94560',        # Rouge rubis (Joueur 1)
        'player1_light': '#ff6b8b',  # Version claire (effet survol)
        'player2': '#00d4ff',        # Cyan néon (Joueur 2)
        'player2_light': '#4ae4ff',  # Version claire
        
        # Cavités (trous)
        'hole_dark': '#2a3a5a',
        'hole_light': '#1a2a4a',
        
        # Interface
        'gold': '#ffd700',           # Doré pour titres
        'silver': '#c0c0c0',         # Argent pour textes secondaires
        'text_primary': '#ffffff',
        'text_secondary': '#a0a0b0',
        
        # Boutons
        'btn_primary': '#e94560',
        'btn_primary_hover': '#ff6b8b',
        'btn_secondary': '#1a1a2e',
        'btn_secondary_hover': '#2a2a4e',
        
        # Effets
        'glow': '#ffffff33',
        'shadow': '#00000055',
    }
    
    # Polices modernes
    FONTS = {
        'title': ('Segoe UI', 36, 'bold'),
        'subtitle': ('Segoe UI', 18),
        'button': ('Segoe UI', 14, 'bold'),
        'score': ('Segoe UI', 12, 'bold'),
        'rules': ('Segoe UI', 10),
        'game': ('Segoe UI', 11),
    }
    
    @classmethod
    def apply_theme(cls, root):
        """Applique le thème à la fenêtre principale"""
        root.configure(bg=cls.COLORS['bg_dark'])
        root.option_add('*Font', cls.FONTS['game'])
        root.option_add('*Background', cls.COLORS['bg_dark'])
        root.option_add('*Foreground', cls.COLORS['text_primary'])
    
    @classmethod
    def create_modern_button(cls, parent, text, command, width=12, height=1):
        """Crée un bouton stylisé avec effet de survol"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=cls.COLORS['btn_primary'],
            fg=cls.COLORS['text_primary'],
            font=cls.FONTS['button'],
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            activebackground=cls.COLORS['btn_primary_hover'],
            activeforeground='white',
            width=width,
            height=height
        )
        return btn
    
    @classmethod
    def create_glow_oval(cls, canvas, x0, y0, x1, y1, color, glow=True):
        """Crée un pion avec effet de lueur"""
        # Ombre portée
        if glow:
            canvas.create_oval(
                x0+3, y0+3, x1+3, y1+3,
                fill=cls.COLORS['shadow'],
                outline='',
                width=0
            )
        
        # Pion principal
        pion = canvas.create_oval(
            x0, y0, x1, y1,
            fill=color,
            outline=cls.COLORS['gold'] if glow else cls.COLORS['silver'],
            width=2 if glow else 1
        )
        
        # Reflet (effet 3D)
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        r = (x1 - x0) / 4
        canvas.create_oval(
            cx - r/2, cy - r/2, cx + r/2, cy + r/2,
            fill=cls.COLORS['glow'],
            outline='',
            width=0
        )
        
        return pion
