# Inyector de Atributos

El Inyector de Atributos te permite inyectar atributos personalizados en lote a todos los usuarios dentro de una Unidad Organizativa especificada, ahorrando horas de trabajo manual.


![Feature Screenshot](/screenshots/attribute-injector.png)

## Resumen

Google Workspace soporta atributos de usuario personalizados a través de esquemas personalizados. El Inyector de Atributos facilita aplicar estos atributos a todos los usuarios en una OU a la vez, en lugar de actualizar manualmente cada usuario individualmente.

## Cómo Funciona

1. **Seleccionar OU Objetivo**: Ingresa la ruta de la unidad organizativa (ej., `/Ventas/Regional`)
2. **Especificar Atributo**: Ingresa el nombre del atributo personalizado de tu esquema
3. **Establecer Valor**: Ingresa el valor a asignar a todos los usuarios
4. **Inyectar**: Haz clic en "Inyectar Atributos" para aplicar cambios
5. **Revisar Resultados**: Ve cuántos usuarios fueron actualizados exitosamente

## Requisitos Previos

### Esquema Personalizado Requerido
Antes de usar el Inyector de Atributos, debes crear un esquema personalizado en Google Workspace:

1. Ve a [Google Admin Console](https://admin.google.com)
2. Navega a **Directory** > **Users** > **Manage custom attributes**
3. Haz clic en **Add Custom Attribute**
4. Crea tu esquema (ej., "InformacionEmpleado")
5. Agrega campos (ej., "departamento", "centroCostos", "tipoEmpleado")

## Formato de Nombre de Atributo

Los atributos deben especificarse en el formato: `NombreEsquema.NombreCampo`

**Ejemplos:**
- `InformacionEmpleado.departamento`
- `InformacionEmpleado.centroCostos`
- `InformacionEmpleado.tipoEmpleado`
- `DatosPersonalizados.region`

## Casos de Uso Comunes

### Asignación de Departamento
Asignar códigos o nombres de departamento a todos los usuarios en OUs departamentales.

```
OU: /Ingenieria
Atributo: InformacionEmpleado.departamento
Valor: ING
```

### Seguimiento de Centro de Costos
Aplicar códigos de centro de costos para informes financieros.

```
OU: /Finanzas/Cuentas por Pagar
Atributo: InformacionEmpleado.centroCostos
Valor: FIN-CP-001
```

### Clasificación de Empleados
Etiquetar usuarios por tipo de empleado para aplicación de políticas.

```
OU: /Contratistas
Atributo: InformacionEmpleado.tipoEmpleado
Valor: Contratista
```

## Mejores Prácticas

### Probar en OUs Pequeñas Primero
Antes de aplicar atributos a OUs grandes:
1. Prueba en una OU de prueba pequeña con 2-3 usuarios
2. Verifica que el atributo aparezca correctamente en Admin Console
3. Luego procede con OUs más grandes

### Usar OUs Jerárquicas
Organiza tu estructura de OU para que coincida con tus necesidades de atributos.

### Documentar tu Esquema
Mantén documentación de:
- Nombres y campos de esquemas personalizados
- Significado de cada atributo
- Valores válidos para cada campo
- Qué OUs usan qué atributos

## Solución de Problemas

### Error "Atributo no encontrado"
El atributo especificado no existe en tu esquema personalizado.

**Solución:**
1. Ve a Admin Console > Directory > Users > Manage custom attributes
2. Verifica que el esquema y campo existan
3. Usa el formato exacto: `NombreEsquema.nombreCampo`

### Error "OU no encontrada"
La ruta de la unidad organizativa es incorrecta.

**Solución:**
1. Verifica que el formato de ruta de OU comience con `/`
2. Verifica que la OU exista en Admin Console
3. Usa la ruta exacta (sensible a mayúsculas)

## Próximos Pasos

- Aprende sobre [Sincronización de Grupos OU](/es/features/ou-group-sync)
- Revisa [Extractor de Alias](/es/features/alias-extractor)
- Consulta el [FAQ](/es/faq) para preguntas comunes
