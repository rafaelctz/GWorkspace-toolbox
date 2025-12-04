# Guía de Solución de Problemas

Soluciones a problemas comunes al usar GWorkspace Toolbox.

## Problemas de Instalación

### Docker No Inicia

**Problema**: El contenedor Docker no inicia o sale inmediatamente.

**Soluciones**:

```bash
# Verificar si Docker está ejecutándose
docker ps

# Ver logs del contenedor
docker-compose logs app

# Verificar conflictos de puerto
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Reiniciar contenedores
docker-compose down
docker-compose up -d
```

### Puerto Ya en Uso

**Problema**: Mensaje de error sobre puerto 8000 en uso.

**Solución**: Cambia el puerto en docker-compose.yml:

```yaml
services:
  app:
    ports:
      - "8080:8000"  # Usa 8080 en lugar de 8000
```

Luego accede a la aplicación en `http://localhost:8080`

### Archivo de Credenciales No Encontrado

**Problema**: La aplicación no puede encontrar credentials.json.

**Soluciones**:

```bash
# Verificar que el archivo existe
ls -la credentials.json

# Asegurar que está en el directorio del proyecto
pwd
ls

# Verificar montaje de volumen en docker-compose.yml
cat docker-compose.yml | grep credentials
```

## Problemas de Autenticación

### Error OAuth: redirect_uri_mismatch

**Problema**: Error OAuth mencionando desajuste de URI de redirección.

**Solución**:

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Navega a APIs & Services > Credentials
3. Edita tu OAuth 2.0 Client ID
4. Bajo "Authorized redirect URIs", agrega:
   - `http://localhost:8000/oauth2callback`
5. Guarda e intenta autenticar nuevamente

### La Autenticación Sigue Fallando

**Problema**: No puedes completar el flujo de autenticación.

**Lista de verificación**:

- [ ] Admin SDK API está habilitado en Google Cloud Console
- [ ] El URI de redirección del cliente OAuth está configurado correctamente
- [ ] Estás usando una cuenta de administrador
- [ ] credentials.json es el cliente OAuth (no Service Account)
- [ ] El navegador permite popups desde localhost
- [ ] No hay extensiones del navegador bloqueando el flujo

**Restablecer autenticación**:

```bash
# Detener contenedores
docker-compose down

# Eliminar archivo token
rm token.json

# Iniciar contenedores
docker-compose up -d

# Intentar autenticar nuevamente
```

## Problemas del Extractor de Alias

### No Hay Alias en CSV

**Problema**: El archivo CSV está vacío o faltan alias.

**Posibles causas**:

1. **No existen alias**: Verifica en Admin Console que los usuarios tengan alias
2. **Problema de permisos**: Asegúrate de estar autenticado como administrador
3. **API no habilitada**: Verifica que Admin SDK API esté habilitada

## Problemas del Inyector de Atributos

### Error "Atributo no encontrado"

**Problema**: Error diciendo que el atributo no existe.

**Solución**:

1. Verifica que el esquema personalizado exista en Admin Console:
   - Directory > Users > Manage custom attributes
2. Verifica el formato del nombre del atributo: `NombreEsquema.nombreCampo`
3. Asegura coincidencia exacta de mayúsculas (sensible a mayúsculas)

### Error "OU no encontrada"

**Problema**: Error diciendo que la unidad organizativa no existe.

**Solución**:

1. Verifica que la ruta de OU comience con `/`
2. Verifica la ruta exacta en Admin Console (sensible a mayúsculas)
3. Sin espacios finales o caracteres especiales

## Problemas de Sincronización de Grupos OU

### Error "Grupo no encontrado"

**Problema**: Error diciendo que el grupo no existe.

**Soluciones**:

1. Verifica que la dirección de correo del grupo sea exactamente correcta
2. Verifica que el grupo exista en Admin Console o Gmail
3. Asegúrate de tener permiso para gestionar el grupo
4. El correo del grupo debe estar completo: `equipo@empresa.com`

### Miembros No Se Están Agregando

**Problema**: La sincronización se completa pero los miembros no se agregan al grupo.

**Lista de verificación**:

- [ ] El grupo existe y es accesible
- [ ] La OU contiene usuarios (no está vacía)
- [ ] Tienes permiso para gestionar el grupo
- [ ] Los usuarios no están ya en el grupo
- [ ] Los permisos de API son correctos

### La Sincronización Programada No Se Está Ejecutando

**Problema**: Los trabajos de sincronización programados no se están ejecutando.

**Lista de verificación**:

- [ ] El contenedor Docker está ejecutándose continuamente
- [ ] El interruptor de programación está habilitado en la UI
- [ ] El volumen de base de datos está persistido
- [ ] No hay errores en los logs del contenedor

**Depurar**:

```bash
# Verificar si el contenedor está ejecutándose
docker ps | grep gworkspace

# Ver logs
docker-compose logs -f app

# Verificar que el archivo de base de datos existe
ls -la database/
```

## Problemas de UI/Interfaz

### La Página No Carga

**Problema**: El navegador muestra error de conexión o página en blanco.

**Soluciones**:

```bash
# Verificar que el contenedor está ejecutándose
docker ps

# Verificar salud del contenedor
docker-compose ps

# Ver logs para errores
docker-compose logs app

# Reiniciar contenedores
docker-compose restart

# Verificar URL
# Debe ser http://localhost:8000 (no https)
```

## Obteniendo Más Ayuda

### Habilitar Registro de Depuración

Para logs más detallados:

```yaml
# En docker-compose.yml, agrega variable de entorno
services:
  app:
    environment:
      - PORT=8000
      - HOST=0.0.0.0
      - LOG_LEVEL=DEBUG  # Agrega esta línea
```

### Reportar Problemas

Si no puedes resolver el problema:

1. Verifica [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues) para problemas similares
2. Revisa el [FAQ](/es/faq)
3. Abre un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Salida de log
   - Información del sistema

¿Sigues teniendo problemas? Abre un issue en [GitHub](https://github.com/rafaelctz/GWorkspace-toolbox/issues) con todos los detalles.
