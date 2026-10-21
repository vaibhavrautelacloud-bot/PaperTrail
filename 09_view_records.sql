-- View all products
SELECT * FROM products;

-- View all sales
SELECT * FROM sales;

-- View all stock changes
SELECT * FROM stock_audit;

-- Calculate total sales
SELECT SUM(final_amount) AS total_sales
FROM sales;

-- View products with low stock
SELECT product_id, product_name, stock_quantity
FROM products
WHERE stock_quantity <= 20;