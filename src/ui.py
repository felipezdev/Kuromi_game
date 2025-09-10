"""
Menu e interfaces do jogo
"""
import pygame
import math
from .constants import *
from .effects import rainbow_color

class MenuItem:
    def __init__(self, text, font, callback=None):
        self.text = text
        self.font = font
        self.callback = callback
        self.selected = False
        self.hover_offset = 0
        self.color_offset = 0
        
    def update(self):
        # Animação de hover
        target = 10 if self.selected else 0
        self.hover_offset += (target - self.hover_offset) * 0.2
        self.color_offset = (self.color_offset + 0.02) % 1.0
        
    def draw(self, surface, x, y):
        color = rainbow_color(self.color_offset) if self.selected else DARK_PURPLE
        
        # Sombra
        shadow = self.font.render(self.text, True, PURPLE)
        surface.blit(shadow, (x + 2, y + 2))
        
        # Texto principal
        text = self.font.render(self.text, True, color)
        surface.blit(text, (x - self.hover_offset, y))
        
        return y + text.get_height() + 10

class Menu:
    def __init__(self, game):
        self.game = game
        self.items = []
        self.selected = 0
        self.background = None
        self.setup_menu()
        
    def setup_menu(self):
        font = self.game.resource_manager.fonts[32]
        title_font = self.game.resource_manager.fonts[64]
        
        self.items = [
            MenuItem("Jogar", font, lambda: self.game.start_game()),
            MenuItem("Modos de Jogo", font, lambda: self.game.show_modes()),
            MenuItem("Objetivos Diários", font, lambda: self.game.show_objectives()),
            MenuItem("Personagens", font, lambda: self.game.show_characters()),
            MenuItem("Instruções", font, lambda: self.game.show_instructions()),
            MenuItem("High Scores", font, lambda: self.game.show_highscores()),
            MenuItem("Sair", font, lambda: self.game.quit_game())
        ]
        
    def update(self):
        for item in self.items:
            item.update()
            
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                if self.items[self.selected].callback:
                    self.items[self.selected].callback()
                    
        # Atualiza seleção
        for i, item in enumerate(self.items):
            item.selected = (i == self.selected)
            
    def draw(self, surface):
        # Desenha background com efeito de fade
        if self.game.resource_manager.images.get('background'):
            surface.blit(self.game.resource_manager.images['background'], (0, 0))
            
        # Overlay semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(PURPLE)
        overlay.set_alpha(MENU_BG_ALPHA)
        surface.blit(overlay, (0, 0))
        
        # Título com efeito rainbow
        title = "✨ Kuromi Catch ✨"
        title_color = rainbow_color(pygame.time.get_ticks() * 0.001)
        title_surf = self.game.resource_manager.fonts[64].render(title, True, title_color)
        shadow_surf = self.game.resource_manager.fonts[64].render(title, True, DARK_PURPLE)
        
        title_x = (WIDTH - title_surf.get_width()) // 2
        title_y = 100
        
        # Desenha sombra do título
        surface.blit(shadow_surf, (title_x + 2, title_y + 2))
        surface.blit(title_surf, (title_x, title_y))
        
        # Desenha itens do menu
        y = HEIGHT // 2
        for item in self.items:
            x = (WIDTH - self.game.resource_manager.fonts[32].size(item.text)[0]) // 2
            y = item.draw(surface, x, y)

class PauseMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.confirming_exit = False
        
    def setup_menu(self):
        font = self.game.resource_manager.fonts[32]
        self.normal_items = [
            MenuItem("Continuar", font, lambda: self.game.unpause()),
            MenuItem("Menu Principal", font, lambda: self.show_confirm()),
            MenuItem("Sair", font, lambda: self.game.quit_game())
        ]
        self.confirm_items = [
            MenuItem("Sim", font, lambda: self.game.return_to_menu()),
            MenuItem("Não", font, lambda: self.hide_confirm())
        ]
        self.items = self.normal_items
        
    def show_confirm(self):
        self.confirming_exit = True
        self.items = self.confirm_items
        self.selected = 0
        
    def hide_confirm(self):
        self.confirming_exit = False
        self.items = self.normal_items
        self.selected = 1
        
    def draw(self, surface):
        # Overlay semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(PURPLE)
        overlay.set_alpha(PAUSE_BG_ALPHA)
        surface.blit(overlay, (0, 0))
        
        # Título
        if self.confirming_exit:
            title = "Voltar ao Menu Principal?"
        else:
            title = "PAUSE"
            
        title_surf = self.game.resource_manager.fonts[48].render(title, True, WHITE)
        shadow_surf = self.game.resource_manager.fonts[48].render(title, True, DARK_PURPLE)
        
        title_x = (WIDTH - title_surf.get_width()) // 2
        title_y = HEIGHT // 4
        
        surface.blit(shadow_surf, (title_x + 2, title_y + 2))
        surface.blit(title_surf, (title_x, title_y))
        
        # Itens do menu
        y = HEIGHT // 2
        for item in self.items:
            x = (WIDTH - self.game.resource_manager.fonts[32].size(item.text)[0]) // 2
            y = item.draw(surface, x, y)
        
    def draw(self, surface):
        # Overlay semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(PURPLE)
        overlay.set_alpha(PAUSE_BG_ALPHA)
        surface.blit(overlay, (0, 0))
        
        # Título
        title = "PAUSE"
        title_surf = self.game.resource_manager.fonts[48].render(title, True, WHITE)
        shadow_surf = self.game.resource_manager.fonts[48].render(title, True, DARK_PURPLE)
        
        title_x = (WIDTH - title_surf.get_width()) // 2
        title_y = HEIGHT // 4
        
        surface.blit(shadow_surf, (title_x + 2, title_y + 2))
        surface.blit(title_surf, (title_x, title_y))
        
        # Itens do menu
        y = HEIGHT // 2
        for item in self.items:
            x = (WIDTH - self.game.resource_manager.fonts[32].size(item.text)[0]) // 2
            y = item.draw(surface, x, y)

class HUD:
    def __init__(self, game):
        self.game = game
        self.heart_image = game.resource_manager.images.get('heart')
        
    def draw(self, surface):
        # Score com sombra
        score_text = f"✨ Score: {self.game.score_manager.current_score} ✨"
        self.draw_text_with_shadow(surface, score_text, (10, 10), 32)
        
        # Vidas
        if self.heart_image:
            for i in range(self.game.player.lives):
                x = WIDTH - 40 - (i * (HEART_SIZE + 5))
                y = 10
                surface.blit(self.heart_image, (x, y))
        else:
            lives_text = f"💖 x{self.game.player.lives}"
            lives_surf = self.game.resource_manager.fonts[32].render(lives_text, True, DARK_PURPLE)
            x = WIDTH - lives_surf.get_width() - 10
            self.draw_text_with_shadow(surface, lives_text, (x, 10), 32)
            
        # Nível atual
        level_text = f"🌟 Nível {self.game.level} 🌟"
        level_x = (WIDTH - self.game.resource_manager.fonts[32].size(level_text)[0]) // 2
        self.draw_text_with_shadow(surface, level_text, (level_x, 10), 32)
        
        # Barra de progresso do nível
        self.draw_level_progress(surface)
        
        # Combo
        if self.game.score_manager.combo > 1:
            combo_text = f"✨ Combo x{self.game.score_manager.combo}!"
            combo_x = (WIDTH - self.game.resource_manager.fonts[32].size(combo_text)[0]) // 2
            color = rainbow_color(pygame.time.get_ticks() * 0.001)
            self.draw_text_with_shadow(surface, combo_text, (combo_x, 80), 32, color)  # Movido para baixo
            
        # Power-ups ativos
        self.draw_powerups(surface)
        
    def draw_text_with_shadow(self, surface, text, pos, size, color=DARK_PURPLE):
        font = self.game.resource_manager.fonts[size]
        shadow = font.render(text, True, PURPLE)
        main = font.render(text, True, color)
        
        surface.blit(shadow, (pos[0] + 2, pos[1] + 2))
        surface.blit(main, pos)
        
    def draw_level_progress(self, surface):
        progress = (self.game.score_manager.current_score % POINTS_PER_LEVEL) / POINTS_PER_LEVEL
        bar_width = WIDTH * 0.4
        bar_x = (WIDTH - bar_width) // 2
        bar_y = 45
        
        # Barra de fundo
        pygame.draw.rect(surface, PURPLE, 
                        (bar_x, bar_y, bar_width, PROGRESS_BAR_HEIGHT), 
                        border_radius=PROGRESS_BAR_HEIGHT//2)
        
        # Barra de progresso
        if progress > 0:
            progress_width = bar_width * progress
            progress_color = rainbow_color(pygame.time.get_ticks() * 0.001)
            pygame.draw.rect(surface, progress_color,
                           (bar_x, bar_y, progress_width, PROGRESS_BAR_HEIGHT),
                           border_radius=PROGRESS_BAR_HEIGHT//2)
            
    def draw_powerups(self, surface):
        x = 10
        y = HEIGHT - 40
        
        for powerup in self.game.player.active_powerups:
            progress = powerup.get_progress()
            if progress <= 0:
                continue
            
            # Ícone do power-up
            icon = None
            if powerup.type == 'magnet':
                icon = self.game.resource_manager.images.get('ima')
            elif powerup.type == 'shield':
                icon = self.game.resource_manager.images.get('shield')
            elif powerup.type == 'multiplier':
                icon = self.game.resource_manager.images.get('coin')
                
            if icon:
                icon_rect = icon.get_rect(center=(x + 20, y))
                # Faz o ícone piscar quando estiver próximo do fim (menos de 30% do tempo)
                if progress < 0.3:
                    if pygame.time.get_ticks() % 500 < 250:  # Pisca a cada 0.5 segundos
                        surface.blit(icon, icon_rect)
                else:
                    surface.blit(icon, icon_rect)
            
            x += 50
            
            x += 50
