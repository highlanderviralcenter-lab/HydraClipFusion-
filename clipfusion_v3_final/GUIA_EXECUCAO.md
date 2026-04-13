# 🚀 Guia de Execução - ClipFusion v3.0

## Passo a Passo (Do Zero até Rodar)

### 1. Preparação do Sistema

```bash
# Atualize o Debian
sudo apt update && sudo apt upgrade -y

# Instale git (se não tiver)
sudo apt install git -y
```

### 2. Download e Instalação

```bash
# Crie diretório
cd ~
mkdir -p clipfusion_v3
cd clipfusion_v3

# Extraia o arquivo (quando disponível)
# tar -xzf clipfusion_v3_final.tar.gz

# Ou clone do GitHub (quando subir)
# git clone https://github.com/highlanderviralcenter-lab/ClipFusion_v3.git
```

### 3. Executar Instalador

```bash
# Torne executável e rode
chmod +x install.sh
sudo bash install.sh

# Siga as instruções na tela
# Quando perguntar sobre reboot, digite "s"
```

### 4. Após Reboot

```bash
# Verifique se tudo está ok
cd ~/clipfusion_v3
./check.sh

# Deve mostrar:
# ✅ FFmpeg: version 5.x
# ✅ VA-API: Funcionando
# ✅ Python: 3.11.x
# 💾 Memória: 7.7Gi total
# 💾 Swap/ZRAM: 6GB zram + 2GB swapfile
```

### 5. Primeira Execução

```bash
# Inicie a aplicação
./run.sh

# A GUI deve abrir com 7 abas
```

## Fluxo de Uso Rápido

### Aba 1: Projeto
1. Digite nome do projeto
2. Clique "Selecionar Vídeo"
3. Escolha nível de proteção (recomendado: BÁSICO para testes)

### Aba 2: Transcrição
1. Clique "Iniciar Transcrição"
2. Aguarde (1-2 min por minuto de vídeo)
3. Revise o texto gerado

### Aba 3: IA Externa
1. Clique "Gerar Prompt"
2. Copie o prompt (Ctrl+C)
3. Cole no Claude.ai ou ChatGPT
4. Cole a resposta JSON na caixa inferior
5. Clique "Processar"

### Aba 4: Cortes
1. Veja cortes sugeridos (18-35s)
2. Marque os que quer aprovar
3. Clique "Aprovar Selecionados"

### Aba 5: Render
1. Clique "Iniciar Render"
2. Aguarde processamento 2-pass
3. Vídeos salvos em `workspace/projects/`

## Troubleshooting

### Erro: `No module named 'cv2'`
```bash
source venv/bin/activate
pip install opencv-python
```

### Erro: `ffmpeg not found`
```bash
sudo apt install ffmpeg
```

### Erro: `Permission denied` no run.sh
```bash
chmod +x run.sh check.sh
```

### GUI não abre (erro display)
```bash
# Se estiver via SSH, precisa de X11 forwarding
# Ou use VNC/RDP
```

## Comandos Úteis

```bash
# Ver temperatura
sensors | grep "Core 0"

# Ver uso de memória
free -h

# Ver processos
htop

# Verificar VA-API
vainfo | grep "VA-API"
```

## Estrutura Final

```
~/clipfusion_v3/
├── run.sh              # Iniciar app
├── check.sh            # Verificar sistema
├── install.sh          # Instalador (já usado)
├── main.py             # Entry point
├── requirements.txt    # Dependências
├── db.py               # Banco de dados
├── anti_copy_modules/  # 7 camadas proteção
├── viral_engine/       # Motor viral
├── core/               # Engine principal
├── gui/                # Interface
├── utils/              # Utilitários
└── workspace/          # Projetos e saídas
    └── projects/
```

## Suporte

Se encontrar problemas:
1. Verifique `./check.sh`
2. Consulte logs em `~/.clipfusion/`
3. Abra issue no GitHub
