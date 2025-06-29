# 🔌 Sistema WebSocket - Painel de Senhas em Tempo Real

## 📋 Visão Geral

O sistema de WebSocket foi implementado para fornecer atualizações em tempo real entre o **Painel do Atendente** e o **Painel TV**, permitindo que as ações do atendente sejam refletidas instantaneamente na exibição pública.

## 🏗️ Arquitetura

### Componentes Principais

1. **Flask-SocketIO**: Servidor WebSocket integrado ao Flask
2. **Painel do Atendente**: Interface para controle de senhas (protegida por login)
3. **Painel TV**: Interface pública para exibição de senhas
4. **APIs REST**: Endpoints para carregamento inicial de dados
5. **Eventos WebSocket**: Comunicação em tempo real

### Fluxo de Dados

```
[Atendente] → [WebSocket] → [Painel TV]
     ↓              ↓           ↓
[Painel Atendente] → [APIs] → [Atualização]
```

## 🚀 Funcionalidades Implementadas

### 1. Painel do Atendente (`/painel_atendente`)

**Características:**

- ✅ Interface protegida por login (role: `senhas` ou `admin`)
- ✅ Lista de senhas aguardando atendimento
- ✅ Estatísticas em tempo real
- ✅ Botões de ação: Chamar, Atender, Marcar Ausente
- ✅ Atualização automática via WebSocket
- ✅ Design responsivo e moderno

**Ações Disponíveis:**

- **Chamar Senha**: Muda status para "chamado" e notifica painel TV
- **Atender Senha**: Muda status para "em_atendimento"
- **Marcar Ausente**: Muda status para "ausente"
- **Finalizar Atendimento**: Muda status para "atendido"

### 2. Painel TV (`/senhas_tv`)

**Características:**

- ✅ Interface pública (sem login)
- ✅ Exibição de senhas aguardando
- ✅ Estatísticas em tempo real
- ✅ Design otimizado para TV (letras grandes, cores contrastantes)
- ✅ Atualização automática via WebSocket
- ✅ Animações e efeitos visuais

### 3. Eventos WebSocket

**Eventos Implementados:**

| Evento                   | Descrição             | Dados Enviados              |
| ------------------------ | --------------------- | --------------------------- |
| `connect`                | Cliente conectado     | Status de conexão           |
| `disconnect`             | Cliente desconectado  | -                           |
| `senha_chamada`          | Senha foi chamada     | ID, senha, nome, prioridade |
| `senha_atendida`         | Senha em atendimento  | ID, senha, nome             |
| `atendimento_finalizado` | Atendimento concluído | ID, senha, nome             |
| `senha_ausente`          | Senha marcada ausente | ID, senha, nome             |

## 📁 Estrutura de Arquivos

```
app/
├── app.py                          # Configuração do SocketIO
├── routes/
│   └── senhas_routes.py           # Rotas do painel atendente
├── templates/
│   ├── painel_atendente.html      # Template do atendente
│   └── senhas_tv.html             # Template do painel TV
└── models/
    └── cadastro.py                # Modelo com métodos de fila

test_websocket.py                  # Script de teste
adicionar_senhas_websocket_teste.py # Dados de teste
WEBSOCKET_SUMMARY.md              # Esta documentação
```

## 🔧 Configuração

### 1. Dependências

O Flask-SocketIO já está incluído no `requirements.txt`:

```
Flask-SocketIO==5.5.1
python-socketio==5.13.0
```

### 2. Configuração do App

```python
# app/app.py
from flask_socketio import SocketIO, emit, join_room, leave_room

# Inicialização do SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Eventos WebSocket
@socketio.on('chamar_senha')
def handle_chamar_senha(data):
    # Lógica para chamar senha
    socketio.emit('senha_chamada', data, broadcast=True)
```

### 3. Inicialização do Servidor

```python
# Usar socketio.run() em vez de app.run()
socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

## 🧪 Testes

### 1. Script de Teste Automático

```bash
python test_websocket.py
```

**Testes Realizados:**

- ✅ Conectividade do servidor
- ✅ APIs públicas funcionando
- ✅ Painel TV acessível
- ✅ WebSocket detectado
- ✅ Painel atendente protegido

### 2. Dados de Teste

```bash
# Criar dados de teste
python adicionar_senhas_websocket_teste.py

# Remover dados de teste
python adicionar_senhas_websocket_teste.py --limpar
```

**Dados Criados:**

- 8 pessoas com diferentes prioridades
- Senhas automáticas geradas
- Status inicial: "aguardando"

## 🎯 Como Usar

### 1. Iniciar o Sistema

```bash
cd "C:\Multirao mulher"
python app/app.py
```

### 2. Acessar as Interfaces

**Painel TV (Público):**

```
http://127.0.0.1:5000/senhas_tv
```

**Painel Atendente (Login necessário):**

```
http://127.0.0.1:5000/painel_atendente
```

### 3. Fluxo de Teste

1. **Abra o Painel TV** em uma aba do navegador
2. **Faça login** como usuário com role `senhas` ou `admin`
3. **Acesse o Painel Atendente** em outra aba
4. **Teste as ações:**
   - Clique em "Chamar" em uma senha
   - Observe a atualização no painel TV
   - Clique em "Atender"
   - Clique em "Finalizar"
   - Teste "Marcar Ausente"

## 🔍 APIs Disponíveis

### APIs Públicas (Painel TV)

| Endpoint               | Método | Descrição               |
| ---------------------- | ------ | ----------------------- |
| `/api/tv/senhas`       | GET    | Lista senhas aguardando |
| `/api/tv/estatisticas` | GET    | Estatísticas gerais     |

### APIs Protegidas (Painel Atendente)

| Endpoint                   | Método | Descrição                        |
| -------------------------- | ------ | -------------------------------- |
| `/api/senhas/aguardando`   | GET    | Senhas aguardando (com detalhes) |
| `/api/senhas/estatisticas` | GET    | Estatísticas detalhadas          |

## 🎨 Interface do Usuário

### Painel do Atendente

**Características:**

- Design responsivo com Bootstrap
- Cards coloridos por prioridade
- Botões de ação intuitivos
- Status de conexão WebSocket
- Notificações toast
- Modal de confirmação

**Cores por Prioridade:**

- 🟢 **Normal**: Verde
- 🟡 **Alta**: Amarelo
- 🔴 **Urgente**: Vermelho

### Painel TV

**Características:**

- Design fullscreen otimizado para TV
- Gradiente azul de fundo
- Letras grandes e contrastantes
- Animações suaves
- Grid responsivo
- Estatísticas em tempo real

## 🔒 Segurança

### Autenticação

- Painel atendente protegido por login
- Verificação de role (`senhas` ou `admin`)
- Redirecionamento automático para login

### Validação

- Validação de dados no servidor
- Sanitização de inputs
- Logs de todas as ações

## 📊 Logs e Monitoramento

### Logs Implementados

- Conexões/desconexões WebSocket
- Ações de senhas (chamar, atender, finalizar)
- Erros de conexão
- Acessos às APIs

### Monitoramento

- Status de conexão em tempo real
- Contadores de usuários conectados
- Estatísticas de uso

## 🚀 Próximas Melhorias

### Funcionalidades Sugeridas

- [ ] Som de notificação no painel TV
- [ ] Histórico de chamadas
- [ ] Configuração de prioridades
- [ ] Relatórios de atendimento
- [ ] Múltiplas salas de atendimento
- [ ] Notificações push para mobile

### Otimizações Técnicas

- [ ] Compressão de dados WebSocket
- [ ] Cache de dados frequentes
- [ ] Reconexão automática
- [ ] Fallback para polling

## 🐛 Troubleshooting

### Problemas Comuns

**1. WebSocket não conecta**

```bash
# Verificar se o servidor está rodando
python test_websocket.py
```

**2. Atualizações não aparecem**

- Verificar console do navegador
- Verificar logs do servidor
- Confirmar que ambos painéis estão abertos

**3. Erro de permissão**

- Verificar role do usuário
- Fazer logout e login novamente

### Logs Úteis

```bash
# Ver logs em tempo real
tail -f logs/mutirao_mulher.log

# Ver logs específicos do WebSocket
grep "WebSocket" logs/mutirao_mulher.log
```

## 📞 Suporte

Para dúvidas ou problemas:

1. Verificar logs do sistema
2. Executar script de teste
3. Verificar console do navegador
4. Consultar esta documentação

---

**🎉 Sistema WebSocket implementado com sucesso!**

O sistema agora oferece atualizações em tempo real entre o painel do atendente e o painel TV, proporcionando uma experiência fluida e profissional para o controle de senhas do Mutirão da Mulher Rural.
