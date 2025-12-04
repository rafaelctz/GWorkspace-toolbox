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

La función de Sincronización de Grupos OU agrega automáticamente usuarios de una Unidad Organizativa a un Grupo de Google.

### Pasos

1. Haz clic en **Sincronización de Grupos OU** en la barra lateral
2. Ingresa la ruta de la **Unidad Organizativa** (ej., `/Facultad`)
3. Ingresa el **Correo del Grupo Objetivo** (ej., `equipo-marketing@escuela.edu`)
4. Elige el modo de sincronización:
   - **Sincronización Inteligente**: Solo agrega nuevos miembros (preserva usuarios agregados manualmente)
   - **Sincronización Completa**: Refleja la OU exactamente (elimina usuarios que no están en la OU)
5. Opcionalmente habilita **Programar Sincronización** para sincronización automática diaria
6. Haz clic en **Sincronizar Ahora** para ejecutar inmediatamente

### Sincronización Inteligente vs Sincronización Completa

**Sincronización Inteligente** (Recomendada):
- Agrega usuarios de la OU al grupo
- Nunca elimina a nadie del grupo
- Seguro para grupos con miembros gestionados manualmente
- Mejor para la mayoría de casos de uso

**Sincronización Completa**:
- La membresía del grupo coincide exactamente con la OU
- Elimina usuarios que no están en la OU
- Usar solo si el grupo debe reflejar la OU exactamente
- Cuidado: eliminará miembros agregados manualmente

### Programación

Habilita **Programar Sincronización** para ejecutar automáticamente la sincronización diariamente a medianoche. La programación persiste a través de reinicios de la aplicación.

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
- Usa el modo de Sincronización Inteligente a menos que específicamente necesites Sincronización Completa
- Exporta y revisa archivos CSV antes de hacer cambios masivos

### Monitoreo
- Verifica los logs de Docker para cualquier error: `docker-compose logs -f`
- Monitorea el estado de trabajos de sincronización en la interfaz de Sincronización de Grupos OU
- Revisa regularmente el historial de sincronización programada

## Próximos Pasos

- Explora la [Documentación Detallada de Características](/es/features)
- Revisa el [FAQ](/es/faq) para preguntas comunes
- Consulta [Solución de Problemas](/es/troubleshooting) si encuentras problemas

## Obteniendo Ayuda

¿Necesitas asistencia?
- Consulta el [FAQ](/es/faq)
- Visita [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Revisa la [Guía de Solución de Problemas](/es/troubleshooting)
