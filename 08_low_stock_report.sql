SET SERVEROUTPUT ON;

DECLARE
    CURSOR low_stock_cursor IS
        SELECT product_id, product_name, stock_quantity
        FROM products
        WHERE stock_quantity <= 20;

    v_id products.product_id%TYPE;
    v_name products.product_name%TYPE;
    v_stock products.stock_quantity%TYPE;
BEGIN
    OPEN low_stock_cursor;

    LOOP
        FETCH low_stock_cursor
        INTO v_id, v_name, v_stock;

        EXIT WHEN low_stock_cursor%NOTFOUND;

        DBMS_OUTPUT.PUT_LINE(
            'ID: ' || v_id ||
            ' | Product: ' || v_name ||
            ' | Stock: ' || v_stock
        );
    END LOOP;

    CLOSE low_stock_cursor;
END;
/