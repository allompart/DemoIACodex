CREATE OR ALTER VIEW dbo.valores AS
SELECT
    ticker,
    rows,
    status,
    message
FROM OPENROWSET(
    BULK '/var/opt/mssql/data/download_report.csv',
    FORMAT = 'CSV',
    FIRSTROW = 2
) WITH (
    ticker varchar(20) 1,
    rows int 2,
    status varchar(20) 3,
    message nvarchar(4000) 4
) AS csv_data;
GO
