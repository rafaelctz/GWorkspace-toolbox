# Instalación

GWorkspace Toolbox se ejecuta como un contenedor Docker, haciendo que la instalación sea simple y consistente en todas las plataformas.

## Requisitos Previos

- Docker y Docker Compose instalados en tu sistema
- Cuenta de administrador de Google Workspace
- Proyecto de Google Cloud con Admin SDK API habilitado

## Paso 1: Instalar Docker

### Windows
Descarga e instala [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop)

### macOS
Descarga e instala [Docker Desktop para Mac](https://www.docker.com/products/docker-desktop)

### Linux
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## Paso 2: Configuración de Google Workspace

### Habilitar Admin SDK API
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un nuevo proyecto o selecciona uno existente
3. Navega a **APIs & Services** > **Library**
4. Busca "Admin SDK API" y habilítalo

### Crear Credenciales OAuth 2.0
1. Ve a **APIs & Services** > **Credentials**
2. Haz clic en **Create Credentials** > **OAuth client ID**
3. Selecciona **Web application**
4. Agrega URI de redirección autorizado: `http://localhost:8000/oauth2callback`
5. Descarga el archivo JSON de credenciales

## Paso 3: Desplegar con Docker

### Crear Directorio del Proyecto
```bash
mkdir gworkspace-toolbox
cd gworkspace-toolbox
```

### Descargar Configuración de Docker Compose
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/rafaelctz/GWorkspace-toolbox/main/docker-compose.yml
```

### Agregar tus Credenciales
1. Guarda tus credenciales OAuth descargadas como `credentials.json` en el directorio del proyecto
2. La aplicación te guiará a través de la autenticación en la primera ejecución

### Iniciar la Aplicación
```bash
docker-compose up -d
```

La aplicación estará disponible en `http://localhost:8000`

## Paso 4: Configuración Inicial

1. Abre tu navegador en `http://localhost:8000`
2. Haz clic en el botón **Autenticar**
3. Inicia sesión con tu cuenta de administrador de Google Workspace
4. Otorga los permisos solicitados
5. Serás redirigido de vuelta a la aplicación

## Actualizaciones Automáticas

La configuración de Docker Compose incluye Watchtower, que verifica automáticamente actualizaciones diariamente y mantiene tu instalación actualizada.

Para actualizar manualmente:
```bash
docker-compose pull
docker-compose up -d
```

## Próximos Pasos

Ahora que está instalado, consulta la [Guía de Inicio Rápido](/es/quickstart) para aprender a usar las características.

## Solución de Problemas

Si encuentras problemas, consulta la [Guía de Solución de Problemas](/es/troubleshooting) o revisa [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues).
