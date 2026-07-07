#!/usr/bin/env bash
# ===========================================================================
# Foton System — Configurador de prefixo do tmux
# Versão: 1.0
#
# Configura o tmux para usar Ctrl+B como prefixo, liberando Ctrl+W para
# o Foton System (ou Neovim do usuário).
#
# Uso: bash scripts/foton_tmux_setup.sh
# Idempotente: execuções múltiplas não duplicam configurações.
# ===========================================================================

set -euo pipefail

TMUX_CONF="${HOME}/.tmux.conf"
MARKER="# === Foton System: prefixo ajustado para evitar conflito ==="
BACKUP_SUFFIX=".foton_backup_$(date +%Y%m%d_%H%M%S)"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Foton System — Configurador de Prefixo do tmux${NC}"
echo ""

# --- Backup ---
if [ -f "$TMUX_CONF" ]; then
    cp "$TMUX_CONF" "${TMUX_CONF}${BACKUP_SUFFIX}"
    echo -e "${GREEN}[v] Backup criado:${NC} ${TMUX_CONF}${BACKUP_SUFFIX}"
else
    echo -e "${YELLOW}[!] ${TMUX_CONF} nao existe — sera criado.${NC}"
fi

# --- Verificar/Injetar marcador ---
if grep -qF "$MARKER" "$TMUX_CONF" 2>/dev/null; then
    echo -e "${GREEN}[v] Configuracao ja presente em ${TMUX_CONF}. Nada a fazer.${NC}"
    echo ""
    echo -e "Para aplicar: ${CYAN}tmux source-file ${TMUX_CONF}${NC}"
    echo "  ou reinicie o tmux."
    exit 0
fi

# --- Injetar ---
cat >> "$TMUX_CONF" <<EOF

${MARKER}
set -g prefix C-b
unbind C-w
bind C-b send-prefix
# ==============================================================
EOF

echo -e "${GREEN}[v] Configuracao injetada em ${TMUX_CONF}${NC}"
echo ""
echo -e "Linhas adicionadas:"
echo -e "  ${CYAN}set -g prefix C-b${NC}"
echo -e "  ${CYAN}unbind C-w${NC}"
echo -e "  ${CYAN}bind C-b send-prefix${NC}"
echo ""
echo -e "Para aplicar: ${CYAN}tmux source-file ${TMUX_CONF}${NC}"
echo "  ou reinicie o tmux."
echo ""
echo -e "${YELLOW}Agora o Foton System usara Ctrl+B como prefixo de splits${NC}"
echo -e "${YELLOW}dentro do tmux, sem conflito.${NC}"
