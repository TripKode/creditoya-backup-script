# Credenciales de Google Cloud Storage

Esta carpeta contiene los archivos de credenciales JSON para acceder a Google Cloud Storage.

## ⚠️ Importante

**Este repositorio es PRIVADO**, por lo que es seguro incluir los archivos JSON de credenciales aquí.

## Archivos en esta carpeta

Los archivos JSON de credenciales de Google Cloud deben colocarse aquí.

Ejemplo:
```
credentials/
├── README.md
├── .gitkeep
└── mi-proyecto-gcs-123456.json  ← Tu archivo de credenciales
```

## Obtener credenciales

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto
3. Ve a "IAM & Admin" → "Service Accounts"
4. Crea una cuenta de servicio o selecciona una existente
5. Click en "Keys" → "Add Key" → "Create new key"
6. Selecciona formato JSON
7. Descarga el archivo y colócalo en esta carpeta

## Configuración

El archivo de credenciales se configura en el archivo `.env` del proyecto:

```env
GCS_CREDENTIALS_PATH=credentials/tu-archivo-de-credenciales.json
```

O durante la configuración interactiva del `setup.sh`.

## ⚠️ Si el repositorio se vuelve público

Si en algún momento este repositorio se vuelve público:

1. **Eliminar inmediatamente** todos los archivos JSON de esta carpeta
2. **Revocar** las credenciales en Google Cloud Console
3. **Crear nuevas** credenciales
4. **Actualizar** el `.gitignore` para ignorar los archivos JSON:
   ```gitignore
   credentials/*
   !credentials/.gitkeep
   ```
5. **Limpiar** el historial de Git de los archivos sensibles

## Seguridad

Aunque el repo es privado, recuerda:
- ✅ Mantén el repositorio como PRIVADO
- ✅ Otorga acceso solo a personas de confianza
- ✅ Usa credenciales con permisos mínimos necesarios
- ✅ Rota las credenciales periódicamente
- ✅ Monitorea el uso de las credenciales en GCP Console
