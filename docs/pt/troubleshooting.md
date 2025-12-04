# Guia de Solução de Problemas

Soluções para problemas comuns ao usar o GWorkspace Toolbox.

## Problemas de Instalação

### Docker Não Inicia

**Problema**: O contêiner Docker não inicia ou sai imediatamente.

**Soluções**:

```bash
# Verificar se o Docker está executando
docker ps

# Ver logs do contêiner
docker-compose logs app

# Verificar conflitos de porta
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Reiniciar contêineres
docker-compose down
docker-compose up -d
```

### Porta Já em Uso

**Problema**: Mensagem de erro sobre porta 8000 em uso.

**Solução**: Altere a porta no docker-compose.yml:

```yaml
services:
  app:
    ports:
      - "8080:8000"  # Use 8080 em vez de 8000
```

Então acesse a aplicação em `http://localhost:8080`

### Arquivo de Credenciais Não Encontrado

**Problema**: A aplicação não consegue encontrar credentials.json.

**Soluções**:

```bash
# Verificar se o arquivo existe
ls -la credentials.json

# Garantir que está no diretório do projeto
pwd
ls

# Verificar montagem de volume no docker-compose.yml
cat docker-compose.yml | grep credentials
```

## Problemas de Autenticação

### Erro OAuth: redirect_uri_mismatch

**Problema**: Erro OAuth mencionando incompatibilidade de URI de redirecionamento.

**Solução**:

1. Vá para [Google Cloud Console](https://console.cloud.google.com)
2. Navegue para APIs & Services > Credentials
3. Edite seu OAuth 2.0 Client ID
4. Em "Authorized redirect URIs", adicione:
   - `http://localhost:8000/oauth2callback`
5. Salve e tente autenticar novamente

### A Autenticação Continua Falhando

**Problema**: Não consegue completar o fluxo de autenticação.

**Lista de verificação**:

- [ ] Admin SDK API está habilitado no Google Cloud Console
- [ ] O URI de redirecionamento do cliente OAuth está configurado corretamente
- [ ] Você está usando uma conta de administrador
- [ ] credentials.json é o cliente OAuth (não Service Account)
- [ ] O navegador permite popups do localhost
- [ ] Não há extensões do navegador bloqueando o fluxo

**Redefinir autenticação**:

```bash
# Parar contêineres
docker-compose down

# Remover arquivo de token
rm token.json

# Iniciar contêineres
docker-compose up -d

# Tentar autenticar novamente
```

## Problemas do Extrator de Alias

### Nenhum Alias no CSV

**Problema**: O arquivo CSV está vazio ou faltando alias.

**Possíveis causas**:

1. **Nenhum alias existe**: Verifique no Admin Console se os usuários têm alias
2. **Problema de permissão**: Certifique-se de estar autenticado como administrador
3. **API não habilitada**: Verifique se o Admin SDK API está habilitado

## Problemas do Injetor de Atributos

### Erro "Atributo não encontrado"

**Problema**: Erro dizendo que o atributo não existe.

**Solução**:

1. Verifique se o esquema personalizado existe no Admin Console:
   - Directory > Users > Manage custom attributes
2. Verifique o formato do nome do atributo: `NomeEsquema.nomeCampo`
3. Garanta correspondência exata de maiúsculas (sensível a maiúsculas)

### Erro "OU não encontrada"

**Problema**: Erro dizendo que a unidade organizacional não existe.

**Solução**:

1. Verifique se o caminho da OU começa com `/`
2. Verifique o caminho exato no Admin Console (sensível a maiúsculas)
3. Sem espaços finais ou caracteres especiais

## Problemas de Sincronização de Grupos OU

### Erro "Grupo não encontrado"

**Problema**: Erro dizendo que o grupo não existe.

**Soluções**:

1. Verifique se o endereço de e-mail do grupo está exatamente correto
2. Verifique se o grupo existe no Admin Console ou Gmail
3. Certifique-se de ter permissão para gerenciar o grupo
4. O e-mail do grupo deve estar completo: `equipe@empresa.com`

### Membros Não Estão Sendo Adicionados

**Problema**: A sincronização completa mas os membros não são adicionados ao grupo.

**Lista de verificação**:

- [ ] O grupo existe e é acessível
- [ ] A OU contém usuários (não está vazia)
- [ ] Você tem permissão para gerenciar o grupo
- [ ] Os usuários não estão já no grupo
- [ ] As permissões de API estão corretas

### A Sincronização Agendada Não Está Sendo Executada

**Problema**: Os trabalhos de sincronização agendados não estão sendo executados.

**Lista de verificação**:

- [ ] O contêiner Docker está executando continuamente
- [ ] O botão de agendamento está habilitado na UI
- [ ] O volume do banco de dados está persistido
- [ ] Não há erros nos logs do contêiner

**Depurar**:

```bash
# Verificar se o contêiner está executando
docker ps | grep gworkspace

# Ver logs
docker-compose logs -f app

# Verificar se o arquivo de banco de dados existe
ls -la database/
```

## Problemas de UI/Interface

### A Página Não Carrega

**Problema**: O navegador mostra erro de conexão ou página em branco.

**Soluções**:

```bash
# Verificar se o contêiner está executando
docker ps

# Verificar saúde do contêiner
docker-compose ps

# Ver logs para erros
docker-compose logs app

# Reiniciar contêineres
docker-compose restart

# Verificar URL
# Deve ser http://localhost:8000 (não https)
```

## Obtendo Mais Ajuda

### Habilitar Registro de Depuração

Para logs mais detalhados:

```yaml
# Em docker-compose.yml, adicione variável de ambiente
services:
  app:
    environment:
      - PORT=8000
      - HOST=0.0.0.0
      - LOG_LEVEL=DEBUG  # Adicione esta linha
```

### Reportar Problemas

Se não conseguir resolver o problema:

1. Verifique [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues) para problemas similares
2. Revise o [FAQ](/pt/faq)
3. Abra uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Saída de log
   - Informações do sistema

Ainda tendo problemas? Abra uma issue no [GitHub](https://github.com/rafaelctz/GWorkspace-toolbox/issues) com todos os detalhes.
