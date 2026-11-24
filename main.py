"""Punto de entrada y ciclo principal de Snake AI Challenge."""

import pickle

import pygame

import config as cfg
import renderer
from game import Partida
from menu import BotonStop, Menu, PantallaResultados
from model_loader import cargar_modelo

TECLAS = {
    pygame.K_UP: 0,
    pygame.K_RIGHT: 1,
    pygame.K_DOWN: 2,
    pygame.K_LEFT: 3,
}

MENU = 'menu'
PARTIDA = 'partida'
RESULTADOS = 'resultados'


def main():
    pygame.init()
    pygame.display.set_caption(cfg.TITULO)
    superficie = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
    reloj = pygame.time.Clock()

    try:
        datos_modelo = cargar_modelo()
    except (OSError, ValueError, pickle.UnpicklingError) as error:
        print('No se pudo cargar el modelo:', error)
        pygame.quit()
        return

    config_modelo = datos_modelo['config']
    tabla_q = datos_modelo['tabla_q']

    estado = MENU
    menu = Menu()
    boton_stop = BotonStop()
    partida = None
    resultados = None
    corriendo = True

    while corriendo:
        dt = reloj.tick(cfg.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False
            elif estado == MENU:
                if menu.procesar_evento(event) == 'jugar':
                    partida = Partida(config_modelo, tabla_q)
                    estado = PARTIDA
            elif estado == PARTIDA:
                if boton_stop.procesar_evento(event) == 'stop':
                    partida.detener()
                if event.type == pygame.KEYDOWN and event.key in TECLAS:
                    partida.procesar_tecla(TECLAS[event.key])
            elif estado == RESULTADOS:
                if resultados.procesar_evento(event) == 'menu':
                    estado = MENU

        if estado == PARTIDA:
            partida.actualizar(dt)
            if partida.ambos_terminados:
                resultados = PantallaResultados(partida.resultado())
                estado = RESULTADOS

        if estado == MENU:
            renderer.dibujar_menu(superficie, menu)
        elif estado == PARTIDA:
            renderer.dibujar_partida(superficie, partida, boton_stop)
        else:
            renderer.dibujar_resultados(superficie, resultados)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
