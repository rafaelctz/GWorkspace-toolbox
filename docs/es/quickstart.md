# Guía de Inicio Rápido

Esta guía te guiará a través del uso de las características de GWorkspace Toolbox por primera vez.

## Requisitos Previos

- GWorkspace Toolbox instalado y en ejecución
- Autenticado con tu cuenta de administrador de Google Workspace

## Extrayendo Alias de Usuario

El Extractor de Alias te permite exportar todos los alias de usuario de tu dominio a un archivo CSV.

### Pasos

1. Abre GWorkspace Toolbox en `http://localhost:8000`
2. Haz clic en **Extractor de Alias** en la barra lateral
3. Asegúrate de estar autenticado (indicador verde en la esquina superior derecha)
4. Haz clic en el botón **Extraer Aliases**
5. Espera a que se complete la extracción
6. Descarga el archivo CSV generado

### Lo que Obtienes

El archivo CSV contiene:
- Correo electrónico principal del usuario
- Dirección de correo electrónico de alias
- Una fila por alias

### Casos de Uso

- Auditar todos los alias de correo electrónico en tu dominio
- Planificar migraciones de correo electrónico
- Documentar el enrutamiento de correo actual
- Informes de cumplimiento

## Inyectando Atributos Personalizados

El Inyector de Atributos te permite agregar atributos personalizados en lote a usuarios en Unidades Organizativas específicas.

### Pasos

1. Haz clic en **Inyector de Atributos** en la barra lateral
2. Ingresa o selecciona la ruta de la **Unidad Organizativa** objetivo (ej., `/Ventas/Regional`)
3. Ingresa el **Nombre del Atributo** (campo de esquema personalizado)
4. Ingresa el **Valor del Atributo** para asignar
5. Haz clic en el botón **Inyectar Atributos**
6. Revisa los resultados mostrando cuántos usuarios fueron actualizados

### Casos de Uso

- Asignar códigos de departamento a todos los usuarios en una OU
- Establecer tipos de empleado para filtrado organizacional
- Agregar información de centro de costos para informes
- Aplicar cualquier atributo personalizado a escala

## Sincronizando OU a Grupos

La característica de Sincronización de Grupos OU sincroniza automáticamente usuarios de Unidades Organizativas a Grupos de Google con configuraciones guardadas.

### Pasos

1. Haz clic en **Sincronización de Grupos OU** en la barra lateral
2. Haz clic en **+ Nueva Configuración**
3. Selecciona una o más **Unidades Organizativas** del árbol (ej., `/Estudiantes/Grado-10`)
4. Ingresa el **Correo del Grupo Objetivo** (ej., `estudiantes-grado10@escuela.edu`)
5. Opcionalmente proporciona un nombre y descripción del grupo
6. Haz clic en **Sincronizar** para crear la configuración y ejecutar la primera sincronización

### Cómo Funciona la Sincronización

**Primera Sincronización (Automática - Modo Seguro):**
- Crea el grupo si no existe
- Agrega todos los usuarios de las OUs seleccionadas al grupo
- **Nunca elimina miembros existentes del grupo**
- Seguro para grupos que ya tienen miembros

**Sincronizaciones Posteriores (Automáticas - Modo Espejo):**
- Cuando haces clic en "Resincronizar" en una configuración guardada
- Agrega usuarios que se unieron a la OU
- **Elimina usuarios que salieron de la OU**
- Hace que el grupo refleje la OU exactamente

⚠️ **Importante**: El sistema automáticamente usa modo seguro para la primera sincronización, luego cambia a modo espejo para todas las sincronizaciones posteriores. No puedes elegir manualmente el modo de sincronización - se determina por si es la primera vez sincronizando esa configuración.

### Gestión de Configuraciones

Después de crear una configuración, puedes:
- **Resincronizar**: Actualiza el grupo con los miembros actuales de la OU
- **Sincronizar Todo**: Ejecuta todas las configuraciones guardadas a la vez
- **Exportar**: Descarga configuraciones para respaldo
- **Importar**: Restaura configuraciones desde respaldo
- **Eliminar**: Elimina configuraciones que ya no necesites

## Selección de Idioma

GWorkspace Toolbox soporta tres idiomas. Cambia el idioma usando el menú desplegable en la esquina superior derecha:

- English (EN)
- Español (ES)
- Português (PT)

Tu preferencia de idioma se guarda automáticamente.

## Mejores Prácticas

### Seguridad
- Siempre usa cuentas de administrador con los privilegios mínimos requeridos
- Revisa los permisos OAuth antes de otorgar acceso
- Mantén el archivo credentials.json seguro y nunca lo subas al control de versiones

### Pruebas
- Prueba operaciones en OUs pequeñas primero
- Revisa la membresía del grupo antes de ejecutar sincronizaciones posteriores (eliminarán miembros que no estén en la OU)
- Exporta y revisa archivos CSV antes de hacer cambios masivos

### Monitoreo
- Verifica los logs de Docker para cualquier error: `docker-compose logs -f`
- Monitorea el estado de trabajos de sincronización en la interfaz de Sincronización de Grupos OU
- Revisa regularmente las marcas de tiempo de última sincronización en las configuraciones guardadas

## Próximos Pasos

- Explora la [Documentación Detallada de Características](/es/features)
- Revisa el [FAQ](/es/faq) para preguntas comunes
- Consulta [Solución de Problemas](/es/troubleshooting) si encuentras problemas

## Obteniendo Ayuda

¿Necesitas asistencia?
- Consulta el [FAQ](/es/faq)
- Visita [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Revisa la [Guía de Solución de Problemas](/es/troubleshooting)
