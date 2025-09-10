"""
Classe principal do jogo Kuromi Catch
"""
import pygame
import sys
import random
import math
from .constants import (
    WIDTH, HEIGHT, FPS, TITLE, START_LIVES, LEVEL_SPEED_INCREASE,
    LEVEL_SCORE_MULTIPLIER, COMBO_MULTIPLIER, BLACK, WHITE, GOLD, 
    PINK, PURPLE, DARK_PURPLE, GAME_MODES, MIN_SPAWN_MS, START_SPAWN_MS, 
    SPAWN_DECREASE_AMOUNT, POINTS_PER_LEVEL, MAX_LEVEL, POWERUP_MIN_INTERVAL,
    POWERUP_CHANCE
)
from .sprites import Player, Item, PowerUp
from .effects import ParticleSystem
from .managers import ResourceManager, ScoreManager, AchievementManager
from .ui.modes_menu import ModesMenu
from .ui import Menu, PauseMenu, HUD
from .modes import GameModeManager, DailyObjectivesManager
from .visual_effects import VisualEffectsManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.state = 'menu'
        self.running = True
        self.paused = False
        
        # Managers
        self.resource_manager = ResourceManager()
        self.score_manager = ScoreManager()
        self.score_manager.game = self  # Define a referência ao jogo
        self.achievement_manager = AchievementManager()
        self.particle_system = ParticleSystem(self)
        self.game_mode_manager = GameModeManager(self)
        self.daily_objectives_manager = DailyObjectivesManager(self)
        self.visual_effects_manager = VisualEffectsManager(self)
        
        # UI
        self.menu = Menu(self)
        self.pause_menu = PauseMenu(self)
        self.modes_menu = ModesMenu(self)
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
        self.state = 'game'
        self.player = Player(self)
        self.start_time = pygame.time.get_ticks()  # Registra o tempo inicial
        self.reset_game_state()
        
    def reset_game_state(self):
        self.level = 1
        self.score_manager.reset()
        self.game_time = 0
        self.spawn_timer = 0
        self.start_time = pygame.time.get_ticks()  # Atualiza o tempo inicial
        self.last_spawn = pygame.time.get_ticks()
        self.items.empty()
        self.powerups.empty()
        
        # Reset dos modificadores de modo
        self.speed_multiplier = 1.0
        self.spawn_multiplier = 1.0
        self.score_multiplier = 1.0
        self.spawn_bad_items = True
        self.required_accuracy = 0.0
        
    def update(self):
        if self.state == 'menu':
            self.menu.update()
        elif self.state == 'pause':
            self.pause_menu.update()
        elif self.state == 'game' and not self.paused:
            self.update_game()
            
        # Atualiza partículas em todos os estados
        self.particle_system.update()
            
    def update_game(self):
        # Atualiza tempo de jogo
        self.game_time = pygame.time.get_ticks()
        elapsed_time = self.game_time - self.start_time
        
        # Atualiza objetivo de sobrevivência
        self.daily_objectives_manager.update_progress('survive_time', elapsed_time // 1000)
        
        # Verifica game over
        if self.player.lives <= 0:
            self.state = 'gameover'
            self.score_manager.check_highscore()
            return
        
        # Atualiza modo de jogo
        self.game_mode_manager.update()
        
        # Spawna itens
        current_time = pygame.time.get_ticks()
        base_delay = max(MIN_SPAWN_MS, 
                        START_SPAWN_MS - (self.level * SPAWN_DECREASE_AMOUNT))
        
        # Aplica modificador do modo de jogo
        mode = GAME_MODES.get(self.game_mode_manager.current_mode)
        if mode:
            spawn_delay = base_delay / mode.get('spawn_mult', 1.0)
        else:
            spawn_delay = base_delay
                         
        if current_time - self.last_spawn > spawn_delay:
            self.spawn_item()
            self.last_spawn = current_time
            
        # Atualiza objetos
        self.player.update()
        self.items.update()
        self.powerups.update()
        
        # Atualiza efeitos visuais
        self.visual_effects_manager.update()
        
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
        base_points = 10 if item.is_good else -10
        points = base_points * self.level * LEVEL_SCORE_MULTIPLIER
        points *= (1 + self.score_manager.combo * COMBO_MULTIPLIER)
        
        # Aplica multiplicador do modo de jogo
        points *= self.score_multiplier
        
        if item.is_good:
            self.score_manager.add_combo()
            self.particle_system.emit_particles('sparkle', item.rect.center)
            self.resource_manager.play_sound('catch')
            
            # Atualiza objetivos diários
            self.daily_objectives_manager.update_progress('catch_items', 
                self.score_manager.items_collected + 1)
            self.daily_objectives_manager.update_progress('reach_combo', 
                self.score_manager.combo)
            
            # Efeitos visuais baseados no combo
            color = GOLD if self.score_manager.combo >= 10 else WHITE
            self.visual_effects_manager.add_score_popup(
                item.rect.centerx, item.rect.centery,
                int(points), color
            )
            
            # Checa perfect catch
            if self.score_manager.perfect_streak >= 5:
                self.visual_effects_manager.show_perfect_flash()
                
        else:
            self.score_manager.reset_combo()
            self.player.take_damage()
            self.particle_system.emit_particles('explosion', item.rect.center)
            self.resource_manager.play_sound('fail')
            
        self.score_manager.add_score(int(points))
        item.kill()
        
        # Atualiza objetivos baseados em pontuação
        self.daily_objectives_manager.update_progress('score_points', 
            self.score_manager.current_score)
        
        # Atualiza contadores do modo de jogo
        if self.game_mode_manager.current_mode != 'normal':
            self.game_mode_manager.items_caught += 1
        
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
        if random.random() < self.spawn_multiplier:  # Considera o multiplicador de spawn
            item = Item(self)
            if not self.spawn_bad_items:  # No modo Chuva de Doces, força itens bons
                item.is_good = True
            self.items.add(item)
            self.game_mode_manager.items_spawned += 1
            
            if (pygame.time.get_ticks() - self.last_powerup_time > POWERUP_MIN_INTERVAL and 
                random.random() < POWERUP_CHANCE):
                powerup = PowerUp(self)
                self.powerups.add(powerup)
                self.last_powerup_time = pygame.time.get_ticks()
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Atualiza e desenha o background com transição
        if self.state == 'game' or self.state == 'pause':
            self.resource_manager.update_background(self.level)
        self.resource_manager.draw_background(self.screen)
            
        if self.state == 'menu':
            self.menu.draw(self.screen)
        elif self.state == 'game' or self.state == 'pause':
            self.draw_game()
            if self.state == 'pause':
                self.pause_menu.draw(self.screen)
        elif self.state == 'instructions':
            self.draw_instructions()
        elif self.state == 'highscore':
            self.draw_highscores()
        elif self.state == 'gameover':
            self.draw_game_over()
        elif self.state == 'characters':
            self.draw_characters()
        elif self.state == 'modes':
            self.modes_menu.draw(self.screen)
            self.modes_menu.update()
        elif self.state == 'objectives':
            self.daily_objectives_manager.draw(self.screen)
        
        # Desenha partículas em todos os estados
        self.particle_system.draw(self.screen)
        pygame.display.flip()
        
    def draw_game(self):
        # Desenha objetos do jogo
        self.items.draw(self.screen)
        self.powerups.draw(self.screen)
        self.player.draw(self.screen)
        
            # Desenha HUD básico
        self.hud.draw(self.screen)
        
        # Desenha efeitos visuais aprimorados
        self.visual_effects_manager.draw(self.screen)
        
        # Desenha indicador de modo de jogo
        if self.game_mode_manager.current_mode != 'normal':
            mode = GAME_MODES[self.game_mode_manager.current_mode]
            mode_text = mode['name']
            text_surf = self.resource_manager.fonts[32].render(mode_text, True, GOLD)
            rect = text_surf.get_rect(centerx=WIDTH//2, top=10)
            self.screen.blit(text_surf, rect)
        
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
                    if self.state == 'game':
                        self.state = 'pause'  # Mostra o menu de pausa
                        self.paused = True
                    elif self.state in ['instructions', 'highscore', 'characters', 'gameover', 'modes', 'objectives']:
                        self.state = 'menu'
                        
                if event.key == pygame.K_r and self.state == 'gameover':
                    self.start_game()
                    
            # Verifica fim da música
            self.resource_manager.check_music_end(event)
                
            if self.state == 'menu':
                self.menu.handle_event(event)
            elif self.state == 'pause':
                self.pause_menu.handle_event(event)
            elif self.state == 'modes':
                self.modes_menu.handle_event(event)
            elif self.state == 'characters' and event.type == pygame.MOUSEBUTTONDOWN:
                # Posições dos personagens
                y = 150
                kuromi_rect = self.resource_manager.images['player'].get_rect(center=(WIDTH // 4, y + 120))
                melody_rect = self.resource_manager.images['player2'].get_rect(center=(WIDTH * 3 // 4, y + 120))
                
                # Checa se clicou em algum personagem
                mouse_pos = pygame.mouse.get_pos()
                if kuromi_rect.collidepoint(mouse_pos):
                    self.resource_manager.selected_character = 'player'
                    self.resource_manager.play_sound('catch')
                elif melody_rect.collidepoint(mouse_pos):
                    char_data = self.resource_manager.unlockable_characters['player2']
                    if char_data['unlocked'] or self.score_manager.highest_score >= char_data['score']:
                        self.resource_manager.selected_character = 'player2'
                        self.resource_manager.play_sound('catch')
                        
        # Processa movimento contínuo do jogador
        if self.state == 'game' and not self.paused:
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
            self.state = 'pause'
            self.paused = True
            
    def unpause(self):
        self.paused = False
        self.state = 'game'
        
    def return_to_menu(self):
        self.state = 'menu'
        self.paused = False
        self.reset_game_state()
        
    def show_instructions(self):
        self.state = 'instructions'
        
    def show_highscores(self):
        self.state = 'highscore'
        
    def show_characters(self):
        self.state = 'characters'
        
    def show_modes(self):
        self.state = 'modes'
        
    def show_objectives(self):
        self.state = 'objectives'
        
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
        
        # Personagem padrão
        x = WIDTH // 4
        char_text = "Kuromi"
        text_surf = self.resource_manager.fonts[32].render(char_text, True, WHITE)
        text_x = x - text_surf.get_width() // 2
        self.screen.blit(text_surf, (text_x, y))
        
        # Status e animação do personagem
        is_selected = self.resource_manager.selected_character == 'player'
        scale = 1.1 if is_selected else 1.0
        status_text = "Selecionado" if is_selected else "Clique para selecionar"
        status_color = GOLD if is_selected else WHITE
        
        status_surf = self.resource_manager.fonts[24].render(status_text, True, status_color)
        status_x = x - status_surf.get_width() // 2
        self.screen.blit(status_surf, (status_x, y + 40))
        
        player_img = self.resource_manager.images['player']
        scaled_img = pygame.transform.smoothscale(
            player_img, 
            (int(player_img.get_width() * scale), 
             int(player_img.get_height() * scale))
        )
        
        player_rect = scaled_img.get_rect(center=(x, y + 120))
        self.screen.blit(scaled_img, player_rect)
        
        # Desenha borda ao redor do personagem selecionado
        if is_selected:
            pygame.draw.rect(self.screen, GOLD, player_rect.inflate(10, 10), 3, border_radius=10)
            # Adiciona partículas de destaque
            if random.random() < 0.1:
                angle = random.uniform(0, math.pi * 2)
                px = player_rect.centerx + math.cos(angle) * 40
                py = player_rect.centery + math.sin(angle) * 40
                self.particle_system.add_particle(px, py, GOLD, 3, 400, gravity=False)
        
        # Personagem desbloqueável
        x = WIDTH * 3 // 4
        char_text = "My Melody"
        
        # Verifica se está desbloqueado
        char_data = self.resource_manager.unlockable_characters['player2']
        is_unlocked = char_data['unlocked'] or self.score_manager.highest_score >= char_data['score']
        
        if is_unlocked:
            text_color = WHITE
            player_img = self.resource_manager.images['player2']
            is_selected = self.resource_manager.selected_character == 'player2'
            status_text = "Selecionado" if is_selected else "Clique para selecionar"
            status_color = GOLD if is_selected else WHITE
            scale = 1.1 if is_selected else 1.0
        else:
            text_color = DARK_PURPLE
            player_img = self.resource_manager.images['player2'].copy()
            dark = pygame.Surface(player_img.get_size()).convert_alpha()
            dark.fill((0, 0, 0, 128))
            player_img.blit(dark, (0, 0))
            status_text = f"Desbloqueio: {150000:,} pontos"
            status_color = DARK_PURPLE
            scale = 0.9
            is_selected = False
        
        text_surf = self.resource_manager.fonts[32].render(char_text, True, text_color)
        status_surf = self.resource_manager.fonts[24].render(status_text, True, status_color)
        
        text_x = x - text_surf.get_width() // 2
        status_x = x - status_surf.get_width() // 2
        self.screen.blit(text_surf, (text_x, y))
        self.screen.blit(status_surf, (status_x, y + 40))
        
        scaled_img = pygame.transform.smoothscale(
            player_img, 
            (int(player_img.get_width() * scale), 
             int(player_img.get_height() * scale))
        )
        
        player_rect = scaled_img.get_rect(center=(x, y + 120))
        self.screen.blit(scaled_img, player_rect)
        
        # Desenha borda ao redor do personagem selecionado
        if is_selected:
            pygame.draw.rect(self.screen, GOLD, player_rect.inflate(10, 10), 3, border_radius=10)
            # Adiciona partículas de destaque
            if random.random() < 0.1:
                angle = random.uniform(0, math.pi * 2)
                px = player_rect.centerx + math.cos(angle) * 40
                py = player_rect.centery + math.sin(angle) * 40
                self.particle_system.add_particle(px, py, GOLD, 3, 400, gravity=False)
        
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
