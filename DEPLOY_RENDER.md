# Despliegue Treeconomy en Render Free + MongoDB Atlas (producción)

Guía paso a paso. Este entorno puede apuntar al **cluster Atlas de producción**
(`cluster0.xhm1v` / BD `treeconomy_pro`), el mismo que usa la app en prod.

**Riesgo:** cualquier migrate o cambio de datos desde Render afecta datos reales.
Asegúrate de Network Access abierto para Render (`0.0.0.0/0` en ese cluster).

---

## Fase 1 — Atlas (cluster de producción existente)

Usar el cluster que ya tienes (no el proyecto `treeconomy-staging` / M0):

| Dato | Valor esperado |
|------|----------------|
| Cluster host | `cluster0.xhm1v.mongodb.net` |
| Usuario | `treeadmin` (o el vigente en Atlas) |
| Base de datos | `treeconomy_pro` |
| URI típica | `mongodb+srv://...@cluster0.xhm1v.mongodb.net/treeconomy_pro?retryWrites=true&w=majority` |

1. En Atlas → ese cluster → **Network Access** → permite `0.0.0.0/0` (IPs de Render Free cambian).
2. Confirma usuario/password en **Database Access**.
3. **Connect** → Drivers → copia el URI si necesitas refrescarlo.

Valores para Render:

| Variable | Valor |
|----------|--------|
| `DB_HOST_PRO` | URI `mongodb+srv://...` del cluster de producción |
| `DB_USER_PRO` | Usuario Atlas (ej. `treeadmin`) |
| `DB_PASSWORD_PRO` | Password de ese usuario |
| `DB_NAME_PRO` | `treeconomy_pro` |

---

## Fase 2 — Código (ya preparado en el repo)

- [`build.sh`](build.sh) — `pip install`, `collectstatic`, `migrate`
- [`render.yaml`](render.yaml) — Blueprint opcional
- [`treeproject/settings/pro.py`](treeproject/settings/pro.py) — hosts/CSRF/dominio/DB dinámicos
- [`requirements.txt`](requirements.txt) — sin `aspose-words` (rompe el build)
- [`Procfile`](Procfile) — `waitress-serve --port=$PORT ...`
- [`runtime.txt`](runtime.txt) / [`.python-version`](.python-version) — `python-3.10.14`

Sube estos cambios a GitHub (`main`) antes de crear el servicio en Render.

```bash
git add build.sh render.yaml requirements.txt treeproject/settings/pro.py DEPLOY_RENDER.md
git commit -m "Prepare Render Free deploy with Atlas M0 staging settings"
git push origin main
```

---

## Fase 3 — Variables de entorno en Render

En el Web Service → **Environment** → añade:

### Obligatorias

| Key | Valor ejemplo / notas |
|-----|------------------------|
| `DJANGO_SETTINGS_MODULE` | `treeproject.settings.pro` |
| `PYTHON_VERSION` | `3.10.14` |
| `SECRET_KEY` | Generate (Render) o una clave larga aleatoria |
| `DB_HOST_PRO` | URI producción `mongodb+srv://...@cluster0.xhm1v.mongodb.net/...` |
| `DB_USER_PRO` | Usuario Atlas prod (ej. `treeadmin`) |
| `DB_PASSWORD_PRO` | Password de ese usuario |
| `DB_NAME_PRO` | `treeconomy_pro` |
| `ALLOWED_HOSTS` | `tu-servicio.onrender.com` (sin `https://`) |
| `CSRF_TRUSTED_ORIGINS` | `https://tu-servicio.onrender.com` |
| `DOMINIO` | `tu-servicio.onrender.com` |
| `DOMINIO_URL` | `https://tu-servicio.onrender.com` |
| `AWS_ACCESS_KEY_ID` | De tu `.env` |
| `AWS_SECRET_ACCESS_KEY` | De tu `.env` |
| `AWS_STORAGE_BUCKET_NAME` | De tu `.env` |
| `EMAIL_HOST` | ej. `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | Tu email SMTP |
| `EMAIL_HOST_PASSWORD` | App password SMTP |
| `DEFAULT_FROM_EMAIL` | Mismo o remitente |
| `NOTIFY_EMAIL` | Email de notificaciones |
| `SOCIAL_AUTH_FACEBOOK_KEY` | De `.env` |
| `SOCIAL_AUTH_FACEBOOK_SECRET` | De `.env` |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` | De `.env` |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` | De `.env` |
| `STRIPE_PUBLIC_KEY_PRO` | De `.env` (live o test, según quieras) |
| `STRIPE_PRIVATE_KEY_PRO` | De `.env` |
| `STRIPE_FREE_PRICE` | De `.env` |
| `CONVERTAPI_SECRET_KEY` | De `.env` |
| `MAPBOX_TOKEN` | De `.env` |

Render también inyecta `RENDER_EXTERNAL_HOSTNAME`; `pro.py` lo añade solo a `ALLOWED_HOSTS` / CSRF / dominio si falta.

**No subas** el archivo `.env` al repositorio.

---

## Fase 4 — Crear Web Service en Render

1. [dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service**.
2. Conecta el repo de GitHub y selecciona la rama `main`.
3. Configuración:
   - **Language:** Python 3
   - **Plan:** Free
   - **Build Command:** `./build.sh`
   - **Start Command:** `waitress-serve --port=$PORT treeproject.wsgi:application`
4. Pega las variables de entorno → **Create Web Service**.
5. Espera el deploy. Si falla, revisa **Logs** (`pip`, `collectstatic` o `migrate`).

Alternativa: **New** → **Blueprint** y usa [`render.yaml`](render.yaml); igual debes completar los secretos en el dashboard.

---

## Fase 5 — Verificación

1. Abre `https://<servicio>.onrender.com/es-co/` (el primer hit en Free puede tardar ~30–60 s).
2. Admin: `https://<servicio>.onrender.com/es-co/admin/`
3. En **Render Shell**:
   ```bash
   python manage.py createsuperuser
   ```
4. En Atlas → Browse Collections → confirma actividad en `treeconomy_pro`.
5. Prueba login y que los estáticos carguen desde S3.

### Si algo falla

| Síntoma | Qué revisar |
|---------|-------------|
| Build: `aspose-words` | Ya está comentado en `requirements.txt`; haz pull/push |
| `DisallowedHost` | `ALLOWED_HOSTS` y `RENDER_EXTERNAL_HOSTNAME` |
| CSRF 403 | `CSRF_TRUSTED_ORIGINS` con `https://...` |
| Error Mongo / timeout | Network Access `0.0.0.0/0`, URI y user/pass |
| PDF / WeasyPrint | Limitación Free sin libs de sistema; el resto de la app puede funcionar |

---

## Limitaciones Free

- El servicio **se duerme** tras ~15 min sin tráfico.
- No uses este entorno contra la BD de producción.
- PDF (WeasyPrint) puede fallar sin Docker + paquetes del sistema.
