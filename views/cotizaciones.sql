EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'Ad Hoc Distributed Queries', 1;
RECONFIGURE;
GO

CREATE OR ALTER VIEW dbo.cotizaciones AS
SELECT
    yahoo_ticker,
    bme_ticker,
    [name],
    [date],
    [open],
    high,
    low,
    [close],
    adj_close,
    volume
FROM OPENROWSET(
    BULK '/var/opt/mssql/data/ibex35_prices.csv',
    FORMAT = 'CSV',
    FIRSTROW = 2
) WITH (
    yahoo_ticker varchar(20) 1,
    bme_ticker varchar(20) 2,
    [name] nvarchar(200) 3,
    [date] date 4,
    [open] decimal(19,8) 5,
    high decimal(19,8) 6,
    low decimal(19,8) 7,
    [close] decimal(19,8) 8,
    adj_close decimal(19,8) 9,
    volume bigint 10
) AS csv_data;
GO
