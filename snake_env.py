"""Entorno Snake compatible con el notebook de entrenamiento."""

import random

CONFIG = {
    'grid_size': 15,
    'reward_food': 10.0,
    'reward_collision': -10.0,
    'reward_step': -0.01,
}

DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
DIRECTION_NAMES = ['arriba', 'derecha', 'abajo', 'izquierda']


class SnakeEnv:
    """Lógica del juego, sin ninguna dependencia de Pygame."""

    def __init__(self, config=None, grid_size=None):
        self.config = config if config is not None else CONFIG
        self.grid_size = grid_size if grid_size is not None else self.config['grid_size']
        self.reset()

    def reset(self):
        center = self.grid_size // 2
        self.snake = [[center, center], [center, center - 1], [center, center - 2]]
        self.direction = 1
        self.score = 0
        self.steps = 0
        self.done = False
        self.food = None
        self._spawn_food()

    def _spawn_food(self):
        free_cells = [[r, c] for r in range(self.grid_size)
                      for c in range(self.grid_size)
                      if [r, c] not in self.snake]
        if not free_cells:
            self.food = None
            self.done = True
            return
        self.food = random.choice(free_cells)

    def step(self, action):
        if self.done:
            return 0.0, True, {'motivo': 'partida_terminada', 'food_eaten': False}

        if action == 1:
            self.direction = (self.direction + 1) % 4
        elif action == 2:
            self.direction = (self.direction - 1) % 4
        elif action != 0:
            raise ValueError('La accion debe ser 0, 1 o 2')

        head = self.snake[0]
        dr, dc = DIRECTIONS[self.direction]
        new_head = [head[0] + dr, head[1] + dc]
        ate_food = self.food is not None and new_head == self.food

        if not (0 <= new_head[0] < self.grid_size and 0 <= new_head[1] < self.grid_size):
            self.done = True
            return self.config['reward_collision'], self.done, {'motivo': 'pared', 'food_eaten': False}

        body_to_check = self.snake if ate_food else self.snake[:-1]
        if new_head in body_to_check:
            self.done = True
            return self.config['reward_collision'], self.done, {'motivo': 'cuerpo', 'food_eaten': False}

        self.snake.insert(0, new_head)
        self.steps += 1

        if ate_food:
            self.score += 1
            reward = self.config['reward_food']
            self._spawn_food()
        else:
            self.snake.pop()
            reward = self.config['reward_step']

        motivo = 'comida' if ate_food else 'movimiento'
        return reward, self.done, {'motivo': motivo, 'food_eaten': ate_food}

    def get_score(self):
        """Devuelve la puntuación de la partida actual."""
        return self.score
