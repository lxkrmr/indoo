# Indoo – Verbesserungsvorschläge (aus ERP-1737 Regression-Session)

## Kontext
Beim Testen der ERP-1737-Flows (Delivery Note Werte) haben wir `indoo` für schnelle Daten-Checks genutzt.
Dabei sind ein paar UX-/CLI-Themen aufgefallen, die den Alltag unnötig bremsen.

## Offene Punkte

### C) Hilfreichere Fehlertexte
**Vorschlag:**
- bei ungültiger Feldsyntax explizit anzeigen:
  - „Use space-separated fields"
  - Beispielkommando direkt im Fehlertext

**Nutzen:**
- schnellere Selbstkorrektur

## Erledigt

### A) Domain-/Filter-Support für `list` ✓
`--domain` akzeptiert eine Python-Liste von Tripeln, direkt kopierbar aus Code.

```bash
indoo list product.product id display_name bid_price \
  --domain "[('bid_price', '>', 0), ('name', 'not ilike', 'Gold')]" \
  --limit 20
```

## Verworfen

### B) CSV-Felder
Nur ein Weg: space-separated. CSV widerspricht CLI-Konventionen und bringt
extra Parsing ohne echten Mehrwert.

### D) Batch-Read für mehrere Datensätze
Nicht nötig. `--domain "[('id', 'in', [10, 11, 12])]"` auf `list` deckt den Use Case ab.

### E) `search`-Subcommand
Nicht nötig. `list --domain` ist der Power Mode. Kein zweites Kommando für dasselbe.
