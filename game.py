"""Coordinación de las dos partidas simultáneas: agente IA y jugador humano."""

import numpy as np

import config as cfg
from agent_q import AgentQ
from snake_env import SnakeEnv


class Partida:
    """Mantiene dos entornos independientes y un único agente de solo consulta."""

    def __init__(self, config_modelo, tabla_q):
        self.config = config_modelo
        self.max_pasos = config_modelo['max_steps_per_episode']

        self.agente = AgentQ(config_modelo, tabla_q)
        self.env_agente = SnakeEnv(config_modelo)
        self.env_humano = SnakeEnv(config_modelo)

        # Ambas partidas empiezan con la misma comida; después evolucionan por separado.
        self.env_humano.food = list(self.env_agente.food)

        self.direccion_humana = self.env_humano.direction
        self.terminado_agente = False
        self.terminado_humano = False
        self.motivo_agente = ''
        self.motivo_humano = ''

        self.ultima_accion_agente = 0
        self.ultimos_valores_q = np.zeros(3)
        self.estado_conocido = False
        self.ultima_clave = None

        self._tiempo_acumulado = 0

    def procesar_tecla(self, direccion_absoluta):
        """Guarda la dirección deseada, ignorando el giro directo de 180°."""
        if self.terminado_humano:
            return
        actual = self.env_humano.direction
        if direccion_absoluta == (actual + 2) % 4:
            return
        self.direccion_humana = direccion_absoluta

    def _accion_humana(self):
        """Traduce la dirección absoluta a la acción relativa que entiende el entorno."""
        actual = self.env_humano.direction
        deseada = self.direccion_humana
        if deseada == actual:
            return 0
        if deseada == (actual + 1) % 4:
            return 1
        if deseada == (actual - 1) % 4:
            return 2
        return 0

    def _paso_agente(self):
        estado = self.agente.get_state(self.env_agente)
        clave = self.agente.estado_como_clave(estado)
        accion, valores, existe = self.agente.decidir_greedy(clave)

        self.ultima_clave = clave
        self.ultimos_valores_q = valores
        self.estado_conocido = existe
        self.ultima_accion_agente = accion

        _recompensa, done, info = self.env_agente.step(accion)
        self._finalizar_si_corresponde('agente', done, info, self.env_agente)

    def _paso_humano(self):
        accion = self._accion_humana()
        _recompensa, done, info = self.env_humano.step(accion)
        self._finalizar_si_corresponde('humano', done, info, self.env_humano)

    def _finalizar_si_corresponde(self, quien, done, info, env):
        if done:
            motivo = info.get('motivo', 'colision')
        elif env.steps >= self.max_pasos:
            motivo = 'limite_de_pasos'
        else:
            return

        if quien == 'agente':
            self.terminado_agente = True
            self.motivo_agente = motivo
        else:
            self.terminado_humano = True
            self.motivo_humano = motivo

    def actualizar(self, dt_ms):
        """Un tick mueve ambas serpientes exactamente una celda."""
        self._tiempo_acumulado += dt_ms
        if self._tiempo_acumulado < cfg.TICK_MS:
            return
        self._tiempo_acumulado -= cfg.TICK_MS

        if not self.terminado_agente:
            self._paso_agente()
        if not self.terminado_humano:
            self._paso_humano()

    def detener(self):
        """Cierra la partida de inmediato sin borrar el motivo de quien ya terminó."""
        if not self.terminado_agente:
            self.terminado_agente = True
            self.motivo_agente = 'detenido_por_usuario'
        if not self.terminado_humano:
            self.terminado_humano = True
            self.motivo_humano = 'detenido_por_usuario'

    @property
    def ambos_terminados(self):
        return self.terminado_agente and self.terminado_humano

    def resultado(self):
        score_agente = self.env_agente.get_score()
        score_jugador = self.env_humano.get_score()

        if score_agente > score_jugador:
            ganador = 'agente'
        elif score_jugador > score_agente:
            ganador = 'jugador'
        else:
            ganador = 'empate'

        return {
            'ganador': ganador,
            'score_agente': score_agente,
            'score_jugador': score_jugador,
            'comida_agente': score_agente,
            'comida_jugador': score_jugador,
            'longitud_agente': len(self.env_agente.snake),
            'longitud_jugador': len(self.env_humano.snake),
            'movimientos_agente': self.env_agente.steps,
            'movimientos_jugador': self.env_humano.steps,
            'motivo_agente': self.motivo_agente,
            'motivo_jugador': self.motivo_humano,
        }
