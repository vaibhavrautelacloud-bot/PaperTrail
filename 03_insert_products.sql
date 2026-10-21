INSERT INTO products (
    product_id, product_name, stock_quantity, price
)
VALUES (101, 'Notebook', 50, 60);

INSERT INTO products (
    product_id, product_name, stock_quantity, price
)
VALUES (102, 'Pen', 100, 10);

INSERT INTO products (
    product_id, product_name, stock_quantity, price
)
VALUES (103, 'Pencil', 80, 5);

INSERT INTO products (
    product_id, product_name, stock_quantity, price
)
VALUES (104, 'Eraser', 40, 5);

INSERT INTO products (
    product_id, product_name, stock_quantity, price
)
VALUES (105, 'School Bag', 20, 500);

COMMIT;

SELECT * FROM products;