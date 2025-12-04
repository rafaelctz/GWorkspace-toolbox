# Sincronização de Grupos OU

O recurso de Sincronização de Grupos OU sincroniza automaticamente usuários de uma Unidade Organizacional para um Grupo do Google, com capacidades de sincronização inteligente e opções de agendamento.

## Visão Geral

Manter os Grupos do Google sincronizados com Unidades Organizacionais pode ser demorado e propenso a erros quando feito manualmente. A Sincronização de Grupos OU automatiza este processo, garantindo que os grupos sempre reflitam suas OUs correspondentes.

## Como Funciona

1. **Especificar OU**: Digite o caminho da unidade organizacional (ex., `/Marketing`)
2. **Selecionar Grupo Alvo**: Digite o e-mail do Grupo do Google (ex., `equipe-marketing@empresa.com`)
3. **Escolher Modo de Sincronização**: Sincronização Inteligente ou Sincronização Completa
4. **Agendamento Opcional**: Habilite sincronização automática diária
5. **Sincronizar**: Clique em "Sincronizar Agora" ou deixe o agendamento lidar com isso

## Modos de Sincronização

### Sincronização Inteligente (Recomendada)

**O que faz:**
- Adiciona todos os usuários da OU ao grupo
- **Nunca remove** membros do grupo
- Preserva membros adicionados manualmente

**Melhor para:**
- Grupos com uma mistura de membros baseados em OU e gerenciados manualmente
- Garantir que ninguém seja removido acidentalmente
- Adição unidirecional de membros
- Casos de uso mais comuns

**Exemplo:**
```
Membros OU: alice@, bob@, carlos@
Grupo Antes: alice@, david@ (adicionado manualmente)
Grupo Depois: alice@, bob@, carlos@, david@
```

### Sincronização Completa

**O que faz:**
- Faz a associação do grupo corresponder exatamente à OU
- Adiciona usuários da OU
- **Remove usuários NÃO na OU**

**Melhor para:**
- Grupos que devem espelhar uma OU exatamente
- Grupos de permissões automatizados
- Quando você quer mapeamento estrito OU-para-grupo

**Exemplo:**
```
Membros OU: alice@, bob@, carlos@
Grupo Antes: alice@, david@ (adicionado manualmente)
Grupo Depois: alice@, bob@, carlos@
Resultado: david@ foi removido
```

⚠️ **Aviso**: A Sincronização Completa removerá membros adicionados manualmente. Use apenas quando quiser que o grupo corresponda exatamente à OU.

## Agendamento

### Habilitar Sincronização Agendada

Ative "Agendar Sincronização" para habilitar sincronização automática diária:

- Executa diariamente à meia-noite (hora local do servidor)
- Usa o modo de sincronização que você especificou
- Persiste através de reinicializações da aplicação
- Armazenado em banco de dados SQLite

## Casos de Uso Comuns

### Grupos de Acesso Departamental

Conceder automaticamente acesso departamental a recursos:

```
OU: /Vendas
Grupo: departamento-vendas@empresa.com
Modo: Sincronização Inteligente
Agendamento: Habilitado

Resultado: Todos os membros da equipe de vendas obtêm automaticamente acesso a:
- Drives compartilhados
- Sites internos
- Recursos departamentais
```

### Listas de E-mail de Equipe

Manter listas de e-mail de equipe automaticamente:

```
OU: /Engenharia/Backend
Grupo: equipe-backend@empresa.com
Modo: Sincronização Completa
Agendamento: Habilitado

Resultado: O grupo sempre reflete a lista atual da equipe backend
```

## Melhores Práticas

### Escolher o Modo de Sincronização Correto

| Cenário | Modo Recomendado |
|---------|------------------|
| O grupo tem apenas membros de OU | Sincronização Completa |
| O grupo também tem membros externos | Sincronização Inteligente |
| Controle de acesso estrito necessário | Sincronização Completa |
| Adicionando membros de OU a grupo existente | Sincronização Inteligente |
| Não tem certeza qual usar | Sincronização Inteligente (mais segura) |

### Documentação

Documente suas configurações de sincronização:
- Quais OUs sincronizam com quais grupos
- Modo de sincronização usado para cada um
- Propósito de cada grupo sincronizado
- Contagens de associação esperadas

### Testes

Antes de habilitar Sincronização Completa:
1. Verifique a associação atual do grupo
2. Identifique quaisquer membros adicionados manualmente
3. Decida se eles devem permanecer
4. Considere Sincronização Inteligente se não tiver certeza

## Solução de Problemas

### Erro "Grupo não encontrado"

O grupo especificado não existe ou você não tem acesso.

**Solução:**
1. Verifique se o endereço de e-mail do grupo está correto
2. Verifique se o grupo existe no Admin Console
3. Certifique-se de ter permissão para gerenciar o grupo

### Erro "OU não encontrada"

O caminho da unidade organizacional está incorreto.

**Solução:**
1. Verifique se o caminho da OU começa com `/`
2. Verifique o caminho exato da OU no Admin Console
3. O caminho é sensível a maiúsculas

### O Agendamento Não Está Sendo Executado

**Solução:**
1. Verifique se o agendamento está habilitado (o botão deve estar ativado)
2. Verifique se o contêiner Docker está executando continuamente
3. Verifique os logs: `docker-compose logs -f`

## Próximos Passos

- Revise [Extrator de Alias](/pt/features/alias-extractor)
- Aprenda sobre [Injetor de Atributos](/pt/features/attribute-injector)
- Confira o [FAQ](/pt/faq) para perguntas comuns
