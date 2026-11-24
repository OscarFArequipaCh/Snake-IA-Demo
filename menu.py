"""Pantallas de menú y de resultados comparativos."""

import pygame

import config as cfg


class Menu:
    def __init__(self):
        self.boton = pygame.Rect(cfg.WINDOW_WIDTH // 2 - 190, 420, 380, 74)

    def procesar_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.boton.collidepoint(event.pos):
                return 'jugar'
        return None


class BotonStop:
    def __init__(self):
        self.boton = pygame.Rect(cfg.BOTON_STOP)

    def procesar_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.boton.collidepoint(event.pos):
                return 'stop'
        return None


class PantallaResultados:
    def __init__(self, datos):
        self.datos = datos
        self.boton = pygame.Rect(cfg.WINDOW_WIDTH // 2 - 210, 700, 420, 66)

    def procesar_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.boton.collidepoint(event.pos):
                return 'menu'
        return None
