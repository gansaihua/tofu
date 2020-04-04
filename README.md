# tofu

SELECT
a.symbol,
DATE_FORMAT(a.contract_issued, '%Y%m%d'),
DATE_FORMAT(MIN(datetime), '%Y%m%d'),
DATE_FORMAT(a.last_traded, '%Y%m%d'),
DATE_FORMAT(MAX(datetime),'%Y%m%d')
FROM futures_bar AS b
JOIN futures_code AS a
ON b.code_id = a.id
WHERE a.root_symbol_id = 26
GROUP BY a.symbol
