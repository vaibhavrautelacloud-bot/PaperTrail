CREATE OR REPLACE TRIGGER stock_update_trigger
AFTER UPDATE OF stock_quantity ON products
FOR EACH ROW
BEGIN
    INSERT INTO stock_audit (
        product_id,
        old_quantity,
        new_quantity,
        change_date
    )
    VALUES (
        :OLD.product_id,
        :OLD.stock_quantity,
        :NEW.stock_quantity,
        SYSDATE
    );
END;
/