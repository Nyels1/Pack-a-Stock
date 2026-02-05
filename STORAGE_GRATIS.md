# 🆓 ALMACENAMIENTO GRATIS PARA PACK-A-STOCK

## ✨ OPCIÓN RECOMENDADA: Cloudflare R2

**Cloudflare R2** es GRATIS hasta 10GB y sin costos de transferencia.

### 📦 Límites Gratuitos (R2):
- ✅ **10GB** de almacenamiento gratis
- ✅ **Transferencia ilimitada** gratis (sin costo de egreso)
- ✅ 10 millones de operaciones clase A/mes (PUT, LIST)
- ✅ 100 millones de operaciones clase B/mes (GET, HEAD)
- ✅ No requiere tarjeta de crédito

### 💡 ¿Cuánto puedes almacenar gratis?

**Estimación realista:**
- QR Code (PNG): ~5KB por material
- Imagen de material (JPG optimizada): ~50KB por material
- **Total por material: ~55KB**

**Con 10GB gratis:**
- 📦 **~18,000 materiales** con imagen y QR
- 📦 **~200,000 materiales** solo con QR (sin imagen)

**¡Es más que suficiente para la mayoría de empresas!** 🎉

---

## 🚀 CONFIGURACIÓN PASO A PASO (5 minutos)

### 1. Crear cuenta en Cloudflare

1. Ve a https://dash.cloudflare.com/sign-up
2. Crea tu cuenta gratis (email + contraseña)
3. Verifica tu email

### 2. Crear bucket R2

1. En el dashboard, ve a **R2 Object Storage**
2. Click **Create bucket**
3. Nombre del bucket: `pack-a-stock` (o el que prefieras)
4. Location: **Automatic** (Cloudflare lo distribuye globalmente)
5. Click **Create bucket**

### 3. Generar API Token

1. En R2, ve a **Manage R2 API Tokens**
2. Click **Create API token**
3. Configuración:
   - **Token name**: pack-a-stock-api
   - **Permissions**: Object Read & Write
   - **TTL**: Forever (o el tiempo que prefieras)
4. Click **Create API Token**
5. **COPIA Y GUARDA:**
   - Access Key ID: `abc123...`
   - Secret Access Key: `xyz789...`
   - ⚠️ **No podrás ver el Secret de nuevo!**

### 4. Obtener endpoint del bucket

1. En tu bucket, ve a **Settings**
2. Busca la sección **S3 API**
3. Copia el endpoint (ejemplo: `https://abc123def456.r2.cloudflarestorage.com`)

### 5. Hacer el bucket público (para que los QR e imágenes sean accesibles)

1. En tu bucket, ve a **Settings**
2. Sección **Public Access**
3. Click **Allow Access**
4. Se generará una URL pública: `https://pub-xxxxxx.r2.dev`
5. Copia esta URL (la usarás para `AWS_S3_CUSTOM_DOMAIN`)

### 6. Configurar tu `.env`

Edita tu archivo `.env` en Pack-a-Stock:

```env
# Activar S3/R2
USE_S3=True

# Cloudflare R2 Credentials
AWS_ACCESS_KEY_ID=tu-access-key-id-aqui
AWS_SECRET_ACCESS_KEY=tu-secret-access-key-aqui

# Bucket settings
AWS_STORAGE_BUCKET_NAME=pack-a-stock
AWS_S3_ENDPOINT_URL=https://abc123def456.r2.cloudflarestorage.com

# URL pública del bucket
AWS_S3_CUSTOM_DOMAIN=pub-xxxxxx.r2.dev

# Permisos
AWS_DEFAULT_ACL=public-read
```

### 7. Reiniciar backend

```bash
docker-compose restart backend
```

### 8. ¡Listo! 🎉

Ahora cuando crees un material:
- El QR se generará automáticamente
- Se guardará en: `https://pub-xxxxxx.r2.dev/qr_codes/1/MAT-ABC123.png`
- Las imágenes también se guardarán en R2

---

## 🧪 PROBAR QUE FUNCIONA

1. Crea un material nuevo desde el frontend
2. El QR se debería generar automáticamente
3. Revisa la consola del backend para ver logs
4. Ve a Cloudflare R2 → tu bucket → Objects
5. Deberías ver la carpeta `qr_codes/`

**URL del QR:**
```
https://pub-xxxxxx.r2.dev/qr_codes/1/MAT-ABC123DEF456.png
```

---

## 📊 MONITOREAR USAGE

En Cloudflare dashboard:
- R2 → Overview → Metrics
- Verás cuánto almacenamiento estás usando
- Cuántas operaciones has hecho
- Todo en tiempo real

---

## ⚠️ SI SUPERAS LOS 10GB (muy difícil)

Cloudflare cobra:
- $0.015/GB/mes por almacenamiento extra
- Ejemplo: 20GB = $0.15/mes (15 centavos!)
- Transferencia sigue siendo GRATIS

---

## 🆚 COMPARATIVA

| Feature | Cloudflare R2 (Gratis) | DigitalOcean Spaces | AWS S3 |
|---------|------------------------|---------------------|--------|
| Precio base | **$0/mes** | $5/mes | Variable |
| Almacenamiento gratis | 10GB | 0GB | 5GB (12 meses) |
| Transferencia | GRATIS ilimitada | 1TB incluido | Se cobra |
| Setup | Fácil | Fácil | Medio |
| Confiabilidad | Alta | Alta | Muy alta |

---

## ❓ PREGUNTAS FRECUENTES

**¿Necesito tarjeta de crédito?**
No, el tier gratuito de R2 no requiere tarjeta.

**¿Qué pasa si me paso de 10GB?**
Te cobran $0.015/GB adicional (15 centavos por 10GB extra).

**¿Los archivos son públicos?**
Sí, con `AWS_DEFAULT_ACL=public-read` cualquiera con la URL puede verlos.

**¿Puedo cambiar después a otro servicio?**
Sí, solo cambia las variables de `.env` y migra los archivos.

**¿Funciona igual que S3?**
Sí, R2 es 100% compatible con la API de S3.

---

## 🔐 SEGURIDAD

**Token API:**
- ⚠️ NUNCA subas el `.env` a Git
- ✅ Usa `.env.example` como plantilla
- ✅ Agrega `.env` al `.gitignore`

**Archivos públicos:**
- Los QR codes DEBEN ser públicos (para escanear)
- Las imágenes de materiales también
- Si necesitas archivos privados más adelante, crea otro bucket

---

## 💪 SIGUIENTE PASO

Ahora que tienes almacenamiento gratis configurado, puedes:
1. ✅ Crear materiales con imágenes
2. ✅ Los QR se generan automáticamente
3. ✅ Todo se guarda en la nube gratis
4. ✅ Escalable hasta ~18,000 materiales

**¿Listo para continuar con el escaneo QR en el frontend?** 📱
