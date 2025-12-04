# Perguntas Frequentes

Perguntas e respostas comuns sobre o GWorkspace Toolbox.

## Geral

### O que é o GWorkspace Toolbox?

O GWorkspace Toolbox é um conjunto gratuito e de código aberto de ferramentas projetado para ajudar administradores do Google Workspace a automatizar tarefas administrativas comuns como gerenciar alias de e-mail, atributos de usuário e associações de grupos.

### O GWorkspace Toolbox é gratuito?

Sim, o GWorkspace Toolbox é completamente gratuito e de código aberto sob a Licença MIT. Não há recursos premium ou níveis pagos.

### Qual edição do Google Workspace eu preciso?

O GWorkspace Toolbox funciona com todas as edições do Google Workspace (Business Starter, Business Standard, Business Plus, Enterprise) desde que você tenha acesso de administrador.

### Posso usar isso com uma conta Gmail gratuita?

Não, o GWorkspace Toolbox requer um domínio Google Workspace (anteriormente G Suite) com acesso de administrador. Ele usa o Admin SDK API que não está disponível para contas Gmail pessoais.

## Instalação e Configuração

### Preciso de habilidades técnicas para instalar o GWorkspace Toolbox?

Familiaridade básica com Docker e linha de comando é útil, mas a instalação é direta. Siga o [Guia de Instalação](/pt/installation) passo a passo.

### Posso executar isso no Windows?

Sim, o GWorkspace Toolbox é executado no Windows, macOS e Linux usando Docker Desktop.

### Preciso de um servidor para executar o GWorkspace Toolbox?

Não, você pode executá-lo no seu computador local. No entanto, para que as sincronizações agendadas funcionem continuamente, você precisará de uma máquina que permaneça ligada (servidor local, VPS ou instância na nuvem).

### Quais portas o GWorkspace Toolbox usa?

Por padrão, ele usa a porta 8000. Você pode alterar isso no arquivo `docker-compose.yml` se necessário.

### Onde meus dados são armazenados?

Todos os dados são armazenados localmente:
- Tokens de autenticação: arquivo `token.json`
- Agendamentos de sincronização: banco de dados SQLite no diretório `./database`
- Exportações CSV: diretório `./exports`

Nenhum dado é enviado para servidores externos exceto APIs do Google.

## Autenticação e Segurança

### Meus dados do Google Workspace estão seguros?

Sim. O GWorkspace Toolbox usa autenticação OAuth 2.0 e solicita apenas as permissões mínimas necessárias. Suas credenciais são armazenadas localmente e nunca transmitidas para terceiros.

### Quais permissões o GWorkspace Toolbox precisa?

A ferramenta solicita:
- Acesso de leitura a usuários do diretório (para Extrator de Alias, Sincronização de Grupos OU)
- Acesso de escrita a usuários do diretório (para Injetor de Atributos)
- Gerenciar grupos (para Sincronização de Grupos OU)

### Posso revogar o acesso?

Sim, você pode revogar o acesso a qualquer momento:
1. Vá para [Permissões da Conta Google](https://myaccount.google.com/permissions)
2. Encontre GWorkspace Toolbox
3. Clique em "Remover Acesso"

### Preciso ser um superadministrador?

Sim, a maioria dos recursos requer privilégios de superadministrador. Alguns recursos podem funcionar com funções de administrador delegado que tenham permissões apropriadas.

## Recursos

### O Extrator de Alias pode exportar alias apenas para OUs específicas?

Atualmente, o Extrator de Alias exporta alias para todos os usuários no domínio. Você pode filtrar o arquivo CSV depois por endereço de e-mail principal para obter usuários de OUs específicas.

### O Injetor de Atributos funciona com campos padrão do Google?

Não, o Injetor de Atributos funciona apenas com atributos de esquema personalizado. Campos padrão como nome, telefone ou cargo devem ser gerenciados através do Admin Console.

### Posso sincronizar múltiplas OUs para um grupo?

Sim, você pode criar múltiplos trabalhos de sincronização que todos apontem para o mesmo grupo. Use o modo de Sincronização Inteligente para garantir que os usuários de todas as OUs sejam adicionados sem se removerem mutuamente.

## Solução de Problemas

### A aplicação não inicia

Verifique:
1. Docker está executando: `docker ps`
2. A porta 8000 não está em uso por outra aplicação
3. O arquivo Docker Compose está presente
4. Execute `docker-compose logs` para ver mensagens de erro

### Não consigo autenticar

Certifique-se de que:
1. O arquivo credentials.json está no diretório do projeto
2. O URI de redirecionamento do cliente OAuth inclui `http://localhost:8000/oauth2callback`
3. O Admin SDK API está habilitado no Google Cloud Console
4. Você está usando uma conta de administrador

### As sincronizações agendadas não estão sendo executadas

Verifique:
1. O contêiner Docker está executando: `docker ps`
2. O agendamento está habilitado na UI
3. O volume do banco de dados está persistido (verifique docker-compose.yml)
4. Verifique os logs para erros: `docker-compose logs -f app`

## Atualizações e Manutenção

### Como atualizo o GWorkspace Toolbox?

Se estiver usando Watchtower (incluído no docker-compose.yml), as atualizações são automáticas. Atualização manual:

```bash
docker-compose pull
docker-compose up -d
```

### Com que frequência o GWorkspace Toolbox é atualizado?

As atualizações são lançadas conforme necessário para correções de bugs, patches de segurança e novos recursos. Confira [GitHub Releases](https://github.com/rafaelctz/GWorkspace-toolbox/releases) para o changelog.

## Contribuição

### Posso contribuir para o GWorkspace Toolbox?

Sim! O GWorkspace Toolbox é de código aberto. Veja o [Guia de Contribuição](https://github.com/rafaelctz/GWorkspace-toolbox/blob/main/CONTRIBUTING.md) para detalhes.

### Encontrei um bug, como reporto?

Por favor abra uma issue no [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues) com:
- Descrição do problema
- Passos para reproduzir
- Comportamento esperado vs real
- Saída de log se aplicável

## Ainda Tem Perguntas?

- Confira o [Guia de Solução de Problemas](/pt/troubleshooting)
- Procure no [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Abra uma nova issue se sua pergunta não estiver respondida
