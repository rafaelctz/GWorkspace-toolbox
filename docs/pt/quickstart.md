# Guia de Início Rápido

Este guia irá orientá-lo no uso dos recursos do GWorkspace Toolbox pela primeira vez.

## Pré-requisitos

- GWorkspace Toolbox instalado e em execução
- Autenticado com sua conta de administrador do Google Workspace

## Extraindo Alias de Usuário

O Extrator de Alias permite exportar todos os alias de usuário do seu domínio para um arquivo CSV.

### Passos

1. Abra o GWorkspace Toolbox em `http://localhost:8000`
2. Clique em **Extrator de Alias** na barra lateral
3. Certifique-se de estar autenticado (indicador verde no canto superior direito)
4. Clique no botão **Extrair Aliases**
5. Aguarde a conclusão da extração
6. Baixe o arquivo CSV gerado

### O que Você Obtém

O arquivo CSV contém:
- E-mail principal do usuário
- Endereço de e-mail do alias
- Uma linha por alias

### Casos de Uso

- Auditar todos os alias de e-mail no seu domínio
- Planejar migrações de e-mail
- Documentar roteamento de e-mail atual
- Relatórios de conformidade

## Injetando Atributos Personalizados

O Injetor de Atributos permite adicionar atributos personalizados em lote a usuários em Unidades Organizacionais específicas.

### Passos

1. Clique em **Injetor de Atributos** na barra lateral
2. Digite ou selecione o caminho da **Unidade Organizacional** alvo (ex., `/Estudantes/Regional`)
3. Digite o **Nome do Atributo** (campo de esquema personalizado)
4. Digite o **Valor do Atributo** para atribuir
5. Clique no botão **Injetar Atributos**
6. Revise os resultados mostrando quantos usuários foram atualizados

### Casos de Uso

- Atribuir códigos de departamento a todos os usuários em uma OU
- Definir tipos de funcionário para filtragem organizacional
- Adicionar informações de centro de custo para relatórios
- Aplicar qualquer atributo personalizado em escala

## Sincronizando OU para Grupos

O recurso de Sincronização de Grupos OU sincroniza automaticamente usuários de Unidades Organizacionais para Grupos do Google com configurações salvas.

### Passos

1. Clique em **Sincronização de Grupos OU** na barra lateral
2. Clique em **+ Nova Configuração**
3. Selecione uma ou mais **Unidades Organizacionais** da árvore (ex., `/Alunos/Ano-10`)
4. Digite o **E-mail do Grupo Alvo** (ex., `alunos-ano10@escola.edu`)
5. Opcionalmente forneça um nome e descrição do grupo
6. Clique em **Sincronizar** para criar a configuração e executar a primeira sincronização

### Como Funciona a Sincronização

**Primeira Sincronização (Automática - Modo Seguro):**
- Cria o grupo se não existir
- Adiciona todos os usuários das OUs selecionadas ao grupo
- **Nunca remove membros existentes do grupo**
- Seguro para grupos que já têm membros

**Sincronizações Subsequentes (Automáticas - Modo Espelho):**
- Quando você clica em "Ressincronizar" em uma configuração salva
- Adiciona usuários que se juntaram à OU
- **Remove usuários que saíram da OU**
- Faz o grupo refletir a OU exatamente

⚠️ **Importante**: O sistema automaticamente usa modo seguro para a primeira sincronização, depois muda para modo espelho para todas as sincronizações subsequentes. Você não pode escolher manualmente o modo de sincronização - é determinado por ser a primeira vez sincronizando aquela configuração.

### Gerenciamento de Configurações

Após criar uma configuração, você pode:
- **Ressincronizar**: Atualiza o grupo com os membros atuais da OU
- **Sincronizar Todas**: Executa todas as configurações salvas de uma vez
- **Exportar**: Baixa configurações para backup
- **Importar**: Restaura configurações do backup
- **Excluir**: Remove configurações que você não precisa mais

## Seleção de Idioma

O GWorkspace Toolbox suporta três idiomas. Altere o idioma usando o menu suspenso no canto superior direito:

- English (EN)
- Español (ES)
- Português (PT)

Sua preferência de idioma é salva automaticamente.

## Melhores Práticas

### Segurança
- Sempre use contas de administrador com privilégios mínimos necessários
- Revise as permissões OAuth antes de conceder acesso
- Mantenha o arquivo credentials.json seguro e nunca o envie para controle de versão

### Testes
- Teste operações em OUs pequenas primeiro
- Revise a associação do grupo antes de executar sincronizações subsequentes (elas removerão membros que não estão na OU)
- Exporte e revise arquivos CSV antes de fazer alterações em massa

### Monitoramento
- Verifique os logs do Docker para quaisquer erros: `docker-compose logs -f`
- Monitore o status de trabalhos de sincronização na interface de Sincronização de Grupos OU
- Revise regularmente as marcas de tempo da última sincronização nas configurações salvas

## Próximos Passos

- Explore a [Documentação Detalhada de Recursos](/pt/features)
- Revise o [FAQ](/pt/faq) para perguntas comuns
- Confira [Solução de Problemas](/pt/troubleshooting) se encontrar problemas

## Obtendo Ajuda

Precisa de assistência?
- Confira o [FAQ](/pt/faq)
- Visite [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Revise o [Guia de Solução de Problemas](/pt/troubleshooting)
