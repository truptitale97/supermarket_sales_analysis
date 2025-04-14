SELECT *
FROM (
  SELECT 
    dcp.branch,
    dcp.`product line` AS product_line,
    ROUND(SUM(fs.total), 2) AS total_sales,
    RANK() OVER (PARTITION BY dcp.branch ORDER BY SUM(fs.total) DESC) AS sales_rank
  FROM 
    `supermarketsales-456610.supermarket_sales.fact_sales` fs
  JOIN 
    `supermarketsales-456610.supermarket_sales.dim_customer_product` dcp
    ON fs.`invoice id` = dcp.`invoice id`
  GROUP BY 
    dcp.branch, dcp.`product line`
)
WHERE sales_rank <= 3
ORDER BY 
  branch, sales_rank