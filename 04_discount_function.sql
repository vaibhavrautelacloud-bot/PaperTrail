CREATE OR REPLACE FUNCTION calculate_discount (
    p_amount NUMBER
)
RETURN NUMBER
IS
BEGIN
    IF p_amount < 500 THEN
        RETURN 0;
    ELSIF p_amount < 1000 THEN
        RETURN p_amount * 0.05;
    ELSE
        RETURN p_amount * 0.10;
    END IF;
END;
/