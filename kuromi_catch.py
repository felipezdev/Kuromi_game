#!/usr/bin/env python3
"""
Kuromi Catch - Um jogo kawaii de coletar itens!
"""
import os
import sys

# Adiciona o diretório atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game import Game

def main():
    """
    Função principal que inicia o jogo
    """
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
