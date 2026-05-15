#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║  ACERCA CARDS — Generador de tarjetas NFC            ║
║  Uso: python3 nuevo-cliente.py                       ║
║  Resultado: tarjeta en vivo en Vercel en ~30 seg     ║
╚══════════════════════════════════════════════════════╝
"""

import os, sys, json, base64, subprocess, re, urllib.request, urllib.error

# ── CONFIGURACIÓN (editar una sola vez) ──────────────────────────
GITHUB_TOKEN = "PEGA_TU_TOKEN_AQUI"
GITHUB_REPO  = "xavia01/acerca-cards"   # usuario/repo
VERCEL_BASE  = "https://acerca-cards.vercel.app"
# ─────────────────────────────────────────────────────────────────

HTML_BEFORE = open(os.path.join(os.path.dirname(__file__), "html_before.txt")).read()
HTML_AFTER  = open(os.path.join(os.path.dirname(__file__), "html_after.txt")).read()


def ask(label, required=True, default=""):
    while True:
        val = input(f"  {label}{' (opcional, Enter para saltar)' if not required else ''}: ").strip()
        if val:
            return val
        if not required:
            return default
        print("  ⚠️  Campo requerido.")


def slug(first, last):
    """Genera slug URL: 'Juan Pérez' → 'juan-perez'"""
    name = f"{first}-{last}".lower()
    name = re.sub(r'[áàä]','a', name)
    name = re.sub(r'[éèë]','e', name)
    name = re.sub(r'[íìï]','i', name)
    name = re.sub(r'[óòö]','o', name)
    name = re.sub(r'[úùü]','u', name)
    name = re.sub(r'[ñ]','n', name)
    name = re.sub(r'[^a-z0-9-]','-', name)
    name = re.sub(r'-+','-', name).strip('-')
    return name


def foto_a_base64(ruta):
    """Convierte foto a data URI embebida. Acepta ruta local."""
    if not ruta:
        return ""
    try:
        # Redimensionar con ImageMagick si está disponible
        tmp = "/tmp/avatar_tmp.jpg"
        result = subprocess.run(
            ["convert", ruta, "-resize", "400x400^", "-gravity", "Center",
             "-extent", "400x400", "-quality", "82", tmp],
            capture_output=True
        )
        target = tmp if result.returncode == 0 else ruta
        with open(target, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = "jpeg" if target.endswith(('.jpg','.jpeg')) else "png"
        return f"data:image/{ext};base64,{data}"
    except Exception as e:
        print(f"  ⚠️  No se pudo procesar la foto: {e}")
        return ""


def generar_html(p):
    """Genera el HTML completo con los datos del perfil."""
    linkedin_display = ""
    if p.get("linkedin"):
        parts = p["linkedin"].split("/in/")
        if len(parts) > 1:
            linkedin_display = parts[1].rstrip("/")

    profile_js = f"""const PROFILE = {{
  language: '{p.get("language","es")}',
  firstName: '{p["firstName"].replace("'","\\'")}',
  lastName: '{p["lastName"].replace("'","\\'")}',
  honorific: '{p.get("honorific","").replace("'","\\'")}',
  title: '{p.get("title","").replace("'","\\'")}',
  company: '{p.get("company","").replace("'","\\'")}',
  eyebrow: '{p.get("eyebrow","").replace("'","\\'")}',
  photo: '{p.get("photo","")}',
  phone: '{p.get("phone","")}',
  whatsapp: '{p.get("whatsapp","")}',
  email: '{p.get("email","")}',
  website: '{p.get("website","")}',
  linkedin: '{p.get("linkedin","")}',
  instagram: '{p.get("instagram","")}',
  address: '{p.get("address","").replace("'","\\'")}',
  mapsQuery: '{p.get("mapsQuery","").replace("'","\\'")}',
  legal: 'Tarjeta digital · 2026'
}};"""

    # Actualizar title y meta en el before
    full = p.get("honorific","") + " " + p["firstName"] + " " + p["lastName"]
    full = full.strip()
    eyebrow = p.get("eyebrow","")
    before = HTML_BEFORE
    before = re.sub(r'<title>.*?</title>', f'<title>{full} · {eyebrow}</title>', before)
    before = re.sub(r'content="Javier Matías Henríquez[^"]*"', f'content="{full} — {p.get("title","")}"', before)

    return before + profile_js + HTML_AFTER


def github_upload(path, content_bytes, message):
    """Sube o actualiza un archivo en GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    content_b64 = base64.b64encode(content_bytes).decode()

    # Verificar si ya existe (para obtener SHA)
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    sha = None
    try:
        with urllib.request.urlopen(req) as r:
            existing = json.loads(r.read())
            sha = existing.get("sha")
    except:
        pass

    payload = {"message": message, "content": content_b64}
    if sha:
        payload["sha"] = sha

    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main():
    print("\n" + "═"*54)
    print("  ACERCA CARDS · Nuevo cliente")
    print("═"*54 + "\n")

    # ── Recopilar datos ──────────────────────────────────────
    print("📋  DATOS DEL CLIENTE\n")
    honorific = ask("Honorífico (Dr., Dra., Lic., Ing., MSc., o vacío)", required=False)
    first     = ask("Nombre")
    last      = ask("Apellido(s)")
    title     = ask("Cargo / especialidad")
    company   = ask("Empresa / institución", required=False)
    eyebrow   = ask("Categoría (ej: Cardiología, Derecho, Innovación)", required=False)

    print()
    print("📞  CONTACTO\n")
    phone     = ask("Teléfono con código país (+1809...)")
    whatsapp  = ask("WhatsApp (Enter si es el mismo)", required=False) or phone
    email     = ask("Email", required=False)
    website   = ask("Sitio web (https://...)", required=False)
    linkedin  = ask("LinkedIn (URL completa)", required=False)
    instagram = ask("Instagram (URL completa)", required=False)
    address   = ask("Dirección (texto libre)", required=False)

    print()
    print("📸  FOTO\n")
    photo_path = ask("Ruta de la foto (arrastra el archivo aquí, o Enter para usar iniciales)", required=False)
    photo_path = photo_path.strip("'\"")  # limpiar comillas si arrastró archivo

    print()
    print("⚙️   Procesando...")

    # Foto
    photo_b64 = ""
    if photo_path and os.path.exists(photo_path):
        print("  → Optimizando foto...")
        photo_b64 = foto_a_base64(photo_path)
        print(f"  ✓ Foto lista ({len(photo_b64)//1000}KB)")
    elif photo_path:
        print(f"  ⚠️  No encontré la foto en: {photo_path} — se usarán iniciales")

    # Perfil
    profile = {
        "language": "es",
        "honorific": honorific,
        "firstName": first,
        "lastName": last,
        "title": title,
        "company": company,
        "eyebrow": eyebrow or title.split("·")[0].split("/")[0].strip(),
        "photo": photo_b64,
        "phone": phone,
        "whatsapp": whatsapp,
        "email": email,
        "website": website,
        "linkedin": linkedin,
        "instagram": instagram,
        "address": address,
        "mapsQuery": company or address,
    }

    # Generar HTML
    print("  → Generando tarjeta...")
    html = generar_html(profile)
    url_slug = slug(first, last)
    print(f"  ✓ HTML generado ({len(html)//1000}KB) · slug: {url_slug}")

    # Subir a GitHub
    print(f"  → Subiendo a GitHub ({GITHUB_REPO}/{url_slug}/index.html)...")
    full_name = f"{honorific} {first} {last}".strip()
    result = github_upload(
        f"{url_slug}/index.html",
        html.encode("utf-8"),
        f"Add card: {full_name}"
    )
    print(f"  ✓ Subido a GitHub")

    # URL final
    url = f"{VERCEL_BASE}/{url_slug}"
    print()
    print("═"*54)
    print(f"  ✅  TARJETA LISTA")
    print("═"*54)
    print(f"\n  👤  {full_name}")
    print(f"  🔗  {url}")
    print(f"\n  📲  Programa el NFC con esta URL:")
    print(f"      {url}")
    print()
    print("  En NFC Tools → Escribir → URL → pega la URL → Validar")
    print()

    # Copiar URL al portapapeles (si está disponible)
    try:
        subprocess.run(["xclip", "-selection", "clipboard"], input=url.encode(), check=True)
        print("  📋  URL copiada al portapapeles")
    except:
        try:
            subprocess.run(["pbcopy"], input=url.encode(), check=True)
            print("  📋  URL copiada al portapapeles")
        except:
            pass

    print("═"*54 + "\n")


if __name__ == "__main__":
    if GITHUB_TOKEN == "PEGA_TU_TOKEN_AQUI":
        print("\n⚠️  Configura tu GITHUB_TOKEN en la línea 17 del script.\n")
        sys.exit(1)
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelado.")
