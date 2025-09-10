"""
Classes dos sprites do jogo
"""
import pygame
import random
import math
from .constants import *
from .effects import ParticleSystem

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        # Verifica se o personagem alternativo está desbloqueado
        char_data = self.game.resource_manager.unlockable_characters.get('player2')
        if char_data and self.game.score_manager.highest_score >= char_data['score']:
            char_data['unlocked'] = True
            
        # Usa o personagem selecionado
        self.image = game.resource_manager.images[game.resource_manager.selected_character]
            
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        
        self.lives = START_LIVES
        self.active_powerups = []
        self.invulnerable = False
        
        # Animações
        self.angle = 0
        self.scale = 1.0
        self.scale_direction = 1
        self.original_image = self.image
        
    def update(self):
        # Atualiza power-ups
        for powerup in self.active_powerups[:]:
            powerup.update()
            if powerup.is_expired():
                if powerup.type == 'shield':
                    self.invulnerable = False
                self.active_powerups.remove(powerup)
                
        # Animação de "respiração"
        self.scale += 0.001 * self.scale_direction
        if self.scale > 1.05:
            self.scale_direction = -1
        elif self.scale < 0.95:
            self.scale_direction = 1
            
        # Atualiza imagem com escala
        scaled_size = (
            int(self.original_image.get_width() * self.scale),
            int(self.original_image.get_height() * self.scale)
        )
        self.image = pygame.transform.smoothscale(self.original_image, scaled_size)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
    def move(self, dx):
        # Movimento com inclinação suave
        self.rect.x += dx * PLAYER_SPEED
        
        # Mantém dentro da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            
        # Animação de inclinação
        target_angle = -15 if dx > 0 else 15 if dx < 0 else 0
        self.angle = self.angle * 0.8 + target_angle * 0.2
        
        # Rotaciona a imagem
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
    def take_damage(self):
        if not self.invulnerable:
            self.lives -= 1
            self.game.particle_system.emit_particles('damage', self.rect.center)
            self.game.resource_manager.play_sound('fail')
            
    def add_powerup(self, powerup):
        # Remove power-up do mesmo tipo se existir
        self.active_powerups = [p for p in self.active_powerups if p.type != powerup.type]
        self.active_powerups.append(powerup)
        
    def has_powerup(self, powerup_type):
        return any(p.type == powerup_type for p in self.active_powerups)
        
    def draw(self, surface):
        # Desenha o jogador
        surface.blit(self.image, self.rect)
        
        # Efeito de escudo se tiver o power-up
        if self.has_powerup('shield'):
            pygame.draw.circle(surface, PURPLE, self.rect.center, 
                             max(self.rect.width, self.rect.height) // 2 + 5, 2)

class Item(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.is_good = random.random() < 0.7
        
        # Escolhe uma imagem aleatória
        images = self.game.resource_manager.images['good' if self.is_good else 'bad']
        self.original_image = random.choice(images)
        self.image = self.original_image
        
        # Posição inicial
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.bottom = 0
        
        # Movimento
        self.speed = (ITEM_SPEED + self.game.level * LEVEL_SPEED_INCREASE * 
                     (1 + random.random() * 0.4))
        self.angle = 0
        self.rotation_speed = random.randint(-3, 3)
        
        # Para movimento suave
        self.float_offset = random.random() * math.pi * 2
        self.float_amplitude = random.randint(1, 3)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        
    def update(self):
        # Movimento de queda
        self.y += self.speed
        
        # Movimento de flutuação
        self.x += math.sin(self.float_offset) * self.float_amplitude
        self.float_offset += 0.05
        
        # Atualiza posição do retângulo
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Rotação
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Mantém o centro na mesma posição
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
        # Remove se saiu da tela
        if self.rect.top > HEIGHT:
            self.kill()
            if self.is_good:
                self.game.player.take_damage()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.type = random.choice(['magnet', 'shield', 'multiplier'])
        self.start_time = pygame.time.get_ticks()
        self.duration = POWERUP_DURATION
        if self.type == 'shield':
            self.duration = SHIELD_DURATION
            
        # Define a cor baseada no tipo
        if self.type == 'magnet':
            self.color = GOLD
        elif self.type == 'shield':
            self.color = PURPLE
        else:  # multiplier
            self.color = PINK
            
        # Configuração visual - usa imagens específicas para cada power-up
        if self.type == 'multiplier':
            self.image = game.resource_manager.images.get('coin', None)
        elif self.type == 'shield':
            self.image = game.resource_manager.images.get('shield', None)
        elif self.type == 'magnet':
            self.image = game.resource_manager.images.get('ima', None)
            
        # Se não conseguir carregar a imagem, cria uma forma básica
        if not self.image:
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (20, 20), 20)
        
        # Configuração da posição
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.bottom = 0
        
        # Movimento
        self.speed = ITEM_SPEED * 0.8  # Power-ups caem mais devagar
        self.angle = 0
        self.rotation_speed = random.randint(-2, 2)
        
        # Para movimento suave
        self.float_offset = random.random() * math.pi * 2
        self.float_amplitude = random.randint(1, 3)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        
        # Configura cor e efeito
        if type == 'magnet':
            self.color = GOLD
        elif type == 'shield':
            self.color = PURPLE
        else:  # multiplier
            self.color = PINK
            
    def update(self):
        # Movimento de queda
        self.y += self.speed
        
        # Movimento de flutuação
        self.x += math.sin(self.float_offset) * self.float_amplitude
        self.float_offset += 0.05
        
        # Atualiza posição do retângulo
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Rotação
        self.angle = (self.angle + self.rotation_speed) % 360
        rotated = pygame.transform.rotate(self.image, self.angle)
        
        # Mantém o centro na mesma posição
        old_center = self.rect.center
        self.rect = rotated.get_rect()
        self.rect.center = old_center
        
        # Remove se saiu da tela
        if self.rect.top > HEIGHT:
            self.kill()
        
    def is_expired(self):
        return pygame.time.get_ticks() - self.start_time > self.duration
        
    def get_progress(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        return max(0, 1 - (elapsed / self.duration))
        
    def apply(self, player):
        player.add_powerup(self)
        if self.type == 'shield':
            player.invulnerable = True
