"""
Gerenciador de modos de jogo e objetivos diários
"""
import json
import random
import pygame
from datetime import datetime, timedelta
from .constants import (
    MODES_FILE, GAME_MODES, DAILY_OBJECTIVES, OBJECTIVES_FILE,
    DAILY_OBJECTIVES_REWARD, STATE_GAMEOVER
)

class GameModeManager:
    def __init__(self, game):
        self.game = game
        self.current_mode = 'normal'
        self.mode_start_time = 0
        self.items_spawned = 0
        self.items_caught = 0
        self.unlocked_modes = self.load_modes()
        
    def load_modes(self):
        try:
            with open(MODES_FILE, 'r') as f:
                return json.load(f)
        except:
            # Por padrão, todos os modos estão desbloqueados
            modes = {}
            for mode in GAME_MODES.keys():
                modes[mode] = True
            self.save_modes(modes)
            return modes
            
    def save_modes(self, modes):
        with open(MODES_FILE, 'w') as f:
            json.dump(modes, f)
            
    def start_mode(self, mode_name):
        self.current_mode = mode_name
        self.mode_start_time = pygame.time.get_ticks()
        self.items_spawned = 0
        self.items_caught = 0
        
        # Reseta o estado do jogo com as configurações do modo
        self.game.reset_game_state()
        
        mode_data = GAME_MODES[mode_name]
        
        # Aplica modificadores do modo
        if mode_name == 'candy_rain':
            # No modo Chuva de Doces, todos os itens são bons
            self.game.spawn_bad_items = False
            self.game.score_multiplier = mode_data['score_mult']
        elif mode_name == 'speed_rush':
            # No modo Corrida Veloz, tudo é mais rápido
            self.game.speed_multiplier = mode_data['speed_mult']
            self.game.score_multiplier = mode_data['score_mult']
        elif mode_name == 'precision':
            # No modo Precisão, menos itens mas precisa de alta precisão
            self.game.spawn_multiplier = mode_data['spawn_mult']
            self.game.required_accuracy = mode_data['required_accuracy']
            self.game.score_multiplier = mode_data['score_mult']
            
    def update(self):
        mode = GAME_MODES.get(self.current_mode)
        if not mode:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Checa condições de vitória/derrota específicas do modo
        if self.current_mode == 'candy_rain':
            if current_time - self.mode_start_time >= mode['duration']:
                self.complete_mode()
                
        elif self.current_mode == 'precision':
            if self.items_spawned > 0:
                accuracy = self.items_caught / self.items_spawned
                if accuracy < mode['required_accuracy']:
                    self.game.state = STATE_GAMEOVER
                    
    def complete_mode(self):
        # Desbloqueia o próximo modo
        modes = list(GAME_MODES.keys())
        current_index = modes.index(self.current_mode)
        if current_index + 1 < len(modes):
            next_mode = modes[current_index + 1]
            self.unlocked_modes[next_mode] = True
            self.save_modes(self.unlocked_modes)
            
        # Adiciona conquista
        achievement_key = {
            'speed_rush': 'speed_demon',
            'precision': 'accuracy',
            'candy_rain': 'sugar_rush'
        }.get(self.current_mode)
        
        if achievement_key:
            self.game.achievement_manager.add_achievement(achievement_key)
            
class DailyObjectivesManager:
    def __init__(self, game):
        self.game = game
        self.objectives = []
        self.progress = {}
        self.last_update = None
        self.active_objective = None
        self.load_objectives()
        
    def load_objectives(self):
        try:
            with open(OBJECTIVES_FILE, 'r') as f:
                data = json.load(f)
                self.objectives = data['objectives']
                self.progress = data['progress']
                self.last_update = datetime.fromisoformat(data['last_update'])
        except:
            self.generate_new_objectives()
            
    def save_objectives(self):
        data = {
            'objectives': self.objectives,
            'progress': self.progress,
            'last_update': self.last_update.isoformat()
        }
        with open(OBJECTIVES_FILE, 'w') as f:
            json.dump(data, f)
            
    def generate_new_objectives(self):
        self.objectives = []
        available_objectives = list(DAILY_OBJECTIVES.keys())
        chosen = random.sample(available_objectives, 3)
        
        for obj_type in chosen:
            obj_data = DAILY_OBJECTIVES[obj_type]
            target = random.randint(obj_data['max'] // 2, obj_data['max'])
            self.objectives.append({
                'type': obj_type,
                'target': target,
                'completed': False
            })
            
        self.progress = {obj['type']: 0 for obj in self.objectives}
        self.last_update = datetime.now()
        self.save_objectives()
        
    def check_daily_reset(self):
        now = datetime.now()
        if (not self.last_update or 
            now.date() > self.last_update.date()):
            self.generate_new_objectives()
            
    def update_progress(self, objective_type, value):
        if objective_type in self.progress:
            # Encontra o objetivo correspondente
            target = 0
            active_found = False
            for obj in self.objectives:
                if obj['type'] == objective_type:
                    target = obj['target']
                    if not obj['completed'] and not active_found:
                        self.active_objective = obj
                        active_found = True
                    break
                    
            # Se não encontrou nenhum objetivo ativo, limpa o objetivo ativo
            if not active_found:
                self.active_objective = None
            
            # Limita o progresso ao valor máximo do objetivo
            self.progress[objective_type] = min(value, target)
            
            # Verifica se o objetivo foi completado
            for obj in self.objectives:
                if (obj['type'] == objective_type and 
                    not obj['completed'] and 
                    value >= obj['target']):
                    obj['completed'] = True
                    self.game.score_manager.add_score(DAILY_OBJECTIVES_REWARD)
                    # Adiciona efeito visual de conclusão
                    self.game.particle_system.emit_particles('sparkle', 
                        (self.game.screen.get_width()//2, 
                         self.game.screen.get_height()//2))
                    self.game.resource_manager.play_sound('powerup')
                    
            self.save_objectives()
            
            # Verifica conquista de objetivos diários
            completed = sum(1 for obj in self.objectives if obj['completed'])
            if completed >= 3:
                self.game.achievement_manager.add_achievement('daily_master')
                
    def get_formatted_objective(self, objective):
        obj_data = DAILY_OBJECTIVES[objective['type']]
        return obj_data['desc'].format(objective['target'])
        
    def draw(self, screen):
        # Cria superfície semi-transparente
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((147, 112, 219))  # PURPLE
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        # Título
        fonts = self.game.resource_manager.fonts
        title = "✨ Objetivos Diários ✨"
        title_surf = fonts[48].render(title, True, (255, 215, 0))  # GOLD
        title_x = (screen.get_width() - title_surf.get_width()) // 2
        screen.blit(title_surf, (title_x, 50))
        
        # Lista de objetivos
        y = 150
        for i, obj in enumerate(self.objectives):
            # Nome do objetivo
            obj_data = DAILY_OBJECTIVES[obj['type']]
            name_text = obj_data['name']
            name_surf = fonts[32].render(name_text, True, (255, 255, 255))  # WHITE
            screen.blit(name_surf, (screen.get_width()//4, y))
            
            # Descrição e progresso
            progress = self.progress.get(obj['type'], 0)
            desc = self.get_formatted_objective(obj)
            progress_text = f"{progress}/{obj['target']}"
            
            # Cor baseada no status
            if obj['completed']:
                color = (255, 215, 0)  # GOLD
                status = "✓ COMPLETO!"
            else:
                color = (255, 255, 255)  # WHITE
                status = f"{int(progress/obj['target']*100)}%"
            
            desc_surf = fonts[24].render(desc, True, color)
            status_surf = fonts[24].render(status, True, color)
            
            screen.blit(desc_surf, (screen.get_width()//4, y + 40))
            screen.blit(status_surf, (screen.get_width()*3//4, y + 40))
            
            # Barra de progresso
            progress_rect = pygame.Rect(
                screen.get_width()//4,
                y + 70,
                400,
                20
            )
            # Fundo da barra
            pygame.draw.rect(screen, (72, 61, 139), progress_rect)  # DARK_PURPLE
            
            # Progresso atual
            width = int((progress / obj['target']) * progress_rect.width)
            if width > 0:
                fill_rect = progress_rect.copy()
                fill_rect.width = width
                pygame.draw.rect(screen, color, fill_rect)
            
            # Borda da barra
            pygame.draw.rect(screen, (255, 255, 255), progress_rect, 2)
            
            y += 150
            
        # Instrução para voltar
        back = "Pressione ESC para voltar"
        back_surf = fonts[24].render(back, True, (255, 255, 255))
        x = (screen.get_width() - back_surf.get_width()) // 2
        screen.blit(back_surf, (x, screen.get_height() - 50))