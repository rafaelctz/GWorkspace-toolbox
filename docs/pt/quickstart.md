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
2. Digite ou selecione o caminho da **Unidade Organizacional** alvo (ex., `/Vendas/Regional`)
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

O recurso de Sincronização de Grupos OU adiciona automaticamente usuários de uma Unidade Organizacional a um Grupo do Google.

### Passos

1. Clique em **Sincronização de Grupos OU** na barra lateral
2. Digite o caminho da **Unidade Organizacional** (ex., `/Marketing`)
3. Digite o **E-mail do Grupo Alvo** (ex., `equipe-marketing@empresa.com`)
4. Escolha o modo de sincronização:
   - **Sincronização Inteligente**: Apenas adiciona novos membros (preserva usuários adicionados manualmente)
   - **Sincronização Completa**: Espelha a OU exatamente (remove usuários que não estão na OU)
5. Opcionalmente habilite **Agendar Sincronização** para sincronização automática diária
6. Clique em **Sincronizar Agora** para executar imediatamente

### Sincronização Inteligente vs Sincronização Completa

**Sincronização Inteligente** (Recomendada):
- Adiciona usuários da OU ao grupo
- Nunca remove ninguém do grupo
- Seguro para grupos com membros gerenciados manualmente
- Melhor para a maioria dos casos de uso

**Sincronização Completa**:
- A associação do grupo corresponde exatamente à OU
- Remove usuários que não estão na OU
- Use apenas se o grupo deve espelhar a OU exatamente
- Cuidado: removerá membros adicionados manualmente

### Agendamento

Habilite **Agendar Sincronização** para executar automaticamente a sincronização diariamente à meia-noite. O agendamento persiste através de reinicializações da aplicação.

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
- Use o modo de Sincronização Inteligente a menos que você especificamente precise da Sincronização Completa
- Exporte e revise arquivos CSV antes de fazer alterações em massa

### Monitoramento
- Verifique os logs do Docker para quaisquer erros: `docker-compose logs -f`
- Monitore o status de trabalhos de sincronização na interface de Sincronização de Grupos OU
- Revise regularmente o histórico de sincronização agendada

## Próximos Passos

- Explore a [Documentação Detalhada de Recursos](/pt/features)
- Revise o [FAQ](/pt/faq) para perguntas comuns
- Confira [Solução de Problemas](/pt/troubleshooting) se encontrar problemas

## Obtendo Ajuda

Precisa de assistência?
- Confira o [FAQ](/pt/faq)
- Visite [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Revise o [Guia de Solução de Problemas](/pt/troubleshooting)
