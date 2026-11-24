"""Verificacion automatica final del proyecto, incluido el boton STOP."""

import contextlib
import hashlib
import io
import json
import os
import random
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import numpy as np
import pygame

import config as cfg
import renderer
from agent_q import AgentQ
from game import Partida
from menu import BotonStop, Menu, PantallaResultados
from model_loader import cargar_modelo
from snake_env import SnakeEnv

RUTA_PKL = 'q_learning_snake_v4.pkl'
RUTA_NOTEBOOK = 'Snake_AI_Q_Learning_VF.ipynb'
CLAVES_PKL = {'version', 'tabla_q', 'config', 'historial', 'epsilon'}

resultados = []


def comprobar(nombre, condicion, detalle=''):
    resultados.append((nombre, bool(condicion), detalle))


def hash_archivo(ruta):
    with open(ruta, 'rb') as archivo:
        return hashlib.sha256(archivo.read()).hexdigest()


def suma_tabla(tabla):
    return sum(float(np.asarray(valores).sum()) for valores in tabla.values())


def escenario(config, snake, direccion, food):
    env = SnakeEnv(config)
    env.snake = snake
    env.direction = direccion
    env.food = food
    return env


def verificar():
    hash_inicial = hash_archivo(RUTA_PKL)
    datos = cargar_modelo(RUTA_PKL)
    config = datos['config']
    tabla = datos['tabla_q']

    comprobar('1. PKL cargado correctamente', isinstance(datos, dict) and len(tabla) > 0,
              '{} estados'.format(len(tabla)))
    comprobar('2. Version y estructura validas',
              datos['version'] == 4 and set(datos) >= CLAVES_PKL,
              'version {}'.format(datos['version']))

    agente = AgentQ(config, tabla)
    clave_conocida = next(iter(tabla))
    valores, existe = agente.valores_q_lectura(clave_conocida)
    comprobar('3. Consulta de la tabla Q', existe and valores.shape == (3,),
              str(valores.tolist()))

    with open(RUTA_NOTEBOOK, encoding='utf-8') as archivo:
        notebook = json.load(archivo)
    celdas = [''.join(c['source']) for c in notebook['cells'] if c['cell_type'] == 'code']
    espacio = {'np': np, 'random': random}
    with contextlib.redirect_stdout(io.StringIO()):
        for indice in (1, 2, 5, 7):
            exec(celdas[indice], espacio)
    agente_notebook = espacio['AgentQ'](config)

    escenarios = [
        SnakeEnv(config),
        escenario(config, [[0, 5], [1, 5], [2, 5]], 0, [10, 10]),
        escenario(config, [[10, 13], [10, 12], [10, 11]], 1, [10, 1]),
        escenario(config, [[10, 5], [10, 4], [10, 3], [10, 2], [10, 1], [10, 0]], 1, [11, 1]),
    ]
    estados_iguales = all(
        np.array_equal(agente.get_state(env), agente_notebook.get_state(env))
        for env in escenarios
    )
    comprobar('4. Representacion de estado identica al notebook',
              estados_iguales and len(agente.NOMBRES_ESTADO) == 12,
              '12 caracteristicas, {} escenarios'.format(len(escenarios)))

    claves_conocidas = list(tabla)[:5]
    greedy_igual = all(
        agente.decidir_greedy(clave)[0] == int(np.argmax(tabla[clave]))
        for clave in claves_conocidas
    )
    comprobar('5. Seleccion greedy igual a la evaluacion',
              greedy_igual and agente.decidir_greedy((9,) * 12)[0] == 0,
              '{} claves y fallback 0'.format(len(claves_conocidas)))

    cantidad_antes = len(tabla)
    suma_antes = suma_tabla(tabla)
    for _ in range(50):
        agente.decidir_greedy((9,) * 12)
        agente.valores_q_lectura((8,) * 12)
    comprobar('6. Estados desconocidos no modifican la tabla',
              len(tabla) == cantidad_antes and suma_tabla(tabla) == suma_antes,
              '{} estados'.format(len(tabla)))

    random.seed(42)
    partida = Partida(config, tabla)
    for _ in range(400):
        partida.actualizar(cfg.TICK_MS)
    comprobar('7. Agente juega sin reentrenar',
              partida.env_agente.steps > 0
              and partida.env_agente.get_score() > 0
              and len(tabla) == cantidad_antes,
              '{} movimientos, score {}'.format(partida.env_agente.steps,
                                                partida.env_agente.get_score()))

    control = Partida(config, tabla)
    control.procesar_tecla(3)
    reversa_ignorada = control.direccion_humana == 1
    mapeo_correcto = True
    for direccion in range(4):
        control.env_humano.direction = direccion
        control.direccion_humana = direccion
        mapeo_correcto = mapeo_correcto and control._accion_humana() == 0
        control.direccion_humana = (direccion + 1) % 4
        mapeo_correcto = mapeo_correcto and control._accion_humana() == 1
        control.direccion_humana = (direccion - 1) % 4
        mapeo_correcto = mapeo_correcto and control._accion_humana() == 2
    comprobar('8. Control humano y giro anti-reversa',
              reversa_ignorada and mapeo_correcto)

    partida_muerte = Partida(config, tabla)
    partida_muerte.env_humano.snake = [[0, 7], [1, 7], [2, 7]]
    partida_muerte.env_humano.direction = 0
    partida_muerte.direccion_humana = 0
    partida_muerte.actualizar(cfg.TICK_MS)
    muerte_independiente = partida_muerte.terminado_humano and not partida_muerte.terminado_agente
    pasos_antes = partida_muerte.env_agente.steps
    for _ in range(5):
        partida_muerte.actualizar(cfg.TICK_MS)
    sigue_agente = partida_muerte.env_agente.steps > pasos_antes
    comprobar('9. Tableros independientes', muerte_independiente and sigue_agente)
    comprobar('10. Muerte de uno no detiene al otro',
              partida_muerte.terminado_humano and sigue_agente,
              'motivo humano: {}'.format(partida_muerte.motivo_humano))

    config_corto = dict(config)
    config_corto['max_steps_per_episode'] = 2
    partida_corta = Partida(config_corto, tabla)
    for _ in range(10):
        partida_corta.actualizar(cfg.TICK_MS)
    resultado = partida_corta.resultado()
    campos = {'ganador', 'score_agente', 'score_jugador', 'comida_agente',
              'comida_jugador', 'longitud_agente', 'longitud_jugador',
              'movimientos_agente', 'movimientos_jugador'}
    comprobar('11. Resultados cuando ambos terminan',
              partida_corta.ambos_terminados and campos <= set(resultado),
              'ganador: {}'.format(resultado['ganador']))

    menu = Menu()
    pantalla_resultados = PantallaResultados(resultado)
    evento_jugar = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                      pos=menu.boton.center)
    evento_volver = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                       pos=pantalla_resultados.boton.center)
    nueva_partida = Partida(config, tabla)
    comprobar('12. Volver al menu y nueva partida',
              menu.procesar_evento(evento_jugar) == 'jugar'
              and pantalla_resultados.procesar_evento(evento_volver) == 'menu'
              and nueva_partida.env_agente.steps == 0
              and nueva_partida.env_agente.food == nueva_partida.env_humano.food)

    boton_stop = BotonStop()
    evento_stop = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                     pos=boton_stop.boton.center)
    partida_detenida = Partida(config, tabla)
    for _ in range(5):
        partida_detenida.actualizar(cfg.TICK_MS)
    pasos_antes_stop = (partida_detenida.env_agente.steps,
                        partida_detenida.env_humano.steps)
    if boton_stop.procesar_evento(evento_stop) == 'stop':
        partida_detenida.detener()
    for _ in range(5):
        partida_detenida.actualizar(cfg.TICK_MS)
    comprobar('13. Boton STOP detiene ambas serpientes',
              partida_detenida.ambos_terminados
              and partida_detenida.motivo_agente == 'detenido_por_usuario'
              and partida_detenida.motivo_humano == 'detenido_por_usuario'
              and (partida_detenida.env_agente.steps,
                   partida_detenida.env_humano.steps) == pasos_antes_stop,
              'pasos congelados en {}'.format(pasos_antes_stop))

    detalle_grafico = ''
    sin_error_grafico = True
    pygame.init()
    try:
        superficie = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
        renderer.dibujar_menu(superficie, menu)
        renderer.dibujar_partida(superficie, partida_muerte, boton_stop)
        renderer.dibujar_resultados(superficie, pantalla_resultados)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
        pygame.event.get()
        pygame.display.flip()
    except Exception as error:
        sin_error_grafico = False
        detalle_grafico = str(error)
    finally:
        pygame.quit()
    comprobar('14. Graficos y eventos sin errores', sin_error_grafico, detalle_grafico)

    comprobar('PKL original sin modificaciones',
              hash_archivo(RUTA_PKL) == hash_inicial,
              hash_inicial[:16] + '…')

    print('VERIFICACION FINAL')
    for nombre, correcto, detalle in resultados:
        estado = 'OK  ' if correcto else 'FALLO'
        print('[{}] {}{}'.format(estado, nombre,
                                 ' | ' + detalle if detalle else ''))
    aciertos = sum(1 for _nombre, correcto, _detalle in resultados if correcto)
    print('TOTAL: {}/{}'.format(aciertos, len(resultados)))
    return 0 if aciertos == len(resultados) else 1


if __name__ == '__main__':
    sys.exit(verificar())
