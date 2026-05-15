# Acerca Cards

Tarjetas NFC profesionales. Cada carpeta = un cliente.

## Agregar cliente nuevo

```bash
python3 nuevo-cliente.py
```

El script pregunta los datos, genera el HTML y lo sube a GitHub automáticamente.
Vercel despliega en ~30 segundos. URL: `acerca-cards.vercel.app/nombre-apellido`

## Estructura

```
acerca-cards/
├── javier/          → acerca-cards.vercel.app/javier
├── juan-perez/      → acerca-cards.vercel.app/juan-perez
├── _template/       → Plantilla base editable
├── html_before.txt  → Parte 1 del template (no editar)
├── html_after.txt   → Parte 2 del template (no editar)
└── nuevo-cliente.py → Generador de tarjetas
```

## Precio de venta

| Servicio | Precio |
|---|---|
| Tarjeta NFC profesional | RD$2,500 |
| Bilingüe ES/EN | +RD$500 |
| Foto profesional | +RD$1,500 |
| Ediciones (año 2+) | RD$500 c/u |

## Tiempo de fulfillment

~15 minutos por cliente (incluyendo programar el tag físico).
