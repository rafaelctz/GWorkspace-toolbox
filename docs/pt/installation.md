# Instalação

O GWorkspace Toolbox é executado como um contêiner Docker, tornando a instalação simples e consistente em todas as plataformas.

## Pré-requisitos

- Docker e Docker Compose instalados no seu sistema
- Conta de administrador do Google Workspace
- Projeto do Google Cloud com Admin SDK API habilitado

## Passo 1: Instalar Docker

### Windows
Baixe e instale [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop)

### macOS
Baixe e instale [Docker Desktop para Mac](https://www.docker.com/products/docker-desktop)

### Linux
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## Passo 2: Configuração do Google Workspace

### Habilitar Admin SDK API
1. Vá para [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto ou selecione um existente
3. Navegue para **APIs & Services** > **Library**
4. Procure por "Admin SDK API" e habilite-o

### Criar Credenciais OAuth 2.0
1. Vá para **APIs & Services** > **Credentials**
2. Clique em **Create Credentials** > **OAuth client ID**
3. Selecione **Web application**
4. Adicione URI de redirecionamento autorizado: `http://localhost:8000/oauth2callback`
5. Baixe o arquivo JSON de credenciais

## Passo 3: Implantar com Docker

### Criar Diretório do Projeto
```bash
mkdir gworkspace-toolbox
cd gworkspace-toolbox
```

### Baixar Configuração do Docker Compose
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/rafaelctz/GWorkspace-toolbox/main/docker-compose.yml
```

### Adicionar suas Credenciais
1. Salve suas credenciais OAuth baixadas como `credentials.json` no diretório do projeto
2. A aplicação irá guiá-lo através da autenticação na primeira execução

### Iniciar a Aplicação
```bash
docker-compose up -d
```

A aplicação estará disponível em `http://localhost:8000`

## Passo 4: Configuração Inicial

1. Abra seu navegador em `http://localhost:8000`
2. Clique no botão **Autenticar**
3. Faça login com sua conta de administrador do Google Workspace
4. Conceda as permissões solicitadas
5. Você será redirecionado de volta para a aplicação

## Atualizações Automáticas

A configuração do Docker Compose inclui Watchtower, que verifica automaticamente atualizações diariamente e mantém sua instalação atualizada.

Para atualizar manualmente:
```bash
docker-compose pull
docker-compose up -d
```

## Próximos Passos

Agora que está instalado, confira o [Guia de Início Rápido](/pt/quickstart) para aprender a usar os recursos.

## Solução de Problemas

Se você encontrar problemas, consulte o [Guia de Solução de Problemas](/pt/troubleshooting) ou verifique [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues).
