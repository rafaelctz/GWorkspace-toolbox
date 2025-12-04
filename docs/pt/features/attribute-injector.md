# Injetor de Atributos

O Injetor de Atributos permite injetar atributos personalizados em lote para todos os usuários dentro de uma Unidade Organizacional especificada, economizando horas de trabalho manual.


![Feature Screenshot](/screenshots/attribute-injector.png)

## Visão Geral

O Google Workspace suporta atributos de usuário personalizados através de esquemas personalizados. O Injetor de Atributos facilita a aplicação desses atributos a todos os usuários em uma OU de uma vez, em vez de atualizar manualmente cada usuário individualmente.

## Como Funciona

1. **Selecionar OU Alvo**: Digite o caminho da unidade organizacional (ex., `/Estudantes/Ano-10`)
2. **Especificar Atributo**: Digite o nome do atributo personalizado do seu esquema
3. **Definir Valor**: Digite o valor para atribuir a todos os usuários (ex., "aluno", "professor", "funcionario")
4. **Injetar**: Clique em "Injetar Atributos" para aplicar alterações
5. **Revisar Resultados**: Veja quantos usuários foram atualizados com sucesso

## Pré-requisitos

### Esquema Personalizado Necessário
Antes de usar o Injetor de Atributos, você deve criar um esquema personalizado no Google Workspace:

1. Vá para [Google Admin Console](https://admin.google.com)
2. Navegue para **Directory** > **Users** > **Manage custom attributes**
3. Clique em **Add Custom Attribute**
4. Crie seu esquema (ex., "InfoEscolar")
5. Adicione campos (ex., "funcao", "serie", "predio", "idAluno")

## Formato de Nome de Atributo

Os atributos são especificados no formato: `NomeEsquema.NomeCampo`

**Exemplos Simples:**
- `InfoEscolar.funcao` com valores como: `aluno`, `professor`, `funcionario`, `admin`
- `InfoEscolar.serie` com valores como: `1`, `2`, `9`, `Maternal`, `Graduado`
- `InfoEscolar.predio` com valores como: `Principal`, `Norte`, `Sul`

**Importante:** Você pode usar valores de texto simples como "aluno" ou "professor" - não são necessários códigos complexos!

## Casos de Uso Comuns para Escolas

### Atribuir Funções de Usuário
Identificar usuários por sua função na escola.

```
OU: /Professores/Ciencias
Atributo: InfoEscolar.funcao
Valor: professor
```

### Definir Séries
Marcar alunos pela série atual.

```
OU: /Estudantes/Ano-9
Atributo: InfoEscolar.serie
Valor: 9
```

### Atribuição de Prédio
Rastrear a qual prédio ou campus os usuários pertencem.

```
OU: /Estudantes/Fundamental
Atributo: InfoEscolar.predio
Valor: Campus Fundamental
```

### Classificação de Funcionários
Marcar usuários por tipo de funcionário para aplicação de políticas.

```
OU: /Contratados
Atributo: InfoEscolar.tipoFuncionario
Valor: Contratado
```

## Melhores Práticas

### Testar em OUs Pequenas Primeiro
Antes de aplicar atributos a OUs grandes:
1. Teste em uma OU de teste pequena com 2-3 usuários
2. Verifique se o atributo aparece corretamente no Admin Console
3. Em seguida, prossiga com OUs maiores

### Usar OUs Hierárquicas
Organize sua estrutura de OU para corresponder às suas necessidades de atributos.

### Documentar seu Esquema
Mantenha documentação de:
- Nomes e campos de esquemas personalizados
- Significado de cada atributo
- Valores válidos para cada campo
- Quais OUs usam quais atributos

## Solução de Problemas

### Erro "Atributo não encontrado"
O atributo especificado não existe no seu esquema personalizado.

**Solução:**
1. Vá para Admin Console > Directory > Users > Manage custom attributes
2. Verifique se o esquema e campo existem
3. Use o formato exato: `NomeEsquema.nomeCampo`

### Erro "OU não encontrada"
O caminho da unidade organizacional está incorreto.

**Solução:**
1. Verifique se o formato do caminho da OU começa com `/`
2. Verifique se a OU existe no Admin Console
3. Use o caminho exato (sensível a maiúsculas)

## Próximos Passos

- Aprenda sobre [Sincronização de Grupos OU](/pt/features/ou-group-sync)
- Revise [Extrator de Alias](/pt/features/alias-extractor)
- Confira o [FAQ](/pt/faq) para perguntas comuns
