-- TC-008: Database Indexing and Query Efficiency (PERF09 violations)
-- Expected: PERF09 findings for missing index and inefficient query patterns
-- Technology: PostgreSQL SQL

-- ============================================================
-- SCHEMA SETUP (for context)
-- ============================================================

CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    email       VARCHAR(255) NOT NULL,
    status      VARCHAR(50)  NOT NULL,  -- 'active', 'inactive', 'suspended'
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    country     VARCHAR(2)   NOT NULL
    -- NOTE: No index on (status), (email), or (country) — violations below
    -- are detectable from schema + queries
);

CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT       NOT NULL REFERENCES users(id),
    total_cents INTEGER      NOT NULL,
    status      VARCHAR(50)  NOT NULL,
    placed_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
    -- NOTE: No index on (user_id) — foreign key with no supporting index
);


-- ============================================================
-- VIOLATION 1: Unindexed filter on large table
-- ============================================================

-- VIOLATION: users.status has no index. With millions of users this triggers
-- a sequential scan. Called on every active-users dashboard load (high frequency).
SELECT id, email, created_at
FROM   users
WHERE  status = 'active'        -- VIOLATION: no index on status
ORDER  BY created_at DESC
LIMIT  100;


-- ============================================================
-- VIOLATION 2: Function applied to indexed column (hypothetical index on email)
-- ============================================================

-- VIOLATION: LOWER() prevents the index on email from being used.
-- A functional index or case-insensitive collation should be used instead.
SELECT id, email
FROM   users
WHERE  LOWER(email) = LOWER('User@Example.COM');  -- VIOLATION: function on column


-- ============================================================
-- VIOLATION 3: Leading wildcard LIKE prevents index use
-- ============================================================

-- VIOLATION: Leading '%' forces a full scan. Only trailing wildcards
-- can use a B-tree index.
SELECT id, email
FROM   users
WHERE  email LIKE '%@example.com';  -- VIOLATION: leading wildcard


-- ============================================================
-- VIOLATION 4: Missing index on foreign key used in JOIN
-- ============================================================

-- VIOLATION: orders.user_id has no index. Every join between users and orders
-- requires a full scan of the orders table.
SELECT u.email, COUNT(o.id) AS order_count
FROM   users u
JOIN   orders o ON o.user_id = u.id  -- VIOLATION: no index on orders.user_id
WHERE  u.country = 'US'
GROUP  BY u.email;


-- ============================================================
-- VIOLATION 5: SELECT * on large table in a hot list query
-- ============================================================

-- VIOLATION: Fetches all columns including potentially large text fields
-- when the caller only needs id, email, and status.
SELECT *                            -- VIOLATION: over-fetching
FROM   users
WHERE  status = 'active';


-- ============================================================
-- SAFE IMPLEMENTATIONS
-- ============================================================

-- SAFE 1: Add index on status (with CONCURRENTLY to avoid table lock)
CREATE INDEX CONCURRENTLY idx_users_status ON users (status);

-- SAFE 2: Functional index for case-insensitive email lookup
CREATE UNIQUE INDEX idx_users_email_lower ON users (LOWER(email));

-- SAFE 2 query (now index-capable):
SELECT id, email
FROM   users
WHERE  LOWER(email) = 'user@example.com';

-- SAFE 3: Use trigram index for full-text LIKE or switch to text search
-- (for suffix/contains matching; out of scope for basic B-tree)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_users_email_trgm ON users USING gin (email gin_trgm_ops);

-- SAFE 4: Index on foreign key
CREATE INDEX idx_orders_user_id ON orders (user_id);

-- SAFE 5: Projected query — only needed columns
SELECT id, email, status
FROM   users
WHERE  status = 'active'
ORDER  BY created_at DESC
LIMIT  100;


-- ============================================================
-- NOT APPLICABLE: Small lookup table — no index needed
-- ============================================================

CREATE TABLE countries (
    code        CHAR(2)      PRIMARY KEY,
    name        VARCHAR(100) NOT NULL
    -- 250 rows maximum; full scan is acceptable and no index is required.
    -- PERF09 should NOT be flagged for queries against this table.
);

SELECT code, name FROM countries WHERE code = 'US';

