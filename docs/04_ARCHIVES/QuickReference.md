---
type: archive
domain: core
status: archived
tags: [quickref, legacy, tui]
archive_note: >
  Arquivado em Jun/2026 (Sprint DualInterface). Reflete TUI legado —
  menus de implantação e backup que não representam a arquitetura
  atual. Ver [[TuiGuide]] (TUI) e [[DocsMcp]] (MCP) para
  documentação vigente.
---
# [ARQUIVADO] ⚡ Cartão de Referência Rápida: Implantação e Backup (QuickReference)

## Para Colar na Parede do Escritório 📌

---

## 🆘 Preciso de Ajuda Rápido!

| Problema | Solução | Tempo |
|----------|---------|-------|
| **Sistema não abre** | Menu → 7 → 1 (Validar) | 10 seg |
| **Erro na base de dados** | Menu → 7 → 3 (Reparar) | 1 min |
| **Disco cheio** | Menu → 7 → 4 (Gerenciar) | 30 seg |
| **Preciso recomeçar** | Menu → 7 → 2 (Criar nova) | 1 min |
| **Perdi dados** | Menu → 7 → 5 (Restaurar) | 2 min |

---

## 📍 Onde Encontro o Menu?

```
Inicie o FotonSystem
        ↓
Tela Principal (Menu)
        ↓
Opção: 7. Implantação ← Clique aqui!
        ↓
Menu de Deployment
```

---

## 🎮 O Menu Tem 5 Opções

```
1️⃣  Validar Base        → Verifica se está tudo OK
2️⃣  Criar Nova Base      → Reseta tudo do zero
3️⃣  Reparar Base         → Conserta se tiver problema
4️⃣  Gerenciar Backups    → Vê espaço, limpa se need
5️⃣  Restaurar de Backup  → Volta para data anterior
```

---

## 💾 Quanto de Espaço Uso?

```
Por Dia:    15-20 MB     ← Bem pouco
Por Mês:    500 MB       ← Confortável
Por Ano:    5-6 GB       ← Nunca enche
Limite:     500 MB       ← Sistema limpa automaticamente
```

---

## 🔄 Automaticamente, o Sistema:

✅ **Cria backup** quando:
- Dados mudaram significativamente (> 10%)
- OU passou mais de 30 minutos

❌ **Não cria backup** quando:
- Dados mudaram pouquinho (< 10%)
- E passou menos de 30 minutos

📊 **Resultado:**
- 100 operações → ~3 backups (não 100!)
- Economia: 97% 🎉

---

## 🗓️ Quanto Tempo Guarda Backup?

| Período | Frequência | Máximo |
|---------|-----------|--------|
| Últimas 24h | 1 por HORA | 24 |
| Últimos 7 dias | 1 por DIA | 7 |
| Últimas 4 semanas | 1 por SEMANA | 4 |
| Últimos 3 meses | 1 por MÊS | 3 |

**Total:** ~40 backups máximo

---

## 🔍 Checklist de Backup

- [ ] Validar base? `Menu → 7 → 1`
- [ ] Ver espaço? `Menu → 7 → 4 → 2`
- [ ] Precisa limpar? `Menu → 7 → 4 → 1`
- [ ] Quer restaurar? `Menu → 7 → 5`

---

## 📁 Onde Ficam os Backups?

```
Windows:  C:\Users\SEU_USUARIO\AppData\Local\FotonSystem\
Mac:      ~/Library/Application Support/FotonSystem/
Linux:    ~/.local/share/FotonSystem/
```

**Arquivos:**
```
baseDados.xlsx                    ← Arquivo principal
BKP-baseDados_20260205_101500.xlsx ← Backup 1
BKP-baseDados_20260205_104500.xlsx ← Backup 2
BKP-baseDados_20260204_160000.xlsx ← Backup 3
... (mais backups antigos)
```

---

## ⚙️ Configurações Avançadas

**Se tiver MUITA atividade (1000+ ops/dia):**
```
Aumentar:
- TIME_THRESHOLD = 60 min (em vez de 30)
- MAX_BACKUP_SIZE = 1000 MB (em vez de 500)
```

**Se tiver POUCA atividade (< 10 ops/dia):**
```
Diminuir:
- TIME_THRESHOLD = 15 min (em vez de 30)
- Aumentar KEEP_MONTHLY_MONTHS = 6 (em vez de 3)
```

**Se disco está CRÍTICO:**
```
TIME_THRESHOLD = 120 min (2 horas)
MAX_BACKUP_SIZE = 50 MB (só essenciais)
```

---

## 🆘 Problemas Comuns

### "Meu banco está corrompido!"
```
Menu → 7 → 3 (Reparar)
Aguarde... ✓ Pronto!
```

### "Posso recuperar do backup?"
```
Menu → 7 → 5 (Restaurar)
Escolha a data que quer
✓ Recuperado!
```

### "Quanto espaço estou usando?"
```
Menu → 7 → 4 (Gerenciar)
→ 2 (Ver estatísticas)
Vê números exatos
```

### "Quero limpar backups antigos"
```
Menu → 7 → 4 (Gerenciar)
→ 1 (Executar limpeza)
Sistema faz automático
```

---

## 📞 Precisa de Mais Ajuda?

- **Guia Completo:** [[DeploymentUserGuide]]
- **Técnico:** [[BackupStrategySummary]]
- **Fluxo Visual:** [[DatabaseFlowDiagram]]

---

## ✅ Checklist Primeira Vez

- [ ] Abrir FotonSystem
- [ ] Menu → 7 (Implantação)
- [ ] Opção 1 (Validar)
- [ ] Ver mensagem "Base de dados criada com sucesso!"
- [ ] Pronto! Pode usar normalmente

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Guia do Usuário: [[UserGuide]]
- Implantação: [[DeploymentUserGuide]]

**Última atualização:** 05/02/2026  
**Versão:** FotonSystem v1.2.0

---

_Imprima este cartão e coloque perto do computador!_ 📌
