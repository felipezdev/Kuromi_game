"""
Gerenciadores de estado do jogo e recursos
"""
import pygame
import json
import os
import random
from .constants import *

class ScoreManager:
    def __init__(self):
        self.game = None  # Será definido quando o jogo for criado
        self.highscores = self.load_highscores()
        self.reset()
        
    def reset(self):
        """Reseta as variáveis do score"""
        self.current_score = 0
        self.combo = 0
        self.last_catch_time = 0
        self.items_collected = 0
        self.perfect_streak = 0
        # Mantém o recorde mesmo após resetar
        self.highest_score = max(self.highscores) if self.highscores else 0
        
    def add_combo(self):
        """Aumenta o combo quando pega um item bom"""
        now = pygame.time.get_ticks()
        if now - self.last_catch_time < COMBO_TIME:
            self.combo = min(self.combo + 1, MAX_COMBO)
        else:
            self.combo = 1
        self.last_catch_time = now
        
    def reset_combo(self):
        """Reseta o combo quando pega um item ruim"""
        self.combo = 0
        self.perfect_streak = 0
        
    def load_highscores(self):
        try:
            with open(HIGHSCORE_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
            
    def save_highscores(self):
        os.makedirs(os.path.dirname(HIGHSCORE_FILE), exist_ok=True)
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(self.highscores, f)
            
    def add_score(self, points, has_multiplier=False):
        if has_multiplier:
            points *= MULTIPLIER_VALUE
            
        # Aplica multiplicador de combo
        combo_mult = 1 + (self.combo - 1) * COMBO_MULTIPLIER
        points *= combo_mult
        
        old_score = self.current_score
        self.current_score += int(points)
        
        # Verifica desbloqueio de personagens
        for char, data in self.game.resource_manager.unlockable_characters.items():
            if not data['unlocked'] and old_score < data['score'] and self.current_score >= data['score']:
                data['unlocked'] = True
                # Adiciona mensagem de desbloqueio ao achievement manager
                self.game.achievement_manager.pending_achievements.append(f"new_char_{char}")
        
    def update_combo(self):
        now = pygame.time.get_ticks()
        if now - self.last_catch_time < COMBO_TIME:
            self.combo = min(self.combo + 1, MAX_COMBO)
        else:
            self.combo = 1
        self.last_catch_time = now
        
    def break_combo(self):
        self.combo = 0
        
    def check_highscore(self):
        if not self.highscores or self.current_score > min(self.highscores):
            self.highscores.append(self.current_score)
            self.highscores.sort(reverse=True)
            self.highscores = self.highscores[:5]  # Mantém top 5
            self.save_highscores()
            return True
        return False

class AchievementManager:
    def __init__(self):
        self.achievements = self.load_achievements()
        self.pending_achievements = []
        self.display_queue = []
        self.display_timer = 0
        
    def load_achievements(self):
        try:
            with open(ACHIEVEMENTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {name: False for name in ACHIEVEMENTS.keys()}
            
    def save_achievements(self):
        os.makedirs(os.path.dirname(ACHIEVEMENTS_FILE), exist_ok=True)
        with open(ACHIEVEMENTS_FILE, 'w') as f:
            json.dump(self.achievements, f)
            
    def check_achievement(self, name, value):
        if not self.achievements.get(name, False) and value >= ACHIEVEMENTS[name]['req']:
            self.achievements[name] = True
            self.pending_achievements.append(name)
            self.save_achievements()
            
    def update(self):
        now = pygame.time.get_ticks()
        
        # Adiciona conquistas pendentes à fila de exibição
        while self.pending_achievements:
            self.display_queue.append({
                'name': self.pending_achievements.pop(0),
                'time': now
            })
            
        # Remove conquistas antigas da fila
        self.display_queue = [
            ach for ach in self.display_queue
            if now - ach['time'] < ACHIEVEMENT_DISPLAY_TIME
        ]
        
    def draw(self, surface):
        if not self.display_queue:
            return
            
        y = 100
        for ach in self.display_queue:
            elapsed = pygame.time.get_ticks() - ach['time']
            if elapsed < ACHIEVEMENT_DISPLAY_TIME:
                alpha = 255
                if elapsed < 500:  # Fade in
                    alpha = int(255 * (elapsed / 500))
                elif elapsed > ACHIEVEMENT_DISPLAY_TIME - 500:  # Fade out
                    alpha = int(255 * ((ACHIEVEMENT_DISPLAY_TIME - elapsed) / 500))
                    
                achievement = ACHIEVEMENTS[ach['name']]
                text = f"{achievement['name']}"
                desc = achievement['desc']
                
                # Renderiza o texto com sombra
                font = pygame.font.Font(FONT_PATH, 24)
                text_surf = font.render(text, True, GOLD)
                desc_surf = font.render(desc, True, WHITE)
                
                # Cria superfície com transparência
                text_alpha = pygame.Surface((text_surf.get_width() + 20, text_surf.get_height() * 2 + 10), pygame.SRCALPHA)
                pygame.draw.rect(text_alpha, (*PURPLE, 180), text_alpha.get_rect(), border_radius=10)
                
                # Posiciona os textos
                text_alpha.blit(text_surf, (10, 5))
                text_alpha.blit(desc_surf, (10, 5 + text_surf.get_height()))
                
                # Aplica transparência
                text_alpha.set_alpha(alpha)
                
                # Centraliza na tela
                x = (WIDTH - text_alpha.get_width()) // 2
                surface.blit(text_alpha, (x, y))
                y += text_alpha.get_height() + 10

class ResourceManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.current_bg = 0
        self.bg_transition = 0
        self.bg_fade_speed = 0.002
        self.current_bgm = None
        
        # Cria uma superfície vazia para caso uma imagem não seja encontrada
        empty_surface = pygame.Surface((20, 20))
        empty_surface.fill((255, 255, 255))
        self.images['coin'] = empty_surface
        self.images['shield'] = empty_surface
        
        self.load_resources()
        
    def load_resources(self):
        # Carrega imagens
        self.load_image('player', os.path.join(ASSETS_DIR, "player.png"), (120, 120))  # Mantém proporção quadrada
        self.load_image('player2', os.path.join(ASSETS_DIR, "player2.png"), (120, 120))
        self.load_image('coin', os.path.join(ASSETS_DIR, "coin.png"), (40, 40))
        self.load_image('shield', os.path.join(ASSETS_DIR, "shield.png"), (40, 40))
        self.load_image('ima', os.path.join(ASSETS_DIR, "ima.png"), (40, 40))
        
        # Personagens desbloqueáveis
        self.unlockable_characters = {
            'player2': {'score': 150000, 'unlocked': False}
        }
        
        # Carrega backgrounds
        self.images['backgrounds'] = []
        backgrounds_dir = os.path.join(ASSETS_DIR, "backgrounds")
        try:
            bg = pygame.image.load(os.path.join(ASSETS_DIR, "backgrounds", "background.png")).convert()
            bg = pygame.transform.smoothscale(bg, (WIDTH, HEIGHT))
            self.images['backgrounds'].append(bg)
            
            for i in range(2, 5):
                try:
                    bg = pygame.image.load(os.path.join(backgrounds_dir, f"background{i}.png")).convert()
                    bg = pygame.transform.smoothscale(bg, (WIDTH, HEIGHT))
                    self.images['backgrounds'].append(bg)
                except:
                    print(f"Não foi possível carregar background{i}.png")
        except:
            print("Não foi possível carregar o background principal")
        
        # Carrega imagens de itens
        self.images['good'] = self.load_images_from_folder(os.path.join(ASSETS_DIR, "good"), (60, 60))
        self.images['bad'] = self.load_images_from_folder(os.path.join(ASSETS_DIR, "bad"), (60, 60))
        
        # Carrega sons
        self.load_sound('catch', os.path.join(ASSETS_DIR, "sounds", "catch.mp3"), 0.5)
        self.load_sound('fail', os.path.join(ASSETS_DIR, "sounds", "fail.mp3"), 0.5)
        self.load_sound('powerup', os.path.join(ASSETS_DIR, "sounds", "powerup.mp3"), 0.4)
        self.load_sound('levelup', os.path.join(ASSETS_DIR, "sounds", "levelup.mp3"), 0.4)
        
        # Carrega músicas
        self.bgm_tracks = [
            os.path.join(ASSETS_DIR, "sounds", "bgm.mp3"),
            os.path.join(ASSETS_DIR, "sounds", "bgm2.mp3")
        ]
        try:
            self.current_bgm = random.choice(self.bgm_tracks)
            pygame.mixer.music.load(self.current_bgm)
            pygame.mixer.music.set_volume(0.1)  # Volume a 10%
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        except:
            print("Não foi possível carregar a música de fundo")
            
        # Carrega fontes
        self.load_fonts()
        
    def load_image(self, name, path, size=None):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            self.images[name] = img
        except:
            print(f"Não foi possível carregar a imagem: {path}")
            
    def load_images_from_folder(self, folder, size=None):
        images = []
        if not os.path.isdir(folder):
            return images
        for filename in os.listdir(folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    img = pygame.image.load(os.path.join(folder, filename)).convert_alpha()
                    if size:
                        img = pygame.transform.smoothscale(img, size)
                    images.append(img)
                except:
                    print(f"Não foi possível carregar a imagem: {filename}")
        return images
        
    def load_sound(self, name, path, volume=1.0):
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.sounds[name] = sound
        except:
            print(f"Não foi possível carregar o som: {path}")
            
    def load_fonts(self):
        sizes = [16, 24, 32, 40, 48, 64]
        try:
            for size in sizes:
                self.fonts[size] = pygame.font.Font(FONT_PATH, size)
        except:
            print("Usando fonte padrão")
            for size in sizes:
                self.fonts[size] = pygame.font.SysFont(None, size)
                
    def play_sound(self, name):
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass
                
    def play_music(self):
        try:
            pygame.mixer.music.play(-1)
        except:
            pass
            
    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except:
            pass
            
    def update_background(self, level):
        # Atualiza a transição do background com base no nível
        target_bg = min((level - 1) // 3, len(self.images['backgrounds']) - 1)
        
        if target_bg != self.current_bg:
            self.bg_transition = min(1, self.bg_transition + self.bg_fade_speed)
            if self.bg_transition >= 1:
                self.current_bg = target_bg
                self.bg_transition = 0
        else:
            self.bg_transition = max(0, self.bg_transition - self.bg_fade_speed)
            
    def draw_background(self, surface):
        if not self.images['backgrounds']:
            return
            
        # Desenha o background atual
        surface.blit(self.images['backgrounds'][self.current_bg], (0, 0))
        
        # Se estiver em transição, desenha o próximo background com fade
        if self.bg_transition > 0 and self.current_bg + 1 < len(self.images['backgrounds']):
            next_bg = self.images['backgrounds'][self.current_bg + 1].copy()
            next_bg.set_alpha(int(255 * self.bg_transition))
            surface.blit(next_bg, (0, 0))
            
    def check_music_end(self, event):
        if event.type == pygame.USEREVENT + 1:  # Música terminou
            # Troca para a outra música
            next_track = self.bgm_tracks[1] if self.current_bgm == self.bgm_tracks[0] else self.bgm_tracks[0]
            try:
                pygame.mixer.music.load(next_track)
                pygame.mixer.music.play()
                self.current_bgm = next_track
            except:
                print("Não foi possível carregar a próxima música")
