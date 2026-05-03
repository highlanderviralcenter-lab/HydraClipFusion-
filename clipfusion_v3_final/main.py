#!/usr/bin/env python3
"""
ClipFusion Viral Pro v3.0 - Entry Point
Sistema unificado: V1 (arquitetura) + V2 (funcional) + SignalCut (7 camadas)
"""

import sys
import os

# Adiciona diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Lazy loading de imports pesados
def main():
    print("🚀 Iniciando ClipFusion Viral Pro v3.0...")
    print("   Carregando interface...")

    from gui.main_gui import ClipFusionApp

    app = ClipFusionApp()
    app.run()

if __name__ == "__main__":
    main()
