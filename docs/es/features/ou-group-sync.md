# Sincronización de Grupos OU

La función de Sincronización de Grupos OU sincroniza automáticamente usuarios de Unidades Organizativas a Grupos de Google, con configuraciones guardadas que pueden reutilizarse y gestionarse.

![Interfaz de Sincronización de Grupos OU](/screenshots/ou-group-sync.png)

## Resumen

Mantener los Grupos de Google sincronizados con las Unidades Organizativas puede ser tedioso y propenso a errores cuando se hace manualmente. La Sincronización de Grupos OU automatiza este proceso manteniendo configuraciones de sincronización guardadas que puedes ejecutar cuando sea necesario.

## Cómo Funciona

1. **Crear una Configuración de Sincronización**: Selecciona una o más OUs y especifica el Grupo de Google objetivo
2. **Primera Sincronización**: La sincronización inicial solo agrega usuarios al grupo (modo seguro - nunca elimina a nadie)
3. **Sincronizaciones Posteriores**: Las sincronizaciones posteriores reflejan la OU exactamente (agrega nuevos usuarios Y elimina usuarios que ya no están en la OU)
4. **Reutilizar**: Guarda configuraciones y vuelve a sincronizar en cualquier momento con un solo clic

## Entender el Comportamiento de Sincronización

### Primera Sincronización (Automática - Modo Seguro)

Cuando creas una nueva configuración de sincronización y la ejecutas por primera vez:

**Qué hace:**
- Crea el grupo si no existe
- Agrega todos los usuarios de las OUs seleccionadas al grupo
- **Nunca elimina miembros existentes del grupo**
- Seguro para grupos que ya tienen miembros

**Ejemplo:**
```
Miembros OU: estudiante1@, estudiante2@, estudiante3@
Grupo Antes: estudiante1@, profesor@ (agregado manualmente)
Grupo Después: estudiante1@, estudiante2@, estudiante3@, profesor@
Resultado: 2 nuevos estudiantes agregados, profesor@ preservado
```

### Sincronizaciones Posteriores (Automáticas - Modo Espejo)

Cuando haces clic en "Resincronizar" en una configuración existente:

**Qué hace:**
- Compara la membresía actual del grupo con la membresía de la OU
- Agrega usuarios que se unieron a la OU
- **Elimina usuarios que salieron de la OU**
- Hace que el grupo refleje la OU exactamente

**Ejemplo:**
```
Miembros OU: estudiante1@, estudiante2@, estudiante4@ (estudiante3@ transferido, estudiante4@ se unió)
Grupo Antes: estudiante1@, estudiante2@, estudiante3@, profesor@
Grupo Después: estudiante1@, estudiante2@, estudiante4@
Resultado: estudiante4@ agregado, estudiante3@ y profesor@ eliminados
```

⚠️ **Importante**: Después de la primera sincronización, las sincronizaciones posteriores eliminarán miembros que no estén en la OU. El sistema determina automáticamente qué modo de sincronización usar según si es la primera vez que sincronizas esa configuración.

## Configuraciones Guardadas

### Crear una Configuración

1. Haz clic en "+ Nueva Configuración"
2. Selecciona una o más OUs del árbol
3. Ingresa el correo del grupo objetivo (ej., `estudiantes-grado10@escuela.edu`)
4. Opcionalmente proporciona un nombre y descripción del grupo
5. Haz clic en "Sincronizar" para crear la configuración y ejecutar la primera sincronización

### Gestionar Configuraciones

Una vez guardadas, puedes:

- **Resincronizar**: Haz clic en el botón de sincronización para actualizar el grupo con los miembros actuales de la OU
- **Exportar**: Descarga una configuración individual como JSON
- **Eliminar**: Elimina una configuración que ya no necesites
- **Sincronizar Todas**: Ejecuta todas las configuraciones guardadas a la vez

La interfaz muestra:
- Dirección de correo electrónico del grupo
- Número de OUs siendo sincronizadas
- Marca de tiempo de la última sincronización
- Botones de acción rápida para cada configuración

### Exportar e Importar

**Exportar Todas las Configuraciones:**
- Haz clic en "Exportar Todo" para descargar todas las configuraciones guardadas como archivo JSON
- Útil para respaldo o migración a otra instancia

**Importar Configuraciones:**
- Haz clic en "Importar" y selecciona un archivo JSON previamente exportado
- Las configuraciones se agregan (las existentes se omiten)
- Útil para restaurar respaldos o compartir configuraciones

## Casos de Uso Comunes para Escuelas

### Listas de Correo de Clases

Mantener automáticamente grupos de correo electrónico de clases:

```
OUs: /Estudiantes/Grado-10
Grupo: estudiantes-grado10@escuela.edu

Resultado: Todos los estudiantes de 10° grado automáticamente en la lista de correo
Primera sincronización: Agrega todos los estudiantes actuales
Sincronizaciones posteriores: Actualiza cuando los estudiantes se transfieren
```

### Grupos de Departamentos de Facultad

Mantener actualizados los grupos de departamentos de facultad:

```
OUs: /Facultad/Ciencias
Grupo: facultad-ciencias@escuela.edu

Resultado: El grupo siempre refleja el listado actual del departamento de ciencias
Primera sincronización: Agrega toda la facultad de ciencias
Sincronizaciones posteriores: Elimina facultad transferida, agrega nuevas contrataciones
```

### Acceso por Nivel de Grado

Otorgar acceso apropiado a recursos según el grado:

```
OUs: /Estudiantes/Grado-12
Grupo: estudiantes-senior@escuela.edu

Resultado: Los estudiantes de último año obtienen acceso a:
- Cursos de Classroom solo para último año
- Recursos de preparación universitaria
- Materiales de planificación de graduación
```

### Grupos Multi-OU

Combinar múltiples OUs en un grupo:

```
OUs: /Estudiantes/Grado-11, /Estudiantes/Grado-12
Grupo: estudiantes-avanzados@escuela.edu

Resultado: Todos los estudiantes de junior y senior en un grupo para:
- Acceso a cursos avanzados
- Programas de liderazgo estudiantil
- Talleres de preparación universitaria
```

### Grupos de Edificios del Campus

Sincronizar usuarios por campus o edificio físico:

```
OUs: /Facultad/Primaria, /Personal/Primaria
Grupo: campus-primaria@escuela.edu

Resultado: Todo el personal del campus de primaria en el grupo para:
- Anuncios del edificio
- Notificaciones de emergencia
- Acceso a recursos del campus
```

## Mejores Prácticas

### Antes de la Primera Sincronización

Si el grupo ya tiene miembros que quieres mantener:
1. Verifica quién está actualmente en el grupo
2. Asegúrate de que esos usuarios también están en las OUs siendo sincronizadas
3. O ten en cuenta que serán eliminados en sincronizaciones posteriores

### Convenciones de Nomenclatura de Grupos

Usa nomenclatura clara para indicar grupos sincronizados:
- `estudiantes-grado10-auto@escuela.edu` (sincronizado automáticamente)
- `estudiantes-grado10-manual@escuela.edu` (gestionado manualmente)
- Esto ayuda a prevenir confusión sobre qué grupos son gestionados por sincronización

### Documentación

Documenta tus configuraciones de sincronización:
- Qué OUs se sincronizan con qué grupos
- Propósito de cada grupo sincronizado
- Conteos de membresía esperados
- Quién puede activar resincronizaciones

### Resincronización Regular

Programa resincronizaciones regulares (debes activarlas manualmente):
- Semanal: Para grupos dinámicos (grados de estudiantes, nuevas contrataciones)
- Mensual: Para grupos estables (departamentos, edificios)
- Después de cambios mayores: Promociones de nivel de grado, reorganizaciones

## Permisos Requeridos

La Sincronización de Grupos OU requiere estos ámbitos de la API de Google Workspace:

- `https://www.googleapis.com/auth/admin.directory.user.readonly` (leer usuarios de OUs)
- `https://www.googleapis.com/auth/admin.directory.group` (gestionar grupos y membresía)

## Requisitos del Grupo

### Creación del Grupo

La herramienta creará el grupo si no existe, usando:
- La dirección de correo electrónico que especifiques
- El nombre del grupo que proporciones (o derivado del correo)
- La descripción que proporciones (opcional)

### Formato del Correo del Grupo

Debe ser un correo de Grupo de Google válido:
- `estudiantes-grado10@escuela.edu` ✓
- `facultad.ciencias@escuela.edu` ✓
- `club-robotica@escuela.edu` ✓
- `correo-invalido` ✗

### Tipos de Grupos

Funciona con:
- Grupos de Google regulares
- Grupos de seguridad
- Listas de correo
- Grupos de discusión

## Limitaciones

### Alcance de OU

La sincronización opera solo en la OU especificada. NO incluye automáticamente:
- Sub-OUs (unidades organizativas anidadas)
- OUs padre

**Ejemplo:**
```
/Estudiantes              ← Seleccionado: sincroniza solo miembros directos
├── /Grado-9             ← NO incluido
├── /Grado-10            ← NO incluido
└── /Grado-11            ← NO incluido
```

**Solución**: Selecciona múltiples OUs al crear la configuración.

### Propiedad del Grupo

El usuario autenticado debe tener permiso para modificar el grupo objetivo:
- Propietario del grupo
- Administrador del dominio
- Administrador delegado con derechos de gestión de grupos

### Comportamiento de Sincronización Posterior

Después de la primera sincronización, **TODAS las sincronizaciones posteriores eliminarán miembros que no estén en las OUs**. Esto es automático y no se puede deshabilitar. Si necesitas preservar miembros agregados manualmente, agrégalos a una de las OUs sincronizadas.

### Grupos Anidados

La sincronización agrega usuarios directamente a grupos, no como grupos anidados.

## Rendimiento

Tiempos de sincronización típicos:

- **OUs Pequeñas** (< 50 usuarios): 5-15 segundos
- **OUs Medianas** (50-500 usuarios): 15-60 segundos
- **OUs Grandes** (500+ usuarios): 1-5 minutos

Factores que afectan la velocidad:
- Número de usuarios en las OUs
- Tamaño actual del grupo
- Tiempos de respuesta de la API
- Latencia de red

## Solución de Problemas

### Error "Grupo no encontrado"

El grupo especificado no existe o no tienes acceso.

**Solución:**
1. Verifica que la dirección de correo del grupo sea correcta
2. Deja que la herramienta lo cree (si es un grupo nuevo)
3. Asegúrate de tener permiso para gestionar el grupo

### Error "OU no encontrada"

La ruta de la unidad organizativa es incorrecta.

**Solución:**
1. Verifica que la ruta de la OU comience con `/`
2. Verifica la ruta exacta de la OU en la Consola de Administración
3. La ruta distingue mayúsculas y minúsculas
4. Asegúrate de que no haya espacios al final

### No se Agregaron Miembros

Causas comunes:
- La OU está vacía (sin usuarios)
- Todos los usuarios ya están en el grupo

**Solución:**
1. Verifica que la OU tenga usuarios en la Consola de Administración
2. Revisa los resultados de sincronización en la cola de trabajos
3. Verifica los registros de la aplicación para errores

### Miembros Eliminados Inesperadamente

Esto ocurre en sincronizaciones posteriores (después de la primera) porque el sistema refleja la OU exactamente.

**Solución:**
1. Agrega esos usuarios a una de las OUs sincronizadas
2. O acepta que serán eliminados y vuelve a agregarlos manualmente cuando sea necesario
3. O no ejecutes sincronizaciones posteriores si quieres preservar el grupo tal como está

### La Configuración de Sincronización Ya Existe

Estás intentando crear una configuración para un grupo que ya está configurado.

**Solución:**
1. Usa el botón "Resincronizar" en la configuración existente
2. O elimina la configuración antigua primero

## Consideraciones de Seguridad

### Registro de Auditoría

Todos los cambios de membresía de grupo se registran:
- Ver en Consola de Administración > Informes > Auditoría
- Filtrar por eventos de "Configuración de Grupo"
- Rastrear adiciones/eliminaciones
- Revisar quién activó sincronizaciones

### Cambios Automatizados

Como las sincronizaciones posteriores eliminan automáticamente miembros:
- Documenta todas las configuraciones de sincronización
- Monitorea la membresía del grupo regularmente
- Revisa los resultados de sincronización después de cada ejecución
- Ten un proceso para manejar preocupaciones de eliminación

### Control de Acceso

- Limita quién puede acceder a GWorkspace Toolbox
- Monitorea quién crea y ejecuta configuraciones de sincronización
- Revisiones de acceso regulares
- Usa registros de auditoría para rastrear cambios

## Uso Avanzado

### Múltiples OUs a Un Grupo

Selecciona múltiples OUs al crear una configuración:

```
OUs: /Facultad/Primaria, /Facultad/Media, /Facultad/Secundaria
Grupo: toda-facultad@escuela.edu

Resultado: Todos los miembros de la facultad en un grupo
```

### Combinando con Anidación de Grupos de Google

Usa la Consola de Administración para anidar grupos sincronizados:

```
Crear grupos sincronizados separados:
- estudiantes-primer-ano@escuela.edu (sincronizado de /Estudiantes/Grado-9)
- estudiantes-segundo-ano@escuela.edu (sincronizado de /Estudiantes/Grado-10)

Luego anidarlos en la Consola de Administración:
- todos-estudiantes@escuela.edu
  ├── estudiantes-primer-ano@ (anidado)
  └── estudiantes-segundo-ano@ (anidado)
```

### Respaldo y Restauración

Exporta regularmente tus configuraciones:
1. Haz clic en "Exportar Todo" para descargar JSON
2. Almacena el archivo de forma segura
3. Importa cuando sea necesario para restaurar configuraciones

## Próximos Pasos

- Revisa [Extractor de Alias](/es/features/alias-extractor)
- Aprende sobre [Inyector de Atributos](/es/features/attribute-injector)
- Consulta las [Preguntas Frecuentes](/es/faq) para preguntas comunes
