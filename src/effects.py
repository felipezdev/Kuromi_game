"""
Sistema de partículas e efeitos visuais
"""
import pygame
import random
import math
import colorsys
from .constants import *

class Particle:
    def __init__(self, x, y, color, size, lifetime, dx=0, dy=0, gravity=True):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.dx = dx
        self.dy = dy
        self.gravity = gravity
        self.alpha = 255

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.gravity:
            self.dy += 0.1
        self.lifetime -= 1
        self.alpha = int((self.lifetime / self.max_lifetime) * 255)
        return self.lifetime > 0

    def draw(self, surface):
        if self.alpha <= 0:
            return
            
        if hasattr(self, 'image'):
            self.image.set_alpha(self.alpha)
            surface.blit(self.image, (int(self.x - self.size), int(self.y - self.size)))
        else:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (self.size, self.size), self.size)
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self, game=None):
        self.particles = []
        self.game = game
        
    def emit_particles(self, type, pos):
        if type == 'sparkle':
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1, 3)
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                particle = self.add_particle(pos[0], pos[1], None, random.uniform(2, 4), 400, dx, dy, False)
                if particle:
                    particle.image = self.game.resource_manager.images['coin']
        
        elif type == 'explosion':
            for _ in range(10):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 5)
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                particle = self.add_particle(pos[0], pos[1], DARK_PINK, random.uniform(3, 6), 600, dx, dy)
                if particle:
                    particle.image = self.game.resource_manager.images['shield']
                
        elif type == 'powerup':
            color = rainbow_color(random.random())
            for _ in range(15):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 4)
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                self.add_particle(pos[0], pos[1], color, random.uniform(2, 5), 800, dx, dy)
                
        elif type == 'levelup':
            for i in range(20):
                angle = (i / 20) * math.pi * 2
                speed = random.uniform(4, 6)
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                self.add_particle(pos[0], pos[1], GOLD, random.uniform(3, 6), 1000, dx, dy)
                
        elif type == 'damage':
            for _ in range(8):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(3, 6)
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                self.add_particle(pos[0], pos[1], DARK_PINK, random.uniform(2, 4), 500, dx, dy)
                
    def add_particle(self, x, y, color=None, size=None, lifetime=None, dx=0, dy=0, gravity=True):
        if len(self.particles) >= MAX_PARTICLES:
            return
            
        if color is None:
            color = random.choice(SPARKLE_COLORS)
        if size is None:
            size = random.uniform(2, 6)
        if lifetime is None:
            lifetime = PARTICLE_LIFETIME
            
        if dx == 0 and dy == 0:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            
        self.particles.append(Particle(x, y, color, size, lifetime, dx, dy, gravity))
        
    def trail(self, x, y, color):
        self.add_particle(x, y, color, random.uniform(2, 4), 300, dy=random.uniform(-0.5, 0.5), gravity=False)
        
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

class PowerUpEffect:
    def __init__(self, type_name):
        self.type = type_name
        self.start_time = pygame.time.get_ticks()
        self.duration = POWERUP_DURATION
        if type_name == 'shield':
            self.duration = SHIELD_DURATION
        self.particles = ParticleSystem()
        self.color = {
            'magnet': YELLOW,
            'shield': PURPLE,
            'multiplier': GOLD
        }.get(type_name, WHITE)
        
    def is_active(self):
        return pygame.time.get_ticks() - self.start_time < self.duration
        
    def get_progress(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        return max(0, 1 - (elapsed / self.duration))
        
    def update(self, x, y):
        self.particles.update()
        
        if self.type == 'magnet':
            if random.random() < 0.3:
                angle = random.uniform(0, math.pi * 2)
                px = x + math.cos(angle) * MAGNET_RANGE
                py = y + math.sin(angle) * MAGNET_RANGE
                self.particles.add_particle(px, py, self.color, 3, 500)
                
        elif self.type == 'shield':
            for _ in range(2):
                angle = random.uniform(0, math.pi * 2)
                radius = 50
                px = x + math.cos(angle) * radius
                py = y + math.sin(angle) * radius
                self.particles.add_particle(px, py, self.color, 4, 400)
                
        elif self.type == 'multiplier':
            if random.random() < 0.2:
                self.particles.add_particle(x + random.uniform(-30, 30),
                                         y + random.uniform(-30, 30),
                                         self.color, 5, 600)
                
    def draw(self, surface, x, y):
        if self.type == 'shield':
            progress = self.get_progress()
            radius = 60
            points = []
            for i in range(32):
                angle = i * (2 * math.pi / 32)
                offset = math.sin(pygame.time.get_ticks() * 0.005 + angle * 2) * 5
                px = x + math.cos(angle) * (radius + offset)
                py = y + math.sin(angle) * (radius + offset)
                points.append((px, py))
                
            if len(points) > 2:
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(s, (*self.color, int(80 * progress)), points)
                surface.blit(s, (0, 0))
                
        self.particles.draw(surface)

def rainbow_color(offset=0):
    """Gera uma cor do arco-íris baseada no tempo"""
    t = (pygame.time.get_ticks() * RAINBOW_SPEED + offset) % 1.0
    rgb = colorsys.hsv_to_rgb(t, 0.8, 1.0)
    return tuple(int(x * 255) for x in rgb)
