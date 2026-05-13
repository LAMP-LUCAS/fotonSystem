---
type: guide
domain: core
status: active
tags: [deployment, backup, user]
---
# 🚀 Guia Rápido: Implantação e Backup Inteligente (DeploymentUserGuide)

## Para o Usuário Final (Você!)

Bem-vindo! Este guia explica a **nova ferramenta de Implantação** de forma simples e prática.

---

## 🎯 Resumo em 30 Segundos

Nós adicionamos uma **ferramenta automática** que:

✅ Cria a base de dados automaticamente (nunca mais erro!)
✅ Faz backup inteligente (sem encher o disco)
✅ Permite recuperar dados antigos se algo der errado
✅ Menu fácil para controlar tudo

**Você não precisa fazer nada.** O sistema funciona sozinho!

---

## ❓ Cenários Comuns

### 1️⃣ "Primeira vez que abro o FotonSystem"

```
Menu Principal
├─ 1. Gerenciar Clientes
├─ 2. Gerenciar Serviços
├─ ...
└─ 7. 🆕 Implantação (Gerenciar Base de Dados)  ← Pode ignorar por enquanto
```

**O que acontece:**
- Sistema detecta que a base não existe
- Cria automaticamente com estrutura correta
- Você já pode criar clientes!

**Você precisa fazer algo?** NÃO! Tudo automático.

---

### 2️⃣ "Recebi um erro de base de dados"

Se receber erro tipo: `[Errno 2] No such file or directory: 'baseDados.xlsx'`

**Solução em 3 cliques:**
1. Menu Principal → **7. Implantação**
2. Escolha **1. Validar Base de Dados**
3. Se tiver problema, escolha **3. Reparar Base Existente**

Pronto! Sistema corrigido.

---

### 3️⃣ "Meu disco está cheio! Help!"

Não se preocupe. O sistema **not enche o disco** com backups.

**Como funciona:**
- Cada operação (criar cliente, editar) faz backup
- MAS: Se você fizer 100 operações, não cria 100 backups!
- Cria apenas ~10 backups (97% de economia 🎉)

**Quantas operações até problemas?**
- Plano de 1 ano: ~36,000 operações
- Espaço usado: 5.4 GB (confortável)
- Nunca vai encher!

**Se quiser controlar:**
1. Menu Principal → **7. Implantação**
2. Escolha **4. Gerenciar Backups**
3. Veja quanto espaço está usando

---

### 4️⃣ "Quero recomeçar tudo (resetar base)"

1. Menu Principal → **7. Implantação**
2. Escolha **2. Criar Nova Base (com confirmação)**
3. Sistema avisa que vai sobrescrever
4. Confirma? Pronto! Base nova criada

**Nota:** Antes de deletar, faz um backup. Pode recuperar depois!

---

### 5️⃣ "Perdi dados acidentalmente, posso recuperar?"

SIM! O sistema guarda backups automáticos.

1. Menu Principal → **7. Implantação**
2. Escolha **5. Restaurar de Backup**
3. Sistema mostra lista de backups com data/hora
4. Escolha qual restaurar

**Quantos backups guarda?**
- Últimas 24h: 1 por hora (máximo 24)
- Últimos 7 dias: 1 por dia (máximo 7)
- Últimas 4 semanas: 1 por semana (máximo 4)
- Últimos 3 meses: 1 por mês (máximo 3)

Você **sempre** tem um backup de qualquer período importante!

---

## 🎮 Menu Completo de Implantação

Quando você clica em **"7. Implantação"**, abre este menu:

```
GERENCIADOR DE DEPLOYMENT
═══════════════════════════════════════════════════════
Localização da Base: C:\Users\Seu Nome\AppData\Local\FotonSystem\baseDados.xlsx

1. Validar Base de Dados
   └─ Verifica se arquivo existe e tem estrutura correta

2. Criar Nova Base (com confirmação)
   └─ Cria uma base novinha em folha (pede confirmação primeiro!)

3. Reparar Base Existente
   └─ Se base está corrompida, tenta consertar

4. Gerenciar Backups
   └─ Vê quanto espaço está usando, limpa se necessário

5. Restaurar de Backup
   └─ Mostra lista de backups antigos para recuperar

0. Sair
```

---

## 📊 Informações Úteis

### Onde fica meu banco de dados?

```
Windows:
C:\Users\SEU_USUARIO\AppData\Local\FotonSystem\baseDados.xlsx

Mac:
~/Library/Application Support/FotonSystem/baseDados.xlsx

Linux:
~/.local/share/FotonSystem/baseDados.xlsx
```

**Nota:** AppData é uma pasta oculta no Windows. Para ver:
- Abra o Explorador de Arquivos
- Clique em "Exibição" → "Opções"
- Marque "Mostrar arquivos ocultos"

### O que tem de backup em disco agora?

Menu → 7. Implantação → 4. Gerenciar Backups → 2. Ver estatísticas detalhadas

Aí você vê:
- Quantos backups tem
- Quanto espaço estão usando
- Quanto tempo de recuperação tem

**Exemplo:**
```
Últimas 24h (por hora):       6 backups -  9.00 MB
Últimos 7 dias (diários):     6 backups -  9.00 MB
Últimas 4 semanas (semanais): 4 backups -  6.00 MB
Últimos 3 meses (mensais):    3 backups -  4.50 MB
──────────────────────────────────────────────────────
TOTAL                        19 backups - 28.50 MB
```

---

## ⚡ Resumo: Você Precisa Saber

| Situação | O que Fazer | Resultado |
|----------|-------------|-----------|
| Primeira vez | Nada! Cria automático | Base pronta |
| Erro de base | Menu → 7 → 1 (validar) | Sistema corrigido |
| Disco cheio | Menu → 7 → 4 (gerenciar) | Espaço liberado |
| Resetar tudo | Menu → 7 → 2 (criar nova) | Base nova |
| Recuperar dados | Menu → 7 → 5 (restaurar) | Dados recuperados |

---

## ❓ Perguntas Frequentes

**P: Por que preciso dessa ferramenta?**
R: Sem ela, se base sumisse, o sistema inteiro quebrava. Agora trata sozinho!

**P: Perco performance com backups inteligentes?**
R: Zero impacto! Sistema detecta quando fazer backup sem atrasar você.

**P: Posso editar os backups?**
R: Não é recomendado, mas eles são arquivos Excel normais. Não mexe!

**P: Preciso de Internet para backups?**
R: Não! Tudo fica no seu computador. Completamente offline.

**P: Posso configuar a política de backups?**
R: Sim, mas é avançado. Entre em contato se precisar (muita atividade = configurar timeout).

**P: Quantos backups são "demais"?**
R: Sistema limpa automaticamente. Máximo 500 MB por padrão. Nunca pede espaço.

---

## 🆘 Se Algo der Errado

### "Erro: Base de dados corrompida"

1. Menu → 7. Implantação → 3. Reparar
2. Sistema tenta consertar automaticamente
3. Se ainda não funcionar → 5. Restaurar de Backup

### "Menu 7 não aparece"

Atualize o FotonSystem. A ferramenta é nova.

### "Onde estão meus dados?"

**Nunca** são deletados na recuperação. Se restaurar um backup antigo, ele guarda o novo como cópia de segurança.

Exemplo:
```
Você tinha: BKP-baseDados_20260204.xlsx (backup antigo)
Você restaura: Copia para BKP-baseDados_ANTES_DE_RESTAURAR.xlsx
Resultado: Tem os dois! Pode voltar se errou.
```

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Soluções de Base: [[DatabaseInitializationSolution]]
- Diagrama de Fluxo: [[DatabaseFlowDiagram]]

**Tudo funciona automático.** Você só usa o menu se quiser ver estatísticas ou em caso de emergência.

Boa sorte! 🚀
