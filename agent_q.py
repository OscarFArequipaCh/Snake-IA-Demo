"""Agente Q-Learning tabular extraído del notebook, en modo solo consulta."""

import numpy as np

from snake_env import DIRECTIONS


class AgentQ:
    """Reutiliza la percepción del notebook; la política aquí nunca aprende."""

    NOMBRES_ESTADO = ['distancia_frontal', 'distancia_derecha', 'distancia_izquierda',
                      'dir_arriba', 'dir_abajo', 'dir_izquierda', 'dir_derecha',
                      'comida_izquierda', 'comida_derecha', 'comida_arriba', 'comida_abajo',
                      'longitud_categoria']

    ACCIONES = {0: 'recto', 1: 'girar derecha', 2: 'girar izquierda'}

    def __init__(self, config, q_table=None):
        self.config = config
        self.q_table = q_table if q_table is not None else {}

    def inicializar_tabla_q(self):
        return {}

    def categoria_distancia(self, celdas_libres):
        if celdas_libres >= self.config['umbrales_distancia'][1]:
            return 4
        if celdas_libres >= self.config['umbrales_distancia'][0]:
            return 3
        return int(celdas_libres)

    def distancia_obstaculo(self, env, indice_direccion):
        dr, dc = DIRECTIONS[indice_direccion]
        fila, columna = env.snake[0]
        cuerpo = {tuple(segmento) for segmento in env.snake}
        celdas_libres = 0
        while True:
            fila += dr
            columna += dc
            if not (0 <= fila < env.grid_size and 0 <= columna < env.grid_size):
                break
            if (fila, columna) in cuerpo:
                break
            celdas_libres += 1
        return self.categoria_distancia(celdas_libres)

    def categoria_longitud(self, longitud):
        return sum(1 for umbral in self.config['umbrales_longitud'] if longitud >= umbral)

    def get_state(self, env):
        head = env.snake[0]
        indices = [env.direction, (env.direction + 1) % 4, (env.direction - 1) % 4]
        distancias = [self.distancia_obstaculo(env, indice) for indice in indices]

        direccion_one_hot = [1.0 if env.direction == i else 0.0 for i in [0, 2, 3, 1]]

        if env.food is None:
            comida = [0.0, 0.0, 0.0, 0.0]
        else:
            comida = [1.0 if env.food[1] < head[1] else 0.0,
                      1.0 if env.food[1] > head[1] else 0.0,
                      1.0 if env.food[0] < head[0] else 0.0,
                      1.0 if env.food[0] > head[0] else 0.0]

        longitud = self.categoria_longitud(len(env.snake))
        vector = distancias + direccion_one_hot + comida + [float(longitud)]
        return np.array(vector, dtype=np.float32)

    def estado_como_clave(self, vector_estado):
        return tuple(int(valor) for valor in vector_estado)

    def describir_accion(self, accion):
        return self.ACCIONES[accion]

    def valores_q_lectura(self, clave_estado):
        """Devuelve una copia de los 3 valores Q y si la clave existe, sin insertar nada."""
        valores = self.q_table.get(clave_estado)
        if valores is None:
            return np.zeros(3, dtype=float), False
        return np.array(valores, dtype=float, copy=True), True

    def decidir_greedy(self, clave_estado):
        """Igual que la evaluación del notebook: argmax o acción 0 si no existe la clave."""
        valores, existe = self.valores_q_lectura(clave_estado)
        accion = int(np.argmax(valores)) if existe else 0
        return accion, valores, existe
