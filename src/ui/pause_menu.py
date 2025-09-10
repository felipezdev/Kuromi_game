"""
Menu de pausa do jogo
"""
import pygame
from ..constants import (
    WIDTH, HEIGHT, PAUSE_BG_ALPHA,
    WHITE, DARK_PURPLE, PURPLE
)
from .menu import MenuItem

class PauseMenu:
    def __init__(self, game):
        self.game = game
        self.items = []
        self.selected = 0
        self.confirming_exit = False
        self.setup_menu()
        
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
