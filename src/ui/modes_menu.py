"""
Menu de seleção de modos especiais de jogo
"""
import pygame
import random
import math
from ..constants import (
    WIDTH, HEIGHT, MENU_BG_ALPHA, GAME_MODES,
    WHITE, GOLD, PURPLE, DARK_PURPLE
)

class ModesMenu:
    def __init__(self, game):
        self.game = game
        self.selected_mode = 0
        self.modes_list = list(GAME_MODES.keys())
        self.animation_time = 0
        self.particles = []
        self.scroll_offset = 0
        self.mode_spacing = 200
        self.hover_scale = 1.1
        self.center_y = HEIGHT // 2
        
        # Sistema de dicas
        self.tip_alpha = 0
        self.current_tip = 0
        self.tips = [
            "Pressione ENTER para selecionar um modo",
            "Cada modo oferece um desafio único",
            "Quanto maior a dificuldade, maior a recompensa!"
        ]
        self.tip_timer = 0
        
        # Background com gradiente
        self.background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
    def wrap_text(self, text, chars_per_line):
        """Quebra o texto em linhas com número máximo de caracteres"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + 1 <= chars_per_line:
                current_line.append(word)
                current_length += word_length + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length + 1
                
        if current_line:
            lines.append(" ".join(current_line))
            
        return lines
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.state = 'menu'
            elif event.key == pygame.K_LEFT:
                self.selected_mode = (self.selected_mode - 1) % len(self.modes_list)
                # Adiciona efeito de partículas na direção do movimento
                for _ in range(5):
                    self.particles.append({
                        'pos': (WIDTH * 0.7, HEIGHT * 0.5),
                        'vel': (random.uniform(-3, -1), random.uniform(-1, 1)),
                        'lifetime': random.randint(20, 40),
                        'size': random.randint(2, 4)
                    })
            elif event.key == pygame.K_RIGHT:
                self.selected_mode = (self.selected_mode + 1) % len(self.modes_list)
                # Adiciona efeito de partículas na direção do movimento
                for _ in range(5):
                    self.particles.append({
                        'pos': (WIDTH * 0.3, HEIGHT * 0.5),
                        'vel': (random.uniform(1, 3), random.uniform(-1, 1)),
                        'lifetime': random.randint(20, 40),
                        'size': random.randint(2, 4)
                    })
            elif event.key == pygame.K_RETURN:
                mode_name = self.modes_list[self.selected_mode]
                # Efeito de partículas ao selecionar
                for _ in range(20):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(2, 5)
                    self.particles.append({
                        'pos': (WIDTH * 0.5, HEIGHT * 0.5),
                        'vel': (math.cos(angle) * speed, math.sin(angle) * speed),
                        'lifetime': random.randint(30, 60),
                        'size': random.randint(2, 4)
                    })
                self.game.game_mode_manager.start_mode(mode_name)
                self.game.start_game()
                
    def update(self):
        # Atualiza animação
        self.animation_time += 0.03
        
        # Atualiza partículas
        for particle in self.particles[:]:
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
            else:
                particle['pos'] = (
                    particle['pos'][0] + particle['vel'][0],
                    particle['pos'][1] + particle['vel'][1]
                )
                particle['vel'] = (
                    particle['vel'][0] * 0.95,
                    particle['vel'][1] * 0.95
                )
                
        # Adiciona novas partículas
        if random.random() < 0.1:
            self.particles.append({
                'pos': (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                'vel': (random.uniform(-1, 1), random.uniform(-1, 1)),
                'lifetime': random.randint(50, 100),
                'size': random.randint(1, 3)
            })
        
    def draw(self, surface):
        # Background com padrão de estrelas
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(PURPLE)
        
        # Padrão de estrelas
        for particle in self.particles:
            color = (*GOLD, int(255 * particle['lifetime']/100))
            pos = (int(particle['pos'][0]), int(particle['pos'][1]))
            size = particle['size']
            pygame.draw.circle(surface, color, pos, size)
            
        # Título principal
        title = "✨ Modos de Jogo ✨"
        title_surf = self.game.resource_manager.fonts[48].render(title, True, GOLD)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 60))
        surface.blit(title_surf, title_rect)
        
        # Subtítulo
        subtitle = "Escolha um modo especial para um desafio diferente!"
        sub_surf = self.game.resource_manager.fonts[24].render(subtitle, True, WHITE)
        sub_rect = sub_surf.get_rect(center=(WIDTH//2, 110))
        surface.blit(sub_surf, sub_rect)
        
        # Layout em grade para os modos
        card_width = 300
        card_height = 400
        spacing = 40
        start_y = 160
        
        # Calcula o total de espaço necessário
        total_width = len(self.modes_list) * (card_width + spacing) - spacing
        start_x = (WIDTH - total_width) // 2
        
        # Desenha cada card de modo
        for i, mode_name in enumerate(self.modes_list):
            mode = GAME_MODES[mode_name]
            x = start_x + i * (card_width + spacing)
            y = start_y
            
            # Verifica se está selecionado
            is_selected = i == self.selected_mode
            is_unlocked = self.game.game_mode_manager.unlocked_modes.get(mode_name, False)
            
            # Card background com cor sólida
            card = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            card_color = (*PURPLE, 180)  # Cor com transparência
            pygame.draw.rect(card, card_color, card.get_rect(), border_radius=15)
                    
            # Borda do card
            border_color = GOLD if is_selected else PURPLE
            pygame.draw.rect(card, border_color, card.get_rect(), 3, border_radius=15)
            
            # Aplica o card na superfície
            card_rect = card.get_rect(topleft=(x, y))
            surface.blit(card, card_rect)
            
            # Nome do modo
            name_color = GOLD if is_selected else WHITE
            name_surf = self.game.resource_manager.fonts[32].render(mode['name'], True, name_color)
            name_rect = name_surf.get_rect(centerx=x + card_width//2, top=y + 20)
            surface.blit(name_surf, name_rect)
            
            # Descrição curta
            desc_surf = self.game.resource_manager.fonts[24].render(mode['desc'], True, WHITE)
            desc_rect = desc_surf.get_rect(centerx=x + card_width//2, top=y + 70)
            surface.blit(desc_surf, desc_rect)
            
            # Indicador de dificuldade
            diff = "⭐" * mode['difficulty']
            diff_surf = self.game.resource_manager.fonts[24].render(diff, True, GOLD)
            diff_rect = diff_surf.get_rect(centerx=x + card_width//2, top=y + 110)
            surface.blit(diff_surf, diff_rect)
            
            # Descrição longa
            long_desc = self.wrap_text(mode['long_desc'], 28)
            y_offset = 160
            for line in long_desc:
                line_surf = self.game.resource_manager.fonts[20].render(line, True, WHITE)
                line_rect = line_surf.get_rect(centerx=x + card_width//2, top=y + y_offset)
                surface.blit(line_surf, line_rect)
                y_offset += 25
            
            # Efeitos/características
            y_offset = 260
            for effect in mode['effects']:
                effect_surf = self.game.resource_manager.fonts[20].render(f"• {effect}", True, GOLD)
                effect_rect = effect_surf.get_rect(left=x + 20, top=y + y_offset)
                surface.blit(effect_surf, effect_rect)
                y_offset += 30
                
            if is_selected:
                # Tecla para selecionar
                key_surf = self.game.resource_manager.fonts[24].render("ENTER para jogar", True, WHITE)
                key_rect = key_surf.get_rect(centerx=x + card_width//2, bottom=y + card_height - 20)
                surface.blit(key_surf, key_rect)
                
        # Dica na parte inferior
        tip_alpha = int(128 + 127 * math.sin(self.animation_time))
        tip = self.tips[int(self.animation_time / 3) % len(self.tips)]
        tip_surf = self.game.resource_manager.fonts[20].render(tip, True, WHITE)
        tip_surf.set_alpha(tip_alpha)
        tip_rect = tip_surf.get_rect(centerx=WIDTH//2, bottom=HEIGHT - 20)
        surface.blit(tip_surf, tip_rect)
        
        # Teclas de navegação
        nav_text = "← → Navegar entre os modos    ESC Voltar"
        nav_surf = self.game.resource_manager.fonts[20].render(nav_text, True, WHITE)
        nav_rect = nav_surf.get_rect(centerx=WIDTH//2, bottom=HEIGHT - 50)
        surface.blit(nav_surf, nav_rect)
        
        # Instruções com efeito de fade
        alpha = int(128 + 127 * math.sin(self.animation_time))
        instructions = "Use ← → para selecionar e ENTER para jogar"
        inst_surf = self.game.resource_manager.fonts[24].render(instructions, True, WHITE)
        inst_surf.set_alpha(alpha)
        inst_rect = inst_surf.get_rect(center=(WIDTH//2, HEIGHT - 50))
        surface.blit(inst_surf, inst_rect)
        
        # Opção para voltar
        back = "ESC para voltar"
        back_surf = self.game.resource_manager.fonts[20].render(back, True, WHITE)
        back_rect = back_surf.get_rect(topleft=(20, 20))
        surface.blit(back_surf, back_rect)
