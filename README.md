# DemoIACodex

Proyecto de analisis de valores del IBEX 35 usando datos publicos de Yahoo Finanzas mediante `yfinance`.

## Alcance inicial

- Mantener una lista configurable de componentes del IBEX 35.
- Descargar historico diario OHLCV para cada valor usando tickers Yahoo `.MC`.
- Guardar datos originales por valor en `data/raw/`.
- Generar un dataset consolidado en `data/processed/ibex35_prices.csv`.
- Registrar errores de descarga sin detener todo el proceso.

## Fuentes

- Composicion del indice: BME publica la composicion y revision del IBEX 35.
- Cotizaciones historicas: Yahoo Finanzas via `yfinance`.

Nota: la composicion del IBEX 35 se revisa periodicamente. La lista en `config/ibex35_symbols.csv` debe validarse cuando BME publique cambios.

## Preparacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Descarga de datos

Por defecto descarga todo el historico disponible en Yahoo Finanzas para cada valor (`period=max`).

```powershell
python src\download_prices.py
```

Opciones utiles:

```powershell
python src\download_prices.py --start 2024-01-01 --end 2024-12-31
python src\download_prices.py --period 10y
python src\download_prices.py --symbols-file config\ibex35_symbols.csv --output-dir data
```
