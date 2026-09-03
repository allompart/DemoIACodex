# Analisis_Ibex35 Semantic Model

Modelo semantico inicial para Power BI con dos tablas importadas desde SQL Server:

- `cotizaciones`: historico OHLCV de los valores IBEX 35.
- `valores`: resumen de descarga por ticker, pensado para usarse como filtro en reportes.

No se definen relaciones entre tablas en esta version.

## Conexion

- Servidor: `127.0.0.1,14333`
- Base de datos: `Analisis_Ibex`
- Vistas origen: `dbo.cotizaciones`, `dbo.valores`

Las credenciales no se guardan en el repositorio. Configuralas en Power BI Desktop al abrir/refrescar el modelo.
