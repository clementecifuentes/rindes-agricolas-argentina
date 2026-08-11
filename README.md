# Rindes agrícolas en Argentina 🌾

Análisis histórico de la producción de **soja, maíz y trigo** en Argentina sobre
las **Estimaciones Agrícolas oficiales** de la Secretaría de Agricultura,
Ganadería y Pesca: **56 campañas (1969/70 → 2024/25)** con superficie, producción
y rendimiento por departamento.

**Stack:** Python · Pandas · Matplotlib

---

## Hallazgos principales

- **La soja pasó de cultivo marginal a líder absoluto**: de menos de 1 M tn en
  los 70 a picos de 60 M tn, aunque el maíz la alcanzó (y por momentos superó)
  en las últimas campañas — un cambio estructural de la agricultura argentina.
- **El rinde del maíz casi se triplicó** desde los años 90 (de ~2,5 a ~7 tn/ha),
  impulsado por genética e intensificación. Soja y trigo mejoraron a un ritmo
  mucho menor (~3 tn/ha hoy) — el techo biológico y el desplazamiento a
  ambientes marginales pesan.
- **La zona núcleo concentra la producción**: Buenos Aires (42 M tn), Córdoba
  (34,9) y Santa Fe (20,2) explican la mayor parte del volumen de los tres
  cultivos en 2024/25.
- **La brecha de rindes en soja es enorme**: departamentos que superan 3,5 tn/ha
  conviven con otros por debajo de 1,5 — la distribución bimodal sugiere dos
  agriculturas distintas (núcleo vs. extra-pampeana), con implicancias directas
  para el potencial de mejora.

## Visualizaciones

### Producción nacional histórica
![Producción nacional por campaña](figures/01_produccion_nacional.png)

### Evolución del rendimiento
![Rendimiento nacional promedio](figures/02_rendimiento.png)

### Concentración geográfica
![Producción por provincia](figures/03_provincias.png)

### Brecha de rindes
![Distribución de rindes de soja por departamento](figures/04_brecha_rindes.png)

## Fuente de datos

[Estimaciones Agrícolas](https://datos.magyp.gob.ar/dataset/estimaciones-agricolas)
— Secretaría de Agricultura, Ganadería y Pesca, República Argentina.
Datos abiertos con ~160.000 registros por cultivo, campaña, provincia y
departamento desde 1969.

## Reproducir el análisis

```bash
pip install -r requirements.txt

# 1. Descargar los datos (~15 MB)
python src/descargar_datos.py

# 2. Generar las figuras
python src/analisis.py
```

## Estructura

```
├── src/
│   ├── descargar_datos.py   # descarga del dataset oficial
│   └── analisis.py          # series históricas, rankings y brecha de rindes
├── figures/                 # gráficos generados (PNG)
├── data/                    # datos crudos (no versionados)
└── requirements.txt
```

## Notas metodológicas

- Se usan las categorías `soja total`, `maíz` y `trigo total` del dataset.
- El rendimiento nacional se calcula ponderado (producción total / superficie
  cosechada total), no como promedio simple de departamentos.
- En la brecha de rindes se consideran solo departamentos con más de 1.000 ha
  cosechadas para evitar ruido de lotes chicos.

---

**Clemente Cifuentes** — Data Analyst ·
[LinkedIn](https://linkedin.com/in/clementecifuentes) ·
[Portafolio](https://github.com/clementecifuentes)
