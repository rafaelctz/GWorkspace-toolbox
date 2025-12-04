# Preguntas Frecuentes

Preguntas y respuestas comunes sobre GWorkspace Toolbox.

## General

### ¿Qué es GWorkspace Toolbox?

GWorkspace Toolbox es un conjunto gratuito y de código abierto de herramientas diseñado para ayudar a los administradores de Google Workspace a automatizar tareas administrativas comunes como gestionar alias de correo, atributos de usuario y membresías de grupos.

### ¿Es gratuito GWorkspace Toolbox?

Sí, GWorkspace Toolbox es completamente gratuito y de código abierto bajo la Licencia MIT. No hay características premium ni niveles pagos.

### ¿Qué edición de Google Workspace necesito?

GWorkspace Toolbox funciona con todas las ediciones de Google Workspace (Business Starter, Business Standard, Business Plus, Enterprise) siempre que tengas acceso de administrador.

### ¿Puedo usar esto con una cuenta de Gmail gratuita?

No, GWorkspace Toolbox requiere un dominio de Google Workspace (anteriormente G Suite) con acceso de administrador. Usa el Admin SDK API que no está disponible para cuentas personales de Gmail.

## Instalación y Configuración

### ¿Necesito habilidades técnicas para instalar GWorkspace Toolbox?

Familiaridad básica con Docker y línea de comandos es útil, pero la instalación es sencilla. Sigue la [Guía de Instalación](/es/installation) paso a paso.

### ¿Puedo ejecutar esto en Windows?

Sí, GWorkspace Toolbox se ejecuta en Windows, macOS y Linux usando Docker Desktop.

### ¿Necesito un servidor para ejecutar GWorkspace Toolbox?

No, puedes ejecutarlo en tu computadora local. Sin embargo, para que las sincronizaciones programadas funcionen continuamente, necesitarás una máquina que permanezca encendida (servidor local, VPS o instancia en la nube).

### ¿Qué puertos usa GWorkspace Toolbox?

Por defecto, usa el puerto 8000. Puedes cambiarlo en el archivo `docker-compose.yml` si es necesario.

### ¿Dónde se almacenan mis datos?

Todos los datos se almacenan localmente:
- Tokens de autenticación: archivo `token.json`
- Programaciones de sincronización: base de datos SQLite en directorio `./database`
- Exportaciones CSV: directorio `./exports`

No se envían datos a servidores externos excepto las APIs de Google.

## Autenticación y Seguridad

### ¿Están seguros mis datos de Google Workspace?

Sí. GWorkspace Toolbox usa autenticación OAuth 2.0 y solo solicita los permisos mínimos requeridos. Tus credenciales se almacenan localmente y nunca se transmiten a terceros.

### ¿Qué permisos necesita GWorkspace Toolbox?

La herramienta solicita:
- Acceso de lectura a usuarios del directorio (para Extractor de Alias, Sincronización de Grupos OU)
- Acceso de escritura a usuarios del directorio (para Inyector de Atributos)
- Gestionar grupos (para Sincronización de Grupos OU)

### ¿Puedo revocar el acceso?

Sí, puedes revocar el acceso en cualquier momento:
1. Ve a [Permisos de Cuenta de Google](https://myaccount.google.com/permissions)
2. Encuentra GWorkspace Toolbox
3. Haz clic en "Eliminar Acceso"

### ¿Necesito ser superadministrador?

Sí, la mayoría de las características requieren privilegios de superadministrador. Algunas características pueden funcionar con roles de administrador delegado que tengan permisos apropiados.

## Características

### ¿Puede el Extractor de Alias exportar alias solo para OUs específicas?

Actualmente, el Extractor de Alias exporta alias para todos los usuarios en el dominio. Puedes filtrar el archivo CSV después por dirección de correo principal para obtener usuarios de OUs específicas.

### ¿Funciona el Inyector de Atributos con campos estándar de Google?

No, el Inyector de Atributos solo funciona con atributos de esquema personalizado. Los campos estándar como nombre, teléfono o título de trabajo deben gestionarse a través de Admin Console.

### ¿Puedo sincronizar múltiples OUs a un grupo?

Sí, puedes crear múltiples trabajos de sincronización que todos apunten al mismo grupo. Usa el modo de Sincronización Inteligente para asegurar que los usuarios de todas las OUs se agreguen sin eliminarse entre sí.

## Solución de Problemas

### La aplicación no inicia

Verifica:
1. Docker está ejecutándose: `docker ps`
2. El puerto 8000 no está en uso por otra aplicación
3. El archivo Docker Compose está presente
4. Ejecuta `docker-compose logs` para ver mensajes de error

### No puedo autenticarme

Asegúrate de que:
1. El archivo credentials.json esté en el directorio del proyecto
2. El URI de redirección del cliente OAuth incluye `http://localhost:8000/oauth2callback`
3. Admin SDK API esté habilitado en Google Cloud Console
4. Estés usando una cuenta de administrador

### Las sincronizaciones programadas no se están ejecutando

Verifica:
1. El contenedor Docker está ejecutándose: `docker ps`
2. La programación está habilitada en la UI
3. El volumen de base de datos está persistido (verifica docker-compose.yml)
4. Verifica los logs para errores: `docker-compose logs -f app`

## Actualizaciones y Mantenimiento

### ¿Cómo actualizo GWorkspace Toolbox?

Si usas Watchtower (incluido en docker-compose.yml), las actualizaciones son automáticas. Actualización manual:

```bash
docker-compose pull
docker-compose up -d
```

### ¿Con qué frecuencia se actualiza GWorkspace Toolbox?

Las actualizaciones se lanzan según sea necesario para correcciones de errores, parches de seguridad y nuevas características. Consulta [GitHub Releases](https://github.com/rafaelctz/GWorkspace-toolbox/releases) para el registro de cambios.

## Contribución

### ¿Puedo contribuir a GWorkspace Toolbox?

¡Sí! GWorkspace Toolbox es de código abierto. Consulta la [Guía de Contribución](https://github.com/rafaelctz/GWorkspace-toolbox/blob/main/CONTRIBUTING.md) para detalles.

### Encontré un error, ¿cómo lo reporto?

Por favor abre un issue en [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues) con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs real
- Salida de log si es aplicable

## ¿Todavía Tienes Preguntas?

- Consulta la [Guía de Solución de Problemas](/es/troubleshooting)
- Busca en [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Abre un nuevo issue si tu pregunta no está respondida
