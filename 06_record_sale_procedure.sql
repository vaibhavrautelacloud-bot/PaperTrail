CREATE OR REPLACE PROCEDURE record_sale (
    p_product_id NUMBER,
    p_qty NUMBER
)
IS
    v_price NUMBER(10,2);
    v_stock NUMBER;
    v_gross NUMBER(10,2);
    v_discount NUMBER(10,2);
    v_final NUMBER(10,2);
BEGIN
    IF p_qty IS NULL OR p_qty <= 0 THEN
        RAISE_APPLICATION_ERROR(
            -20001,
            'Quantity must be greater than zero'
        );
    END IF;

    SELECT price, stock_quantity
    INTO v_price, v_stock
    FROM products
    WHERE product_id = p_product_id
    FOR UPDATE;

    IF v_stock < p_qty THEN
        RAISE_APPLICATION_ERROR(
            -20002,
            'Not enough stock available'
        );
    END IF;

    v_gross := v_price * p_qty;
    v_discount := calculate_discount(v_gross);
    v_final := v_gross - v_discount;

    UPDATE products
    SET stock_quantity = stock_quantity - p_qty
    WHERE product_id = p_product_id;

    INSERT INTO sales (
        product_id,
        quantity,
        gross_amount,
        discount,
        final_amount
    )
    VALUES (
        p_product_id,
        p_qty,
        v_gross,
        v_discount,
        v_final
    );

    COMMIT;

    DBMS_OUTPUT.PUT_LINE('Sale recorded successfully.');
    DBMS_OUTPUT.PUT_LINE('Gross Amount: Rs. ' || v_gross);
    DBMS_OUTPUT.PUT_LINE('Discount: Rs. ' || v_discount);
    DBMS_OUTPUT.PUT_LINE('Final Amount: Rs. ' || v_final);
    DBMS_OUTPUT.PUT_LINE('Remaining Stock: ' || (v_stock - p_qty));

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(
            -20003,
            'Product ID does not exist'
        );
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/