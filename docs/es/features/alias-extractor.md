# Extractor de Alias

La característica Extractor de Alias te permite exportar todos los alias de correo electrónico de tu dominio de Google Workspace a un archivo CSV con un solo clic.


![Feature Screenshot](/screenshots/alias-extractor.png)

## Resumen

Los alias de correo electrónico son direcciones de correo alternativas que entregan al buzón principal de un usuario. Gestionar y rastrear estos alias en una organización grande puede ser desafiante. El Extractor de Alias automatiza este proceso, dándote visibilidad completa de todos los alias en tu dominio.

## Cómo Funciona

1. **Autenticar**: Asegúrate de estar autenticado con credenciales de administrador
2. **Hacer Clic en Extraer**: Presiona el botón "Extraer Aliases"
3. **Procesamiento**: La herramienta consulta Google Workspace para todos los usuarios y sus alias
4. **Descargar**: Recibe un archivo CSV con toda la información de alias

## Formato de Salida CSV

El archivo CSV generado contiene las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Primary Email | Dirección de correo principal del usuario | juan.perez@escuela.edu |
| Alias | La dirección de correo del alias | j.perez@escuela.edu |

### Ejemplo de Salida CSV
```csv
Primary Email,Alias
juan.perez@escuela.edu,j.perez@escuela.edu
juan.perez@escuela.edu,jperez@escuela.edu
maria.garcia@escuela.edu,m.garcia@escuela.edu
```

## Casos de Uso

### Planificación de Migración de Correo
Antes de migrar a un nuevo sistema de correo, exporta todos los alias para asegurar que se preserven en el proceso de migración.

### Auditoría de Cumplimiento
Genera informes regulares de todos los alias de correo para auditorías de cumplimiento y seguridad.

### Documentación
Mantén documentación actualizada del enrutamiento de correo y configuración de alias.

### Operaciones de Limpieza
Identifica alias no utilizados o redundantes para limpieza y optimización.

## Rendimiento

- **Dominios pequeños** (< 100 usuarios): ~10-30 segundos
- **Dominios medianos** (100-1,000 usuarios): ~30-90 segundos
- **Dominios grandes** (1,000+ usuarios): Varios minutos

La herramienta procesa usuarios en lotes y muestra el progreso en tiempo real.

## Permisos Requeridos

El Extractor de Alias requiere los siguientes permisos de Google Workspace:

- `https://www.googleapis.com/auth/admin.directory.user.readonly`

Este permiso de solo lectura permite a la aplicación:
- Listar todos los usuarios en el dominio
- Leer alias de correo de usuarios
- Sin capacidades de escritura o modificación

## Solución de Problemas

### No se Encontraron Alias
Si el CSV está vacío o faltan alias esperados:
- Verifica que estés autenticado como administrador de dominio
- Verifica que los usuarios realmente tengan alias configurados
- Asegúrate de que Admin SDK API esté habilitado en Google Cloud Console

### Errores de Tiempo de Espera
Para dominios muy grandes:
- La operación puede tomar varios minutos
- Asegura una conexión estable a internet
- Verifica que el contenedor Docker tenga suficientes recursos

## Próximos Pasos

- Aprende sobre [Inyector de Atributos](/es/features/attribute-injector)
- Explora [Sincronización de Grupos OU](/es/features/ou-group-sync)
- Lee el [FAQ](/es/faq)
