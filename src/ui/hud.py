"""
HUD do jogo
"""
import pygame
from ..constants import (
    WIDTH, HEIGHT, PROGRESS_BAR_HEIGHT, POINTS_PER_LEVEL,
    HEART_SIZE, DARK_PURPLE, PURPLE, WHITE, GOLD
)
from ..effects import rainbow_color

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
            self.draw_text_with_shadow(surface, combo_text, (combo_x, 80), 32, color)
            
        # Power-ups ativos
        self.draw_powerups(surface)
        
        # Objetivos (se houver algum ativo)
        if self.game.daily_objectives_manager.active_objective:
            self.draw_objective_progress(surface)
        
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
                    if pygame.time.get_ticks() % 500 < 250:
                        surface.blit(icon, icon_rect)
                else:
                    surface.blit(icon, icon_rect)
            
            # Barra de progresso do power-up
            bar_width = 40
            bar_height = 4
            bar_x = x
            bar_y = y + 15
            
            pygame.draw.rect(surface, PURPLE,
                           (bar_x, bar_y, bar_width, bar_height),
                           border_radius=bar_height//2)
            
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                pygame.draw.rect(surface, GOLD,
                               (bar_x, bar_y, progress_width, bar_height),
                               border_radius=bar_height//2)
            
            x += 50
            
    def draw_objective_progress(self, surface):
        objective = self.game.daily_objectives_manager.active_objective
        if not objective:
            return
            
        progress = min(1.0, self.game.daily_objectives_manager.progress.get(
            objective['type'], 0) / objective['target'])
            
        text = self.game.daily_objectives_manager.get_formatted_objective(objective)
        text_surf = self.game.resource_manager.fonts[24].render(text, True, WHITE)
        x = (WIDTH - text_surf.get_width()) // 2
        y = HEIGHT - 80
        surface.blit(text_surf, (x, y))
        
        # Barra de progresso
        bar_width = 200
        bar_height = 8
        bar_x = (WIDTH - bar_width) // 2
        bar_y = HEIGHT - 60
        
        pygame.draw.rect(surface, PURPLE,
                        (bar_x, bar_y, bar_width, bar_height),
                        border_radius=bar_height//2)
        
        if progress > 0:
            progress_width = int(bar_width * progress)
            progress_color = GOLD if progress >= 1 else WHITE
            pygame.draw.rect(surface, progress_color,
                           (bar_x, bar_y, progress_width, bar_height),
                           border_radius=bar_height//2)
