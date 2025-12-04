# Sincronização de Grupos OU

O recurso de Sincronização de Grupos OU sincroniza automaticamente usuários de Unidades Organizacionais para Grupos do Google, com configurações salvas que podem ser reutilizadas e gerenciadas.

![Interface de Sincronização de Grupos OU](/screenshots/ou-group-sync.png)

## Visão Geral

Manter os Grupos do Google sincronizados com Unidades Organizacionais pode ser demorado e propenso a erros quando feito manualmente. A Sincronização de Grupos OU automatiza este processo mantendo configurações de sincronização salvas que você pode executar quando necessário.

## Como Funciona

1. **Criar uma Configuração de Sincronização**: Selecione uma ou mais OUs e especifique o Grupo do Google de destino
2. **Primeira Sincronização**: A sincronização inicial apenas adiciona usuários ao grupo (modo seguro - nunca remove ninguém)
3. **Sincronizações Subsequentes**: Sincronizações posteriores refletem a OU exatamente (adiciona novos usuários E remove usuários que não estão mais na OU)
4. **Reutilizar**: Salve configurações e sincronize novamente a qualquer momento com um único clique

## Entendendo o Comportamento de Sincronização

### Primeira Sincronização (Automática - Modo Seguro)

Quando você cria uma nova configuração de sincronização e a executa pela primeira vez:

**O que faz:**
- Cria o grupo se não existir
- Adiciona todos os usuários das OUs selecionadas ao grupo
- **Nunca remove membros existentes do grupo**
- Seguro para grupos que já têm membros

**Exemplo:**
```
Membros OU: aluno1@, aluno2@, aluno3@
Grupo Antes: aluno1@, professor@ (adicionado manualmente)
Grupo Depois: aluno1@, aluno2@, aluno3@, professor@
Resultado: 2 novos alunos adicionados, professor@ preservado
```

### Sincronizações Subsequentes (Automáticas - Modo Espelho)

Quando você clica em "Ressincronizar" em uma configuração existente:

**O que faz:**
- Compara a associação atual do grupo com a associação da OU
- Adiciona usuários que se juntaram à OU
- **Remove usuários que saíram da OU**
- Faz o grupo refletir a OU exatamente

**Exemplo:**
```
Membros OU: aluno1@, aluno2@, aluno4@ (aluno3@ transferido, aluno4@ entrou)
Grupo Antes: aluno1@, aluno2@, aluno3@, professor@
Grupo Depois: aluno1@, aluno2@, aluno4@
Resultado: aluno4@ adicionado, aluno3@ e professor@ removidos
```

⚠️ **Importante**: Após a primeira sincronização, as sincronizações subsequentes removerão membros que não estão na OU. O sistema determina automaticamente qual modo de sincronização usar com base em se é a primeira vez sincronizando aquela configuração.

## Configurações Salvas

### Criando uma Configuração

1. Clique em "+ Nova Configuração"
2. Selecione uma ou mais OUs da árvore
3. Digite o email do grupo de destino (ex., `alunos-ano10@escola.edu`)
4. Opcionalmente forneça um nome e descrição do grupo
5. Clique em "Sincronizar" para criar a configuração e executar a primeira sincronização

### Gerenciando Configurações

Uma vez salvas, você pode:

- **Ressincronizar**: Clique no botão de sincronização para atualizar o grupo com os membros atuais da OU
- **Exportar**: Baixe uma configuração individual como JSON
- **Excluir**: Remova uma configuração que você não precisa mais
- **Sincronizar Todas**: Execute todas as configurações salvas de uma vez

A interface mostra:
- Endereço de email do grupo
- Número de OUs sendo sincronizadas
- Marca de tempo da última sincronização
- Botões de ação rápida para cada configuração

### Exportar e Importar

**Exportar Todas as Configurações:**
- Clique em "Exportar Todas" para baixar todas as configurações salvas como arquivo JSON
- Útil para backup ou migração para outra instância

**Importar Configurações:**
- Clique em "Importar" e selecione um arquivo JSON previamente exportado
- As configurações são adicionadas (as existentes são puladas)
- Útil para restaurar backups ou compartilhar configurações

## Casos de Uso Comuns para Escolas

### Listas de Email de Turmas

Manter automaticamente grupos de email de turmas:

```
OUs: /Alunos/Ano-10
Grupo: alunos-ano10@escola.edu

Resultado: Todos os alunos do 10º ano automaticamente na lista de email
Primeira sincronização: Adiciona todos os alunos atuais
Sincronizações posteriores: Atualiza quando alunos transferem
```

### Grupos de Departamentos de Professores

Manter grupos de departamentos de professores atualizados:

```
OUs: /Professores/Ciencias
Grupo: professores-ciencias@escola.edu

Resultado: O grupo sempre reflete o quadro atual do departamento de ciências
Primeira sincronização: Adiciona todos os professores de ciências
Sincronizações posteriores: Remove professores transferidos, adiciona novas contratações
```

### Acesso por Nível de Ano

Conceder acesso apropriado aos recursos por ano:

```
OUs: /Alunos/Ano-12
Grupo: alunos-ultimo-ano@escola.edu

Resultado: Alunos do último ano obtêm acesso a:
- Cursos do Classroom apenas para o último ano
- Recursos de preparação universitária
- Materiais de planejamento de formatura
```

### Grupos Multi-OU

Combinar múltiplas OUs em um grupo:

```
OUs: /Alunos/Ano-11, /Alunos/Ano-12
Grupo: alunos-avancados@escola.edu

Resultado: Todos os alunos júniores e seniores em um grupo para:
- Acesso a cursos avançados
- Programas de liderança estudantil
- Workshops de preparação universitária
```

### Grupos de Edifícios do Campus

Sincronizar usuários por campus ou edifício físico:

```
OUs: /Professores/Primaria, /Funcionarios/Primaria
Grupo: campus-primaria@escola.edu

Resultado: Todo o pessoal do campus primário no grupo para:
- Anúncios do edifício
- Notificações de emergência
- Acesso a recursos do campus
```

## Melhores Práticas

### Antes da Primeira Sincronização

Se o grupo já tem membros que você quer manter:
1. Verifique quem está atualmente no grupo
2. Certifique-se de que esses usuários também estão nas OUs sendo sincronizadas
3. Ou esteja ciente de que eles serão removidos em sincronizações subsequentes

### Convenções de Nomenclatura de Grupos

Use nomenclatura clara para indicar grupos sincronizados:
- `alunos-ano10-auto@escola.edu` (sincronizado automaticamente)
- `alunos-ano10-manual@escola.edu` (gerenciado manualmente)
- Isso ajuda a prevenir confusão sobre quais grupos são gerenciados por sincronização

### Documentação

Documente suas configurações de sincronização:
- Quais OUs sincronizam com quais grupos
- Propósito de cada grupo sincronizado
- Contagens de membros esperadas
- Quem pode acionar ressincronizações

### Ressincronização Regular

Programe ressincronizações regulares (você deve acioná-las manualmente):
- Semanal: Para grupos dinâmicos (anos de alunos, novas contratações)
- Mensal: Para grupos estáveis (departamentos, edifícios)
- Após mudanças importantes: Promoções de nível de ano, reorganizações

## Permissões Necessárias

A Sincronização de Grupos OU requer estes escopos da API do Google Workspace:

- `https://www.googleapis.com/auth/admin.directory.user.readonly` (ler usuários de OUs)
- `https://www.googleapis.com/auth/admin.directory.group` (gerenciar grupos e associação)

## Requisitos do Grupo

### Criação do Grupo

A ferramenta criará o grupo se não existir, usando:
- O endereço de email que você especificar
- O nome do grupo que você fornecer (ou derivado do email)
- A descrição que você fornecer (opcional)

### Formato do Email do Grupo

Deve ser um email de Grupo do Google válido:
- `alunos-ano10@escola.edu` ✓
- `professores.ciencias@escola.edu` ✓
- `clube-robotica@escola.edu` ✓
- `email-invalido` ✗

### Tipos de Grupos

Funciona com:
- Grupos do Google regulares
- Grupos de segurança
- Listas de email
- Grupos de discussão

## Limitações

### Escopo da OU

A sincronização opera apenas na OU especificada. NÃO inclui automaticamente:
- Sub-OUs (unidades organizacionais aninhadas)
- OUs pai

**Exemplo:**
```
/Alunos                 ← Selecionado: sincroniza apenas membros diretos
├── /Ano-9             ← NÃO incluído
├── /Ano-10            ← NÃO incluído
└── /Ano-11            ← NÃO incluído
```

**Solução**: Selecione múltiplas OUs ao criar a configuração.

### Propriedade do Grupo

O usuário autenticado deve ter permissão para modificar o grupo de destino:
- Proprietário do grupo
- Administrador do domínio
- Administrador delegado com direitos de gerenciamento de grupo

### Comportamento de Sincronização Subsequente

Após a primeira sincronização, **TODAS as sincronizações subsequentes removerão membros que não estão nas OUs**. Isso é automático e não pode ser desabilitado. Se você precisar preservar membros adicionados manualmente, adicione-os a uma das OUs sincronizadas.

### Grupos Aninhados

A sincronização adiciona usuários diretamente aos grupos, não como grupos aninhados.

## Desempenho

Tempos de sincronização típicos:

- **OUs Pequenas** (< 50 usuários): 5-15 segundos
- **OUs Médias** (50-500 usuários): 15-60 segundos
- **OUs Grandes** (500+ usuários): 1-5 minutos

Fatores que afetam a velocidade:
- Número de usuários nas OUs
- Tamanho atual do grupo
- Tempos de resposta da API
- Latência de rede

## Solução de Problemas

### Erro "Grupo não encontrado"

O grupo especificado não existe ou você não tem acesso.

**Solução:**
1. Verifique se o endereço de email do grupo está correto
2. Deixe a ferramenta criá-lo (se for um grupo novo)
3. Certifique-se de ter permissão para gerenciar o grupo

### Erro "OU não encontrada"

O caminho da unidade organizacional está incorreto.

**Solução:**
1. Verifique se o caminho da OU começa com `/`
2. Verifique o caminho exato da OU no Console de Administração
3. O caminho diferencia maiúsculas de minúsculas
4. Certifique-se de que não há espaços no final

### Nenhum Membro Adicionado

Causas comuns:
- A OU está vazia (sem usuários)
- Todos os usuários já estão no grupo

**Solução:**
1. Verifique se a OU tem usuários no Console de Administração
2. Revise os resultados de sincronização na fila de trabalhos
3. Verifique os logs da aplicação para erros

### Membros Removidos Inesperadamente

Isso acontece em sincronizações subsequentes (após a primeira) porque o sistema reflete a OU exatamente.

**Solução:**
1. Adicione esses usuários a uma das OUs sincronizadas
2. Ou aceite que eles serão removidos e adicione-os manualmente novamente quando necessário
3. Ou não execute sincronizações subsequentes se quiser preservar o grupo como está

### A Configuração de Sincronização Já Existe

Você está tentando criar uma configuração para um grupo que já está configurado.

**Solução:**
1. Use o botão "Ressincronizar" na configuração existente
2. Ou exclua a configuração antiga primeiro

## Considerações de Segurança

### Registro de Auditoria

Todas as mudanças de associação de grupo são registradas:
- Ver em Console de Administração > Relatórios > Auditoria
- Filtrar por eventos de "Configurações do Grupo"
- Rastrear adições/remoções
- Revisar quem acionou sincronizações

### Mudanças Automatizadas

Como as sincronizações subsequentes removem automaticamente membros:
- Documente todas as configurações de sincronização
- Monitore a associação do grupo regularmente
- Revise os resultados de sincronização após cada execução
- Tenha um processo para lidar com preocupações de remoção

### Controle de Acesso

- Limite quem pode acessar o GWorkspace Toolbox
- Monitore quem cria e executa configurações de sincronização
- Revisões de acesso regulares
- Use logs de auditoria para rastrear mudanças

## Uso Avançado

### Múltiplas OUs para Um Grupo

Selecione múltiplas OUs ao criar uma configuração:

```
OUs: /Professores/Primaria, /Professores/Media, /Professores/Secundaria
Grupo: todos-professores@escola.edu

Resultado: Todos os membros do corpo docente em um grupo
```

### Combinando com Aninhamento de Grupos do Google

Use o Console de Administração para aninhar grupos sincronizados:

```
Criar grupos sincronizados separados:
- alunos-primeiro-ano@escola.edu (sincronizado de /Alunos/Ano-9)
- alunos-segundo-ano@escola.edu (sincronizado de /Alunos/Ano-10)

Então aninhá-los no Console de Administração:
- todos-alunos@escola.edu
  ├── alunos-primeiro-ano@ (aninhado)
  └── alunos-segundo-ano@ (aninhado)
```

### Backup e Restauração

Exporte regularmente suas configurações:
1. Clique em "Exportar Todas" para baixar JSON
2. Armazene o arquivo com segurança
3. Importe quando necessário para restaurar configurações

## Próximos Passos

- Revise [Extrator de Alias](/pt/features/alias-extractor)
- Aprenda sobre [Injetor de Atributos](/pt/features/attribute-injector)
- Confira o [FAQ](/pt/faq) para perguntas comuns
