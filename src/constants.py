"""
Constantes e configurações para o Kuromi Catch
"""
import os
from datetime import datetime

# --- Configurações da Janela ---
WIDTH = 1024
HEIGHT = 768
FPS = 60
TITLE = "✨ Kuromi Catch ✨"

# --- Configurações do Jogo ---
START_LIVES = 5
START_SPAWN_MS = 1000
MIN_SPAWN_MS = 300
SPAWN_DECREASE_EVERY = 15000
SPAWN_DECREASE_AMOUNT = 40

# --- Movimento ---
PLAYER_SPEED = 8
ITEM_SPEED = 5
BASE_FALL_SPEED = 2.2
SPEED_INCREASE_PER_SCORE = 0.008

# --- Sistema de Níveis ---
POINTS_PER_LEVEL = 100
MAX_LEVEL = 10
LEVEL_SPEED_INCREASE = 0.2  # Aumento de velocidade por nível
LEVEL_SCORE_MULTIPLIER = 1.2  # Multiplicador de pontos por nível

# --- Power-ups ---
POWERUP_CHANCE = 0.15  # 15% de chance
POWERUP_DURATION = 8000  # 8 segundos
MAGNET_RANGE = 200  # Aumentado o alcance
MAGNET_FORCE = 8  # Aumentada a força de atração do ímã
SHIELD_DURATION = 10000
MULTIPLIER_VALUE = 2.0
POWERUP_MIN_INTERVAL = 5000  # Tempo mínimo entre power-ups

# --- Sistema de Combos ---
COMBO_TIME = 2000
COMBO_MULTIPLIER = 0.2  # Cada combo aumenta 20% dos pontos
MAX_COMBO = 10

# --- Cores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
DARK_PINK = (255, 105, 180)
PURPLE = (147, 112, 219)
DARK_PURPLE = (72, 61, 139)
YELLOW = (255, 255, 150)
GOLD = (255, 215, 0)
SPARKLE_COLORS = [(255,223,186), (255,192,203), (230,230,250)]

# --- Partículas ---
MAX_PARTICLES = 50
PARTICLE_LIFETIME = 1000
RAINBOW_SPEED = 0.02

# --- UI ---
MENU_BG_ALPHA = 180
PAUSE_BG_ALPHA = 150
PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_Y = 50  # Posição Y da barra de progresso
HEART_SIZE = 32

# --- Diretórios ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "kawaii.ttf")
SAVE_PATH = os.path.join(BASE_DIR, "save_data")
HIGHSCORE_FILE = os.path.join(SAVE_PATH, "highscores.json")
ACHIEVEMENTS_FILE = os.path.join(SAVE_PATH, "achievements.json")

# --- Conquistas ---
ACHIEVEMENTS = {
    'combo_master': {'name': '✨ Combo Master', 'desc': 'Atingiu combo 10x', 'req': 10},
    'survivor': {'name': '💖 Survivor', 'desc': 'Sobreviveu 2 minutos', 'req': 120000},
    'collector': {'name': '🌟 Collector', 'desc': 'Pegou 50 itens', 'req': 50},
    'powerup_lover': {'name': '⭐ Power-up Lover', 'desc': 'Pegou todos os power-ups', 'req': 3},
    'perfect': {'name': '🎀 Perfect', 'desc': 'Pegou 20 itens sem errar', 'req': 20},
    'new_char_player2': {'name': '🌟 Novo Personagem!', 'desc': 'Desbloqueou personagem alternativo!', 'req': 150000}
}

# --- Partículas e Efeitos ---
MAX_PARTICLES = 50
PARTICLE_LIFETIME = 1000
SPARKLE_COLORS = [(255,223,186), (255,192,203), (230,230,250)]
RAINBOW_SPEED = 0.02

# --- UI ---
MENU_BG_ALPHA = 180
PAUSE_BG_ALPHA = 150
HEART_SIZE = 30
PROGRESS_BAR_HEIGHT = 20
ACHIEVEMENT_DISPLAY_TIME = 3000

# --- Caminhos ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "kawaii.ttf")
SAVE_PATH = os.path.join(BASE_DIR, "save_data")
HIGHSCORE_FILE = os.path.join(SAVE_PATH, "highscores.json")
ACHIEVEMENTS_FILE = os.path.join(SAVE_PATH, "achievements.json")

# --- Cores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
DARK_PINK = (255, 105, 180)
PURPLE = (147, 112, 219)
DARK_PURPLE = (72, 61, 139)
YELLOW = (255, 255, 150)
GOLD = (255, 215, 0)

# Lista de cores para efeitos rainbow
RAINBOW_COLORS = [
    (255, 105, 180),  # Pink
    (147, 112, 219),  # Purple
    (255, 255, 150),  # Yellow
    (173, 216, 230),  # Light Blue
    (144, 238, 144),  # Light Green
]

# --- Sistema de Objetivos Diários ---
DAILY_OBJECTIVES = {
    'catch_items': {'name': '🍰 Coletor de Doces', 'desc': 'Pegue {} doces', 'max': 50},
    'reach_combo': {'name': '✨ Combo Master', 'desc': 'Alcance um combo {}x', 'max': 8},
    'score_points': {'name': '⭐ Pontuador', 'desc': 'Faça {} pontos', 'max': 1000},
    'survive_time': {'name': '⏰ Sobrevivente', 'desc': 'Sobreviva por {} segundos', 'max': 60},
    'perfect_catch': {'name': '💖 Perfeição', 'desc': 'Pegue {} doces sem errar', 'max': 15}
}
DAILY_OBJECTIVES_REWARD = 500
OBJECTIVES_FILE = os.path.join(SAVE_PATH, "daily_objectives.json")

# --- Modos de Jogo ---
GAME_MODES = {
    'candy_rain': {
        'name': '� Chuva de Doces',
        'desc': 'Somente doces caem do céu!',
        'long_desc': 'Uma chuva mágica faz com que apenas doces deliciosos caiam por 30 segundos! Aproveite para fazer combos incríveis!',
        'duration': 30000,
        'score_mult': 1.2,
        'difficulty': 1,
        'effects': ['Apenas itens bons', 'Duração limitada', 'Bônus de pontos: 20%']
    },
    'speed_rush': {
        'name': '⚡ Corrida Veloz',
        'desc': 'Tudo em alta velocidade!',
        'long_desc': 'Os itens caem muito mais rápido, mas você ganha o dobro de pontos! Teste seus reflexos neste modo desafiador!',
        'speed_mult': 1.8,
        'score_mult': 2.0,
        'difficulty': 2,
        'effects': ['Velocidade aumentada em 80%', 'Pontuação dobrada', 'Dificuldade alta']
    },
    
    }
MODES_FILE = os.path.join(SAVE_PATH, "game_modes.json")

# --- Efeitos Visuais ---
SCORE_POPUP_DURATION = 1000  # Duração dos números flutuantes
PERFECT_FLASH_DURATION = 500  # Duração do flash "PERFECT!"
COMBO_METER_WIDTH = 200
COMBO_METER_HEIGHT = 20
PERSONAL_BEST_OFFSET = 50  # Distância do indicador de recorde pessoal

COMBO_COLORS = {
    3: YELLOW,
    5: PINK,
    7: PURPLE,
    10: GOLD
}

# --- Estados do Jogo ---
STATE_MENU = 'menu'
STATE_GAME = 'game'
STATE_PAUSE = 'pause'
STATE_GAMEOVER = 'gameover'
STATE_INSTRUCTIONS = 'instructions'
STATE_HIGHSCORE = 'highscore'
STATE_CHARACTERS = 'characters'
STATE_MODES = 'modes'  # Novo estado para seleção de modo
STATE_OBJECTIVES = 'objectives'  # Novo estado para objetivos diários
