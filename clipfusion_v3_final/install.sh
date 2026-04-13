#!/bin/bash
# =============================================================================
# ClipFusion Viral Pro v3.0 - Instalação Completa
# Integra: V1 (OpenCV) + V2 (funcional) + SignalCut (7 camadas + kernel tuning)
# Hardware: i5-6200U + Intel HD 520 + 8GB RAM
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ClipFusion Viral Pro v3.0 - Instalação Completa     ║${NC}"
echo -e "${BLUE}║  V1 + V2 + SignalCut Unificados                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verifica root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Execute como root: sudo bash $0${NC}"
    exit 1
fi

# Detecta usuário real
REAL_USER="${SUDO_USER:-$USER}"
if [ "$REAL_USER" = "root" ]; then
    REAL_USER=$(logname 2>/dev/null || echo "highlander")
fi
REAL_HOME=$(eval echo "~$REAL_USER")
CLIPFUSION_DIR="$REAL_HOME/clipfusion_v3"

echo -e "${GREEN}[1/12] Detectando hardware...${NC}"
CPU_MODEL=$(grep "model name" /proc/cpuinfo | head -1 | cut -d':' -f2 | xargs)
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
echo "   CPU: $CPU_MODEL"
echo "   RAM: ${RAM_GB}GB"
echo "   Usuário: $REAL_USER"

echo -e "${GREEN}[2/12] Atualizando sistema...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}[3/12] Instalando dependências do sistema...${NC}"
apt install -y \
    python3-pip python3-venv python3-dev python3-tk \
    ffmpeg git curl wget \
    intel-media-va-driver-non-free i965-va-driver-shaders \
    vainfo intel-gpu-tools lm-sensors \
    thermald linux-cpupower msr-tools \
    btrfs-progs zram-tools \
    htop btop neofetch \
    libopencv-dev \
    xorg i3-wm i3status i3lock lightdm lightdm-gtk-greeter \
    rxvt-unicode rofi feh firefox-esr thunar \
    fonts-noto fonts-noto-color-emoji fonts-firacode \
    openssh-server

echo -e "${GREEN}[4/12] Configurando kernel (i915.enable_guc=3)...${NC}"
if ! grep -q "i915.enable_guc=3" /etc/default/grub; then
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="i915.enable_guc=3 mitigations=off /' /etc/default/grub
    update-grub
    echo -e "${YELLOW}⚠️  Kernel configurado. Reinicialização necessária no final.${NC}"
else
    echo -e "${GREEN}✅ Kernel já configurado${NC}"
fi

echo -e "${GREEN}[5/12] Configurando ZRAM (6GB, zstd, prioridade 100)...${NC}"
cat > /etc/default/zramswap << 'EOF'
ALGO=zstd
SIZE=6144
PRIORITY=100
EOF
systemctl enable zramswap
systemctl restart zramswap || true

echo -e "${GREEN}[6/12] Configurando swapfile (2GB, prioridade 50)...${NC}"
mkdir -p /swap
chattr +C /swap 2>/dev/null || true
if [ ! -f /swap/swapfile ]; then
    dd if=/dev/zero of=/swap/swapfile bs=1M count=2048 status=progress
    chmod 600 /swap/swapfile
    mkswap /swap/swapfile
    swapon -p 50 /swap/swapfile
    echo '/swap/swapfile none swap sw,pri=50 0 0' >> /etc/fstab
else
    echo -e "${YELLOW}⚠️  Swapfile já existe${NC}"
fi

echo -e "${GREEN}[7/12] Aplicando sysctl de performance (SignalCut style)...${NC}"
cat > /etc/sysctl.d/99-clipfusion.conf << 'EOF'
# SignalCut Hybrid - Otimizações de memória
vm.swappiness=150
vm.vfs_cache_pressure=50
vm.dirty_ratio=30
vm.dirty_background_ratio=10
vm.dirty_expire_centisecs=1000
vm.dirty_writeback_centisecs=500
vm.min_free_kbytes=131072
vm.overcommit_memory=2
vm.overcommit_ratio=80

# Rede
net.core.default_qdisc=fq_codel
net.ipv4.tcp_congestion_control=bbr

# Filesystem
fs.inotify.max_user_watches=1048576
fs.file-max=2097152
EOF
sysctl -p /etc/sysctl.d/99-clipfusion.conf

echo -e "${GREEN}[8/12] Configurando thermald e CPU...${NC}"
systemctl enable thermald
systemctl restart thermald
echo 'GOVERNOR="performance"' > /etc/default/cpupower
systemctl enable cpupower
cpupower frequency-set -g performance 2>/dev/null || true

echo -e "${GREEN}[9/12] Criando estrutura do projeto...${NC}"
mkdir -p "$CLIPFUSION_DIR"
cd "$CLIPFUSION_DIR"

# Cria diretórios
mkdir -p {anti_copy_modules,viral_engine,core,gui,utils,config,workspace/projects}
touch {anti_copy_modules,viral_engine,core,gui,utils}/__init__.py

echo -e "${GREEN}[10/12] Configurando ambiente Python...${NC}"
python3 -m venv venv
source venv/bin/activate

# Atualiza pip
pip install --upgrade pip

# Instala dependências (incluindo OpenCV e librosa do V1)
pip install \
    faster-whisper \
    opencv-python \
    numpy \
    pillow \
    pyyaml \
    requests \
    librosa \
    soundfile

echo -e "${GREEN}[11/12] Configurando permissões...${NC}"
chown -R "$REAL_USER":"$REAL_USER" "$CLIPFUSION_DIR"
usermod -aG video,render "$REAL_USER"

echo -e "${GREEN}[12/12] Criando scripts de execução...${NC}"

# run.sh
cat > "$CLIPFUSION_DIR/run.sh" << 'EOF'
#!/bin/bash
# ClipFusion Viral Pro v3.0 - Launcher

cd "$(dirname "$0")"

# Configura VA-API
export LIBVA_DRIVER_NAME=iHD
export LIBVA_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri

# Ativa ambiente
source venv/bin/activate

# Verifica sistema
python3 -c "
import sys
sys.path.insert(0, '.')
from utils.hardware import check_system
check_system()
" 2>/dev/null || echo "⚠️  Verificação de hardware falhou, continuando..."

echo ""
echo "🚀 Iniciando ClipFusion Viral Pro v3.0..."
python3 main.py
EOF
chmod +x "$CLIPFUSION_DIR/run.sh"

# Script de verificação rápida
cat > "$CLIPFUSION_DIR/check.sh" << 'EOF'
#!/bin/bash
# Verificação rápida do sistema

echo "🔍 Verificando ClipFusion v3.0..."
echo ""

# Verifica FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg: $(ffmpeg -version | head -1)"
else
    echo "❌ FFmpeg não encontrado"
fi

# Verifica VA-API
if vainfo 2>/dev/null | grep -q "VA-API"; then
    echo "✅ VA-API: Funcionando"
else
    echo "⚠️  VA-API: Problemas detectados"
fi

# Verifica Python
python3 --version

# Verifica memória
echo ""
echo "💾 Memória:"
free -h | grep "Mem:"
echo ""
echo "💾 Swap/ZRAM:"
swapon --show

echo ""
echo "🌡️  Temperatura:"
sensors | grep "Core 0" || echo "sensors não instalado"
EOF
chmod +x "$CLIPFUSION_DIR/check.sh"

# Finalização
echo ""
echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Reinicie o sistema para ativar as otimizações de kernel.${NC}"
echo ""
echo -e "${BLUE}📁 Diretório do projeto:${NC} $CLIPFUSION_DIR"
echo ""
echo -e "${BLUE}▶️  Comandos disponíveis:${NC}"
echo "   cd $CLIPFUSION_DIR"
echo "   ./check.sh    # Verificar sistema"
echo "   ./run.sh      # Iniciar aplicação"
echo ""
echo -e "${BLUE}📝 Próximos passos:${NC}"
echo "   1. sudo reboot"
echo "   2. Copie os arquivos Python para $CLIPFUSION_DIR"
echo "   3. cd $CLIPFUSION_DIR && ./run.sh"
echo ""

read -p "Reiniciar agora? (s/N): " reboot_now
[[ $reboot_now == [sS]* ]] && sudo reboot
