"""
Menu principal do jogo
"""
import pygame
from ..constants import (
    WIDTH, HEIGHT, MENU_BG_ALPHA,
    DARK_PURPLE, PURPLE, WHITE
)
from ..effects import rainbow_color

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
        font = self.game.resource_manager.fonts[40]  # Fonte maior para melhor legibilidade
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
        
        # Calcula altura total do menu
        total_height = sum([self.game.resource_manager.fonts[32].size(item.text)[1] + 20 for item in self.items])
        
        # Posiciona os itens do menu
        y = (HEIGHT - total_height) // 2 + 50  # +50 para compensar o título
        for item in self.items:
            x = (WIDTH - self.game.resource_manager.fonts[32].size(item.text)[0]) // 2
            y = item.draw(surface, x, y)
