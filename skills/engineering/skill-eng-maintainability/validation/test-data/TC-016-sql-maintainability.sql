-- TC-016: SQL Maintainability (MAINT04, MAINT14)
-- Demonstrates monolithic stored procedure combining 5 disparate business operations vs. modular procedures

-- --- VIOLATION ---
-- VIOLATION: Giant omnibus stored procedure that performs:
-- 1. Inventory stock deductions
-- 2. Customer credit balance adjustments
-- 3. PDF invoice archive logging
-- 4. Notification table queuing
-- 5. Audit trail writing
-- All combined into one 100+ line untestable SQL script.
CREATE OR REPLACE PROCEDURE sp_omnibus_checkout_violation(
    p_order_id INT,
    p_customer_id INT,
    p_amount DECIMAL(10,2),
    p_sku VARCHAR(50),
    p_qty INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1. Inventory deduction
    UPDATE inventory SET stock = stock - p_qty WHERE sku = p_sku;

    -- 2. Balance adjustment
    UPDATE customer_balances SET balance = balance - p_amount WHERE customer_id = p_customer_id;

    -- 3. Invoice record
    INSERT INTO invoices (order_id, amount, created_at) VALUES (p_order_id, p_amount, NOW());

    -- 4. Notification queue
    INSERT INTO notification_queue (recipient_id, message, queued_at)
    VALUES (p_customer_id, 'Your order has processed', NOW());

    -- 5. Audit trail
    INSERT INTO audit_logs (entity_type, entity_id, action, logged_at)
    VALUES ('ORDER', p_order_id, 'CHECKOUT_PROCESSED', NOW());
END;
$$;


-- --- SAFE IMPLEMENTATION ---
-- SAFE: Cohesive, single-responsibility procedures handling isolated domain updates.
CREATE OR REPLACE PROCEDURE sp_deduct_inventory_safe(
    p_sku VARCHAR(50),
    p_qty INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE inventory SET stock = stock - p_qty WHERE sku = p_sku;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_record_invoice_safe(
    p_order_id INT,
    p_amount DECIMAL(10,2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO invoices (order_id, amount, created_at) VALUES (p_order_id, p_amount, NOW());
END;
$$;

