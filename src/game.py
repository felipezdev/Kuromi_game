"""
Classe principal do jogo Kuromi Catch
"""
import pygame
import sys
import random
from .constants import *
from .sprites import Player, Item, PowerUp
from .effects import ParticleSystem
from .managers import ResourceManager, ScoreManager, AchievementManager
from .ui import Menu, PauseMenu, HUD

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.state = STATE_MENU
        self.running = True
        self.paused = False
        
        # Managers
        self.resource_manager = ResourceManager()
        self.score_manager = ScoreManager()
        self.score_manager.game = self  # Define a referência ao jogo
        self.achievement_manager = AchievementManager()
        self.particle_system = ParticleSystem(self)
        
        # UI
        self.menu = Menu(self)
        self.pause_menu = PauseMenu(self)
        self.hud = HUD(self)
        
        # Game objects
        self.player = None
        self.items = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Game state
        self.level = 1
        self.spawn_timer = 0
        self.last_spawn = 0
        self.last_powerup_time = 0
        self.game_time = 0
        
        # Inicia a música de fundo
        self.resource_manager.play_music()
        
    def start_game(self):
        self.state = STATE_GAME
        self.player = Player(self)
        self.reset_game_state()
        
    def reset_game_state(self):
        self.level = 1
        self.score_manager.reset()
        self.game_time = 0
        self.spawn_timer = 0
        self.last_spawn = pygame.time.get_ticks()
        self.items.empty()
        self.powerups.empty()
        
    def update(self):
        if self.state == STATE_MENU:
            self.menu.update()
        elif self.state == STATE_PAUSE:
            self.pause_menu.update()
        elif self.state == STATE_GAME and not self.paused:
            self.update_game()
            
        # Atualiza partículas em todos os estados
        self.particle_system.update()
            
    def update_game(self):
        # Atualiza tempo de jogo
        self.game_time = pygame.time.get_ticks()
        
        # Verifica game over
        if self.player.lives <= 0:
            self.state = STATE_GAMEOVER
            self.score_manager.check_highscore()
            return
        
        # Spawna itens
        current_time = pygame.time.get_ticks()
        spawn_delay = max(MIN_SPAWN_MS, 
                         START_SPAWN_MS - (self.level * SPAWN_DECREASE_AMOUNT))
                         
        if current_time - self.last_spawn > spawn_delay:
            self.spawn_item()
            self.last_spawn = current_time
            
        # Atualiza objetos
        self.player.update()
        self.items.update()
        self.powerups.update()
        
        # Checa colisões
        self.check_collisions()
        
        # Checa level up
        if self.score_manager.current_score >= self.level * POINTS_PER_LEVEL:
            self.level_up()
            
    def check_collisions(self):
        # Colisões com itens
        for item in self.items:
            if pygame.sprite.collide_rect(self.player, item):
                self.handle_item_collision(item)
                
        # Colisões com power-ups
        for powerup in self.powerups:
            if pygame.sprite.collide_rect(self.player, powerup):
                self.handle_powerup_collision(powerup)
                
    def handle_item_collision(self, item):
        points = 10 if item.is_good else -10  # Points for good and bad items
        points *= self.level * LEVEL_SCORE_MULTIPLIER
        points *= (1 + self.score_manager.combo * COMBO_MULTIPLIER)
        
        if item.is_good:
            self.score_manager.add_combo()
            self.particle_system.emit_particles('sparkle', item.rect.center)
            self.resource_manager.play_sound('catch')
        else:
            self.score_manager.reset_combo()
            self.player.take_damage()
            self.particle_system.emit_particles('explosion', item.rect.center)
            self.resource_manager.play_sound('fail')
            
        self.score_manager.add_score(points)
        item.kill()
        
    def handle_powerup_collision(self, powerup):
        powerup.apply(self.player)
        self.resource_manager.play_sound('powerup')
        self.particle_system.emit_particles('powerup', powerup.rect.center)
        powerup.kill()
        
    def level_up(self):
        if self.level < MAX_LEVEL:
            self.level += 1
            self.resource_manager.play_sound('levelup')
            self.particle_system.emit_particles('levelup', self.player.rect.center)
            
    def spawn_item(self):
        item = Item(self)
        self.items.add(item)
        if (pygame.time.get_ticks() - self.last_powerup_time > POWERUP_MIN_INTERVAL and 
            random.random() < POWERUP_CHANCE):
            powerup = PowerUp(self)
            self.powerups.add(powerup)
            self.last_powerup_time = pygame.time.get_ticks()
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Atualiza e desenha o background com transição
        if self.state == STATE_GAME or self.state == STATE_PAUSE:
            self.resource_manager.update_background(self.level)
        self.resource_manager.draw_background(self.screen)
            
        if self.state == STATE_MENU:
            self.menu.draw(self.screen)
        elif self.state == STATE_GAME or self.state == STATE_PAUSE:
            self.draw_game()
            if self.state == STATE_PAUSE:
                self.pause_menu.draw(self.screen)
        elif self.state == STATE_INSTRUCTIONS:
            self.draw_instructions()
        elif self.state == STATE_HIGHSCORE:
            self.draw_highscores()
        elif self.state == STATE_GAMEOVER:
            self.draw_game_over()
        elif self.state == STATE_CHARACTERS:
            self.draw_characters()
        
        # Desenha partículas em todos os estados
        self.particle_system.draw(self.screen)
        pygame.display.flip()
        
    def draw_game(self):
        self.items.draw(self.screen)
        self.powerups.draw(self.screen)
        self.player.draw(self.screen)
        self.hud.draw(self.screen)
        
    def draw_instructions(self):
        # Cria superfície semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(PURPLE)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title = "Como Jogar"
        title_surf = self.resource_manager.fonts[48].render(title, True, WHITE)
        title_x = (WIDTH - title_surf.get_width()) // 2
        self.screen.blit(title_surf, (title_x, 50))
        
        # Instruções
        instructions = [
            "🎮 Use as setas ou A/D para mover",
            "🍰 Colete os doces para ganhar pontos",
            "💀 Evite as caveiras",
            "✨ Faça combos para multiplicar pontos",
            "🛡️ Pegue power-ups para habilidades especiais:",
            "   • Escudo: Proteção contra perda de vidas",
            "   • Ímã: Atrai os doces",
            "   • x2: Dobra os pontos",
            "",
            "Pressione ESC para voltar"
        ]
        
        y = 150
        for line in instructions:
            text = self.resource_manager.fonts[24].render(line, True, WHITE)
            x = (WIDTH - text.get_width()) // 2
            self.screen.blit(text, (x, y))
            y += 40
            
    def draw_highscores(self):
        # Cria superfície semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(PURPLE)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title = "🏆 High Scores 🏆"
        title_surf = self.resource_manager.fonts[48].render(title, True, GOLD)
        title_x = (WIDTH - title_surf.get_width()) // 2
        self.screen.blit(title_surf, (title_x, 50))
        
        # Lista de high scores
        y = 150
        for i, score in enumerate(self.score_manager.highscores[:5], 1):
            text = f"#{i}: {score:,} pontos"
            text_surf = self.resource_manager.fonts[32].render(text, True, WHITE)
            x = (WIDTH - text_surf.get_width()) // 2
            self.screen.blit(text_surf, (x, y))
            y += 50
            
        # Instrução para voltar
        back = "Pressione ESC para voltar"
        back_surf = self.resource_manager.fonts[24].render(back, True, WHITE)
        x = (WIDTH - back_surf.get_width()) // 2
        self.screen.blit(back_surf, (x, HEIGHT - 100))
        
    def draw_game_over(self):
        # Cria superfície semi-transparente com fade
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(PURPLE)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over
        title = "✨ GAME OVER ✨"
        title_surf = self.resource_manager.fonts[64].render(title, True, PINK)
        title_x = (WIDTH - title_surf.get_width()) // 2
        self.screen.blit(title_surf, (title_x, HEIGHT//2 - 150))
        
        # Pontuação
        score_text = f"Pontuação: {self.score_manager.current_score:,}"
        score_surf = self.resource_manager.fonts[32].render(score_text, True, WHITE)
        score_x = (WIDTH - score_surf.get_width()) // 2
        self.screen.blit(score_surf, (score_x, HEIGHT//2 - 50))
        
        # Novo recorde (se aplicável)
        if self.score_manager.current_score == max(self.score_manager.highscores):
            record = "🎉 NOVO RECORDE! 🎉"
            record_surf = self.resource_manager.fonts[40].render(record, True, GOLD)
            record_x = (WIDTH - record_surf.get_width()) // 2
            self.screen.blit(record_surf, (record_x, HEIGHT//2 + 20))
        
        # Instruções
        instructions = [
            "Pressione R para jogar novamente",
            "Pressione ESC para voltar ao menu"
        ]
        
        y = HEIGHT//2 + 100
        for line in instructions:
            text = self.resource_manager.fonts[24].render(line, True, WHITE)
            x = (WIDTH - text.get_width()) // 2
            self.screen.blit(text, (x, y))
            y += 40
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_GAME:
                        self.state = STATE_PAUSE  # Mostra o menu de pausa
                        self.paused = True
                    elif self.state in [STATE_INSTRUCTIONS, STATE_HIGHSCORE, STATE_CHARACTERS, STATE_GAMEOVER]:
                        self.state = STATE_MENU
                        
                if event.key == pygame.K_r and self.state == STATE_GAMEOVER:
                    self.start_game()
                    
            # Verifica fim da música
            self.resource_manager.check_music_end(event)
                
            if self.state == STATE_MENU:
                self.menu.handle_event(event)
            elif self.state == STATE_PAUSE:
                self.pause_menu.handle_event(event)
                        
        # Processa movimento contínuo do jogador
        if self.state == STATE_GAME and not self.paused:
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if self.player:
                self.player.move(dx)
                        
    def toggle_pause(self):
        if not self.paused:
            self.state = STATE_PAUSE
            self.paused = True
            
    def unpause(self):
        self.paused = False
        self.state = STATE_GAME
        
    def return_to_menu(self):
        self.state = STATE_MENU
        self.paused = False
        self.reset_game_state()
        
    def show_instructions(self):
        self.state = STATE_INSTRUCTIONS
        
    def show_highscores(self):
        self.state = STATE_HIGHSCORE
        
    def show_characters(self):
        self.state = STATE_CHARACTERS
        
    def quit_game(self):
        self.running = False
        
    def draw_characters(self):
        # Cria superfície semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(PURPLE)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title = "✨ Personagens ✨"
        title_surf = self.resource_manager.fonts[48].render(title, True, GOLD)
        title_x = (WIDTH - title_surf.get_width()) // 2
        self.screen.blit(title_surf, (title_x, 50))
        
        # Lista de personagens
        y = 150
        x = WIDTH // 4
        
        # Personagem padrão
        char_text = "Kuromi"
        text_surf = self.resource_manager.fonts[32].render(char_text, True, WHITE)
        text_x = x - text_surf.get_width() // 2
        self.screen.blit(text_surf, (text_x, y))
        
        # Status do personagem (Selecionado)
        status_text = "Selecionado"
        status_surf = self.resource_manager.fonts[24].render(status_text, True, GOLD)
        status_x = x - status_surf.get_width() // 2
        self.screen.blit(status_surf, (status_x, y + 40))
        
        player_img = self.resource_manager.images['player']
        player_rect = player_img.get_rect(center=(x, y + 120))
        self.screen.blit(player_img, player_rect)
        
        # Personagem desbloqueável
        x = WIDTH * 3 // 4
        char_text = "My Melody"
        
        # Verifica se está desbloqueado
        char_data = self.resource_manager.unlockable_characters['player2']
        is_unlocked = char_data['unlocked'] or self.score_manager.highest_score >= char_data['score']
        
        if is_unlocked:
            text_color = WHITE
            player_img = self.resource_manager.images['player2']
            status_text = "Desbloqueado!"
            status_color = GOLD
        else:
            text_color = DARK_PURPLE
            player_img = self.resource_manager.images['player2'].copy()
            # Cria uma versão escurecida da imagem
            dark = pygame.Surface(player_img.get_size()).convert_alpha()
            dark.fill((0, 0, 0, 128))
            player_img.blit(dark, (0, 0))
            status_text = f"Desbloqueio: {150000:,} pontos"
            status_color = DARK_PURPLE
        
        text_surf = self.resource_manager.fonts[32].render(char_text, True, text_color)
        status_surf = self.resource_manager.fonts[24].render(status_text, True, status_color)
        
        text_x = x - text_surf.get_width() // 2
        status_x = x - status_surf.get_width() // 2
        self.screen.blit(text_surf, (text_x, y))
        self.screen.blit(status_surf, (status_x, y + 40))
        
        player_rect = player_img.get_rect(center=(x, y + 120))
        self.screen.blit(player_img, player_rect)
        
        # Instrução para voltar
        back = "Pressione ESC para voltar"
        back_surf = self.resource_manager.fonts[24].render(back, True, WHITE)
        x = (WIDTH - back_surf.get_width()) // 2
        self.screen.blit(back_surf, (x, HEIGHT - 50))
        
        # Instrução para voltar
        back = "Pressione ESC para voltar"
        back_surf = self.resource_manager.fonts[24].render(back, True, WHITE)
        x = (WIDTH - back_surf.get_width()) // 2
        self.screen.blit(back_surf, (x, HEIGHT - 50))
        
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            
        pygame.quit()
        sys.exit()
