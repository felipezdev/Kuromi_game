"""
Sistema de efeitos visuais aprimorados
"""
import pygame
import random
import math
from .constants import (
    WIDTH, HEIGHT, WHITE, GOLD, COMBO_COLORS,
    SCORE_POPUP_DURATION, PERFECT_FLASH_DURATION,
    COMBO_METER_WIDTH, COMBO_METER_HEIGHT,
    PERSONAL_BEST_OFFSET
)

class ScorePopup:
    def __init__(self, x, y, points, color=WHITE):
        self.x = x
        self.y = y
        self.points = points
        self.color = color
        self.alpha = 255
        self.scale = 1.2
        self.dy = -2
        self.lifetime = SCORE_POPUP_DURATION
        
    def update(self):
        self.y += self.dy
        self.alpha = int(255 * (self.lifetime / SCORE_POPUP_DURATION))
        self.scale = max(1.0, self.scale - 0.01)
        self.lifetime -= 16  # ~60fps
        return self.lifetime > 0
        
    def draw(self, surface, font):
        if self.alpha <= 0:
            return
            
        text = f"+{self.points}"
        text_surf = font.render(text, True, self.color)
        
        # Aplica escala
        scaled_size = (
            int(text_surf.get_width() * self.scale),
            int(text_surf.get_height() * self.scale)
        )
        text_surf = pygame.transform.smoothscale(text_surf, scaled_size)
        
        # Aplica transparência
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.fill((255, 255, 255, self.alpha))
        text_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Desenha centralizado
        rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, rect)

class ComboMeter:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = 0
        self.target = 0
        self.color = WHITE
        
    def update(self, combo):
        self.target = combo / 10  # Normaliza para 0-1
        self.value += (self.target - self.value) * 0.1
        
        # Atualiza cor baseado no combo
        for threshold, color in sorted(COMBO_COLORS.items()):
            if combo >= threshold:
                self.color = color
                
    def draw(self, surface):
        # Barra de fundo
        pygame.draw.rect(surface, (*WHITE, 100),
                        (self.x, self.y, COMBO_METER_WIDTH, COMBO_METER_HEIGHT),
                        border_radius=COMBO_METER_HEIGHT//2)
        
        # Barra de progresso
        if self.value > 0:
            width = int(COMBO_METER_WIDTH * self.value)
            pygame.draw.rect(surface, self.color,
                           (self.x, self.y, width, COMBO_METER_HEIGHT),
                           border_radius=COMBO_METER_HEIGHT//2)
            
        # Borda
        pygame.draw.rect(surface, WHITE,
                        (self.x, self.y, COMBO_METER_WIDTH, COMBO_METER_HEIGHT),
                        2, border_radius=COMBO_METER_HEIGHT//2)

class VisualEffectsManager:
    def __init__(self, game):
        self.game = game
        self.score_popups = []
        self.combo_meter = ComboMeter(
            (WIDTH - COMBO_METER_WIDTH) // 2,
            HEIGHT - COMBO_METER_HEIGHT - 10
        )
        self.perfect_flash = 0
        self.perfect_count = 0
        
    def add_score_popup(self, x, y, points, color=WHITE):
        self.score_popups.append(ScorePopup(x, y, points, color))
        
    def show_perfect_flash(self):
        self.perfect_flash = PERFECT_FLASH_DURATION
        self.perfect_count += 1
        
    def update(self):
        # Atualiza popups de pontuação
        self.score_popups = [p for p in self.score_popups if p.update()]
        
        # Atualiza medidor de combo
        self.combo_meter.update(self.game.score_manager.combo)
        
        # Atualiza flash de perfect
        if self.perfect_flash > 0:
            self.perfect_flash -= 16
            
    def draw(self, surface):
        # Desenha medidor de combo
        self.combo_meter.draw(surface)
        
        # Desenha popups de pontuação
        for popup in self.score_popups:
            popup.draw(surface, self.game.resource_manager.fonts[24])
            
        # Desenha flash de perfect
        if self.perfect_flash > 0:
            alpha = int(255 * (self.perfect_flash / PERFECT_FLASH_DURATION))
            text = "PERFECT!"
            text_surf = self.game.resource_manager.fonts[48].render(text, True, GOLD)
            text_surf.set_alpha(alpha)
            rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            surface.blit(text_surf, rect)
            
        # Desenha indicador de recorde pessoal
        if (self.game.score_manager.current_score > 0 and
            self.game.score_manager.current_score > self.game.score_manager.highest_score):
            text = "NEW BEST!"
            text_surf = self.game.resource_manager.fonts[24].render(text, True, GOLD)
            rect = text_surf.get_rect(
                centerx=WIDTH//2,
                top=PERSONAL_BEST_OFFSET
            )
            surface.blit(text_surf, rect)
