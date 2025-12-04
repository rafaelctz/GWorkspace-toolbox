# Sincronización de Grupos OU

La característica de Sincronización de Grupos OU sincroniza automáticamente usuarios de una Unidad Organizativa a un Grupo de Google, con capacidades de sincronización inteligente y opciones de programación.


![Feature Screenshot](/screenshots/ou-group-sync.png)

## Resumen

Mantener los Grupos de Google sincronizados con Unidades Organizativas puede ser tedioso y propenso a errores cuando se hace manualmente. La Sincronización de Grupos OU automatiza este proceso, asegurando que los grupos siempre reflejen sus OUs correspondientes.

## Cómo Funciona

1. **Especificar OU**: Ingresa la ruta de la unidad organizativa (ej., `/Facultad`)
2. **Seleccionar Grupo Objetivo**: Ingresa el correo del Grupo de Google (ej., `equipo-marketing@escuela.edu`)
3. **Elegir Modo de Sincronización**: Sincronización Inteligente o Sincronización Completa
4. **Programación Opcional**: Habilita sincronización automática diaria
5. **Sincronizar**: Haz clic en "Sincronizar Ahora" o deja que la programación lo maneje

## Modos de Sincronización

### Sincronización Inteligente (Recomendada)

**Qué hace:**
- Agrega todos los usuarios de la OU al grupo
- **Nunca elimina** miembros del grupo
- Preserva miembros agregados manualmente

**Mejor para:**
- Grupos con una mezcla de miembros basados en OU y gestionados manualmente
- Asegurar que nadie sea eliminado accidentalmente
- Adición unidireccional de miembros
- Casos de uso más comunes

**Ejemplo:**
```
Miembros OU: alicia@, bob@, carlos@
Grupo Antes: alicia@, david@ (agregado manualmente)
Grupo Después: alicia@, bob@, carlos@, david@
```

### Sincronización Completa

**Qué hace:**
- Hace que la membresía del grupo coincida exactamente con la OU
- Agrega usuarios de la OU
- **Elimina usuarios NO en la OU**

**Mejor para:**
- Grupos que deben reflejar una OU exactamente
- Grupos de permisos automatizados
- Cuando quieres mapeo estricto OU-a-grupo

**Ejemplo:**
```
Miembros OU: alicia@, bob@, carlos@
Grupo Antes: alicia@, david@ (agregado manualmente)
Grupo Después: alicia@, bob@, carlos@
Resultado: david@ fue eliminado
```

⚠️ **Advertencia**: La Sincronización Completa eliminará miembros agregados manualmente. Úsala solo cuando quieras que el grupo coincida exactamente con la OU.

## Programación

### Habilitar Sincronización Programada

Activa "Programar Sincronización" para habilitar sincronización automática diaria:

- Se ejecuta diariamente a medianoche (hora local del servidor)
- Usa el modo de sincronización que especificaste
- Persiste a través de reinicios de la aplicación
- Almacenado en base de datos SQLite

## Casos de Uso Comunes

### Grupos de Acceso Departamental

Otorgar automáticamente acceso departamental a recursos:

```
OU: /Ventas
Grupo: departamento-ventas@escuela.edu
Modo: Sincronización Inteligente
Programación: Habilitada

Resultado: Todos los miembros del equipo de ventas obtienen automáticamente acceso a:
- Drives compartidos
- Sitios internos
- Recursos departamentales
```

### Listas de Correo de Equipo

Mantener listas de correo de equipo automáticamente:

```
OU: /Ingenieria/Backend
Grupo: equipo-backend@escuela.edu
Modo: Sincronización Completa
Programación: Habilitada

Resultado: El grupo siempre refleja la lista actual del equipo backend
```

## Mejores Prácticas

### Elegir el Modo de Sincronización Correcto

| Escenario | Modo Recomendado |
|-----------|------------------|
| El grupo solo tiene miembros de OU | Sincronización Completa |
| El grupo también tiene miembros externos | Sincronización Inteligente |
| Se necesita control de acceso estricto | Sincronización Completa |
| Agregando miembros de OU a grupo existente | Sincronización Inteligente |
| No estás seguro cuál usar | Sincronización Inteligente (más segura) |

### Documentación

Documenta tus configuraciones de sincronización:
- Qué OUs se sincronizan con qué grupos
- Modo de sincronización usado para cada uno
- Propósito de cada grupo sincronizado
- Conteos de membresía esperados

### Pruebas

Antes de habilitar Sincronización Completa:
1. Verifica la membresía actual del grupo
2. Identifica cualquier miembro agregado manualmente
3. Decide si deben permanecer
4. Considera Sincronización Inteligente si no estás seguro

## Solución de Problemas

### Error "Grupo no encontrado"

El grupo especificado no existe o careces de acceso.

**Solución:**
1. Verifica que la dirección de correo del grupo sea correcta
2. Verifica que el grupo exista en Admin Console
3. Asegúrate de tener permiso para gestionar el grupo

### Error "OU no encontrada"

La ruta de la unidad organizativa es incorrecta.

**Solución:**
1. Verifica que la ruta de OU comience con `/`
2. Verifica la ruta exacta de OU en Admin Console
3. La ruta es sensible a mayúsculas

### La Programación No Se Está Ejecutando

**Solución:**
1. Verifica que la programación esté habilitada (el interruptor debe estar activado)
2. Verifica que el contenedor Docker esté ejecutándose continuamente
3. Verifica los logs: `docker-compose logs -f`

## Próximos Pasos

- Revisa [Extractor de Alias](/es/features/alias-extractor)
- Aprende sobre [Inyector de Atributos](/es/features/attribute-injector)
- Consulta el [FAQ](/es/faq) para preguntas comunes
