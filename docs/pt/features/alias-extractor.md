# Extrator de Alias

O recurso Extrator de Alias permite exportar todos os alias de e-mail do seu domínio Google Workspace para um arquivo CSV com um único clique.


![Feature Screenshot](/screenshots/alias-extractor.png)

## Visão Geral

Alias de e-mail são endereços de e-mail alternativos que entregam para a caixa de entrada principal de um usuário. Gerenciar e rastrear esses alias em uma grande organização pode ser desafiador. O Extrator de Alias automatiza este processo, dando-lhe visibilidade completa de todos os alias no seu domínio.

## Como Funciona

1. **Autenticar**: Certifique-se de estar autenticado com credenciais de administrador
2. **Clicar em Extrair**: Pressione o botão "Extrair Aliases"
3. **Processamento**: A ferramenta consulta o Google Workspace para todos os usuários e seus alias
4. **Baixar**: Receba um arquivo CSV com todas as informações de alias

## Formato de Saída CSV

O arquivo CSV gerado contém as seguintes colunas:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| Primary Email | Endereço de e-mail principal do usuário | joao.silva@escola.edu |
| Alias | O endereço de e-mail do alias | j.silva@escola.edu |

### Exemplo de Saída CSV
```csv
Primary Email,Alias
joao.silva@escola.edu,j.silva@escola.edu
joao.silva@escola.edu,jsilva@escola.edu
maria.santos@escola.edu,m.santos@escola.edu
```

## Casos de Uso

### Planejamento de Migração de E-mail
Antes de migrar para um novo sistema de e-mail, exporte todos os alias para garantir que sejam preservados no processo de migração.

### Auditoria de Conformidade
Gere relatórios regulares de todos os alias de e-mail para auditorias de conformidade e segurança.

### Documentação
Mantenha documentação atualizada do roteamento de e-mail e configuração de alias.

### Operações de Limpeza
Identifique alias não utilizados ou redundantes para limpeza e otimização.

## Desempenho

- **Domínios pequenos** (< 100 usuários): ~10-30 segundos
- **Domínios médios** (100-1.000 usuários): ~30-90 segundos
- **Domínios grandes** (1.000+ usuários): Vários minutos

A ferramenta processa usuários em lotes e mostra o progresso em tempo real.

## Permissões Necessárias

O Extrator de Alias requer as seguintes permissões do Google Workspace:

- `https://www.googleapis.com/auth/admin.directory.user.readonly`

Esta permissão somente leitura permite que a aplicação:
- Liste todos os usuários no domínio
- Leia alias de e-mail de usuários
- Sem capacidades de escrita ou modificação

## Solução de Problemas

### Nenhum Alias Encontrado
Se o CSV estiver vazio ou faltando alias esperados:
- Verifique se você está autenticado como administrador de domínio
- Verifique se os usuários realmente têm alias configurados
- Certifique-se de que o Admin SDK API está habilitado no Google Cloud Console

### Erros de Tempo Limite
Para domínios muito grandes:
- A operação pode levar vários minutos
- Garanta uma conexão estável à internet
- Verifique se o contêiner Docker tem recursos suficientes

## Próximos Passos

- Aprenda sobre [Injetor de Atributos](/pt/features/attribute-injector)
- Explore [Sincronização de Grupos OU](/pt/features/ou-group-sync)
- Leia o [FAQ](/pt/faq)
