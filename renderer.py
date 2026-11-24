"""Dibujo de tableros, paneles, menú y resultados con Pygame."""

import pygame

import config as cfg
from agent_q import AgentQ

MOTIVOS = {
    'pared': 'Colisión con la pared',
    'cuerpo': 'Colisión con el cuerpo',
    'limite_de_pasos': 'Límite de pasos alcanzado',
    'partida_terminada': 'Partida terminada',
    'detenido_por_usuario': 'Detenido por el jugador',
}

GANADORES = {
    'agente': 'VICTORIA DEL AGENTE',
    'jugador': 'VICTORIA DEL JUGADOR',
    'empate': 'EMPATE',
}


def fuente(tamano, negrita=False):
    try:
        return pygame.font.SysFont('Segoe UI', tamano, bold=negrita)
    except Exception:
        return pygame.font.Font(None, tamano)


def texto(surface, cadena, centro, tamano=20, color=None, negrita=False):
    color = color if color is not None else cfg.COLOR_TEXTO
    imagen = fuente(tamano, negrita).render(cadena, True, color)
    rect = imagen.get_rect(center=centro)
    surface.blit(imagen, rect)
    return rect


def texto_izquierda(surface, cadena, pos, tamano=18, color=None, negrita=False):
    color = color if color is not None else cfg.COLOR_TEXTO
    imagen = fuente(tamano, negrita).render(cadena, True, color)
    rect = imagen.get_rect(topleft=pos)
    surface.blit(imagen, rect)
    return rect


def texto_derecha(surface, cadena, pos, tamano=18, color=None, negrita=False):
    color = color if color is not None else cfg.COLOR_TEXTO
    imagen = fuente(tamano, negrita).render(cadena, True, color)
    rect = imagen.get_rect(topright=pos)
    surface.blit(imagen, rect)
    return rect


def panel(surface, rect, relleno=None, borde=None, radio=14, grosor=2):
    relleno = relleno if relleno is not None else cfg.COLOR_PANEL
    borde = borde if borde is not None else cfg.COLOR_BORDE
    pygame.draw.rect(surface, relleno, rect, border_radius=radio)
    pygame.draw.rect(surface, borde, rect, width=grosor, border_radius=radio)


def _brillo(surface, centro, radio, color, alpha=80):
    capa = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
    pygame.draw.circle(capa, (*color, alpha), (radio, radio), radio)
    surface.blit(capa, (centro[0] - radio, centro[1] - radio))


def _boton(surface, rect, etiqueta, color):
    sobre = rect.collidepoint(pygame.mouse.get_pos())
    relleno = color if sobre else cfg.COLOR_PANEL
    texto_color = cfg.COLOR_FONDO if sobre else color
    if sobre:
        _brillo(surface, rect.center, rect.height, color, 45)
    panel(surface, rect, relleno=relleno, borde=color, radio=12, grosor=3)
    texto(surface, etiqueta, rect.center, 24, texto_color, True)


def dibujar_tablero(surface, env, x, y, color_cabeza, color_cuerpo, titulo,
                    terminado, motivo):
    panel(surface, pygame.Rect(x - 10, y - 10, cfg.BOARD_SIZE + 20, cfg.BOARD_SIZE + 20))
    area = pygame.Rect(x, y, cfg.BOARD_SIZE, cfg.BOARD_SIZE)
    surface.fill(cfg.COLOR_FONDO, area)

    celda = cfg.CELL_SIZE
    for i in range(env.grid_size + 1):
        pygame.draw.line(surface, cfg.COLOR_REJILLA,
                         (x + i * celda, y), (x + i * celda, y + cfg.BOARD_SIZE))
        pygame.draw.line(surface, cfg.COLOR_REJILLA,
                         (x, y + i * celda), (x + cfg.BOARD_SIZE, y + i * celda))

    if env.food is not None:
        centro = (x + env.food[1] * celda + celda // 2,
                  y + env.food[0] * celda + celda // 2)
        _brillo(surface, centro, celda, cfg.COLOR_COMIDA, 75)
        pygame.draw.circle(surface, cfg.COLOR_COMIDA, centro, celda // 2 - 4)

    for indice, (fila, columna) in enumerate(env.snake):
        rect = pygame.Rect(x + columna * celda + 3, y + fila * celda + 3,
                           celda - 6, celda - 6)
        if indice == 0:
            _brillo(surface, rect.center, celda, color_cabeza, 80)
            pygame.draw.rect(surface, color_cabeza, rect, border_radius=8)
            pygame.draw.rect(surface, cfg.COLOR_TEXTO, rect, width=1, border_radius=8)
        else:
            pygame.draw.rect(surface, color_cuerpo, rect, border_radius=7)

    if terminado:
        capa = pygame.Surface((cfg.BOARD_SIZE, cfg.BOARD_SIZE), pygame.SRCALPHA)
        capa.fill((9, 12, 22, 175))
        surface.blit(capa, (x, y))
        centro = (x + cfg.BOARD_SIZE // 2, y + cfg.BOARD_SIZE // 2)
        texto(surface, 'PARTIDA TERMINADA', (centro[0], centro[1] - 18),
              24, cfg.COLOR_ALERTA, True)
        texto(surface, MOTIVOS.get(motivo, motivo), (centro[0], centro[1] + 18),
              18, cfg.COLOR_TEXTO_SUAVE)

    texto(surface, titulo, (x + cfg.BOARD_SIZE // 2, y - 34),
          22, color_cabeza, True)


def dibujar_estadisticas(surface, rect, titulo, color, score, longitud, movimientos):
    x, y, ancho, _alto = rect
    panel(surface, pygame.Rect(rect))
    texto_izquierda(surface, titulo, (x + 20, y + 14), 18, color, True)

    datos = [('PUNTUACIÓN', str(score)),
             ('LONGITUD', str(longitud)),
             ('MOVIMIENTOS', str(movimientos))]
    ancho_columna = ancho // 3
    for i, (etiqueta, valor) in enumerate(datos):
        centro_x = x + ancho_columna * i + ancho_columna // 2
        texto(surface, etiqueta, (centro_x, y + 70), 14, cfg.COLOR_TEXTO_SUAVE)
        texto(surface, valor, (centro_x, y + 120), 38, cfg.COLOR_TEXTO, True)


def dibujar_panel_q(surface, rect, partida):
    x, y, ancho, alto = rect
    panel(surface, pygame.Rect(rect))
    centro = x + ancho // 2

    texto(surface, 'TABLA Q / GREEDY ε=0', (centro, y + 26),
          18, cfg.COLOR_ACENTO, True)

    if partida.estado_conocido:
        texto(surface, 'ESTADO CONOCIDO', (centro, y + 56),
              14, cfg.COLOR_AGENTE, True)
    else:
        texto(surface, 'ESTADO DESCONOCIDO → ACCIÓN 0', (centro, y + 56),
              13, cfg.COLOR_ALERTA, True)

    clave = partida.ultima_clave
    if clave is not None:
        texto(surface, '[' + ', '.join(str(v) for v in clave[:6]) + ']',
              (centro, y + 88), 13, cfg.COLOR_TEXTO_SUAVE)
        texto(surface, '[' + ', '.join(str(v) for v in clave[6:]) + ']',
              (centro, y + 108), 13, cfg.COLOR_TEXTO_SUAVE)
    else:
        texto(surface, 'Esperando el primer movimiento…',
              (centro, y + 98), 13, cfg.COLOR_TEXTO_SUAVE)

    texto(surface, 'Acción: ' + AgentQ.ACCIONES[partida.ultima_accion_agente],
          (centro, y + 142), 18, cfg.COLOR_TEXTO, True)
    texto_izquierda(surface, 'Valores Q', (x + 20, y + 178),
                    15, cfg.COLOR_TEXTO_SUAVE)

    valores = partida.ultimos_valores_q
    escala = max([1.0] + [abs(float(valor)) for valor in valores])
    barra_x = x + 20
    barra_ancho = ancho - 40

    for i, nombre in enumerate(['Recto', 'Derecha', 'Izquierda']):
        fila_y = y + 210 + i * 66
        seleccionada = partida.ultima_accion_agente == i and partida.estado_conocido
        color = cfg.COLOR_ACENTO if seleccionada else cfg.COLOR_BORDE
        texto_izquierda(surface, nombre, (barra_x, fila_y), 15, color, seleccionada)
        texto_derecha(surface, '{:+.2f}'.format(valores[i]),
                      (barra_x + barra_ancho, fila_y), 14, color, True)
        pygame.draw.rect(surface, cfg.COLOR_REJILLA,
                         (barra_x, fila_y + 24, barra_ancho, 14), border_radius=7)
        ancho_barra = int(barra_ancho * max(0.0, float(valores[i])) / escala)
        if ancho_barra > 0:
            pygame.draw.rect(surface, color,
                             (barra_x, fila_y + 24, ancho_barra, 14), border_radius=7)

    if not partida.estado_conocido:
        texto(surface, 'Sin entrada en la tabla → Q = (0, 0, 0)',
              (centro, y + alto - 28), 13, cfg.COLOR_ALERTA)


def dibujar_partida(surface, partida, boton_stop):
    surface.fill(cfg.COLOR_FONDO)
    texto(surface, cfg.TITULO, (cfg.WINDOW_WIDTH // 2, 38),
          34, cfg.COLOR_TEXTO, True)
    texto(surface, 'HUMANO vs AGENTE Q-LEARNING', (cfg.WINDOW_WIDTH // 2, 76),
          16, cfg.COLOR_TEXTO_SUAVE)
    _boton(surface, boton_stop.boton, 'STOP', cfg.COLOR_ALERTA)

    dibujar_tablero(surface, partida.env_agente, cfg.BOARD_LEFT_X, cfg.BOARD_TOP,
                    cfg.COLOR_AGENTE, cfg.COLOR_AGENTE_CUERPO, 'AGENTE IA',
                    partida.terminado_agente, partida.motivo_agente)
    dibujar_tablero(surface, partida.env_humano, cfg.BOARD_RIGHT_X, cfg.BOARD_TOP,
                    cfg.COLOR_HUMANO, cfg.COLOR_HUMANO_CUERPO, 'JUGADOR',
                    partida.terminado_humano, partida.motivo_humano)

    dibujar_panel_q(surface, cfg.PANEL_Q, partida)

    dibujar_estadisticas(surface, cfg.PANEL_STATS_IZQ, 'AGENTE IA',
                         cfg.COLOR_AGENTE, partida.env_agente.get_score(),
                         len(partida.env_agente.snake), partida.env_agente.steps)
    dibujar_estadisticas(surface, cfg.PANEL_STATS_DER, 'JUGADOR',
                         cfg.COLOR_HUMANO, partida.env_humano.get_score(),
                         len(partida.env_humano.snake), partida.env_humano.steps)

    texto(surface, 'Flechas = mover tu serpiente   |   STOP = detener la partida',
          (cfg.WINDOW_WIDTH // 2, cfg.WINDOW_HEIGHT - 20),
          15, cfg.COLOR_TEXTO_SUAVE)


def dibujar_menu(surface, menu):
    surface.fill(cfg.COLOR_FONDO)
    centro = (cfg.WINDOW_WIDTH // 2, 210)
    _brillo(surface, centro, 190, cfg.COLOR_ACENTO, 25)

    texto(surface, cfg.TITULO, (centro[0], 200), 58, cfg.COLOR_AGENTE, True)
    texto(surface, 'Q-LEARNING vs JUGADOR HUMANO', (centro[0], 270),
          20, cfg.COLOR_HUMANO, True)

    _boton(surface, menu.boton, 'JUGAR VS AGENTE', cfg.COLOR_AGENTE)

    texto(surface,
          'Enfréntate al agente de inteligencia artificial entrenado mediante Q-Learning.',
          (centro[0], 545), 18, cfg.COLOR_TEXTO_SUAVE)
    texto(surface, 'Tablero 15 × 15', (centro[0], 600), 18, cfg.COLOR_TEXTO)
    texto(surface, 'Usa las flechas del teclado durante la partida',
          (centro[0], 650), 15, cfg.COLOR_TEXTO_SUAVE)


def dibujar_resultados(surface, pantalla):
    datos = pantalla.datos
    surface.fill(cfg.COLOR_FONDO)

    texto(surface, 'RESULTADOS', (cfg.WINDOW_WIDTH // 2, 70),
          46, cfg.COLOR_TEXTO, True)
    color_ganador = {
        'agente': cfg.COLOR_AGENTE,
        'jugador': cfg.COLOR_HUMANO,
        'empate': cfg.COLOR_TEXTO_SUAVE,
    }[datos['ganador']]
    texto(surface, GANADORES[datos['ganador']], (cfg.WINDOW_WIDTH // 2, 125),
          26, color_ganador, True)

    panel(surface, pygame.Rect(180, 165, 1040, 480))
    texto_izquierda(surface, 'MÉTRICA', (240, 205), 16, cfg.COLOR_TEXTO_SUAVE, True)
    texto(surface, 'AGENTE', (700, 213), 18, cfg.COLOR_AGENTE, True)
    texto(surface, 'JUGADOR', (1060, 213), 18, cfg.COLOR_HUMANO, True)

    filas = [
        ('Puntuación final', datos['score_agente'], datos['score_jugador']),
        ('Comida consumida', datos['comida_agente'], datos['comida_jugador']),
        ('Longitud final', datos['longitud_agente'], datos['longitud_jugador']),
        ('Movimientos', datos['movimientos_agente'], datos['movimientos_jugador']),
    ]
    for i, (etiqueta, valor_agente, valor_jugador) in enumerate(filas):
        fila_y = 270 + i * 72
        if i % 2 == 0:
            pygame.draw.rect(surface, cfg.COLOR_REJILLA,
                             (220, fila_y - 18, 960, 56), border_radius=8)
        texto_izquierda(surface, etiqueta, (240, fila_y), 18, cfg.COLOR_TEXTO)
        texto(surface, str(valor_agente), (700, fila_y + 9),
              24, cfg.COLOR_AGENTE, True)
        texto(surface, str(valor_jugador), (1060, fila_y + 9),
              24, cfg.COLOR_HUMANO, True)

    texto(surface, 'Fin del agente: ' + MOTIVOS.get(datos['motivo_agente'], datos['motivo_agente']),
          (cfg.WINDOW_WIDTH // 2, 580), 14, cfg.COLOR_TEXTO_SUAVE)
    texto(surface, 'Fin del jugador: ' + MOTIVOS.get(datos['motivo_jugador'], datos['motivo_jugador']),
          (cfg.WINDOW_WIDTH // 2, 608), 14, cfg.COLOR_TEXTO_SUAVE)

    _boton(surface, pantalla.boton, 'VOLVER AL MENÚ PRINCIPAL', cfg.COLOR_ACENTO)
