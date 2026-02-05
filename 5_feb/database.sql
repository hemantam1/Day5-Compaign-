-- 1. Portfolios Table
CREATE DATABASE IF NOT EXISTS amazon_ads_db;
USE amazon_ads_db;
CREATE TABLE portfolios (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    budget_amount DECIMAL(10,2),
    budget_start DATE,
    budget_end DATE,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Campaigns Table (Linked to Portfolios)
CREATE TABLE campaigns (
    id VARCHAR(50) PRIMARY KEY,
    portfolio_id VARCHAR(50),
    name VARCHAR(255),
    type VARCHAR(50), -- SP, SB, SV
    status VARCHAR(50),
    daily_budget DECIMAL(10,2),
    targeting_type VARCHAR(50),
    bidding_strategy VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE SET NULL
);

-- 3. Products Table
CREATE TABLE products (
    id VARCHAR(50) PRIMARY KEY,
    asin VARCHAR(20) UNIQUE,
    name VARCHAR(500),
    price DECIMAL(10,2),
    margin DECIMAL(5,2),
    category VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Campaign Products (Jo batata hai kis campaign me konsa product hai)
CREATE TABLE campaign_products (
    id VARCHAR(50) PRIMARY KEY,
    campaign_id VARCHAR(50),
    product_id VARCHAR(50),
    bid DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 5. Performance Metrics (Yahan 1 Lakh Rows aayengi)
CREATE TABLE performance_metrics (
    id VARCHAR(50) PRIMARY KEY,
    campaign_id VARCHAR(50),
    date DATE,
    impressions INTEGER,
    clicks INTEGER,
    spend DECIMAL(10,2),
    sales DECIMAL(10,2),
    orders INTEGER,
    acos DECIMAL(5,2),
    roas DECIMAL(5,2),
    ctr DECIMAL(5,2),
    cpc DECIMAL(5,2),
    cvr DECIMAL(5,2),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

-- 6. AI Recommendations Table
CREATE TABLE ai_recommendations (
    id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50), 
    entity_id VARCHAR(50),
    recommendation_type VARCHAR(100),
    current_value TEXT,
    suggested_value TEXT,
    expected_impact JSON,
    confidence_score DECIMAL(3,2),
    status VARCHAR(50), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Automation Rules Table
CREATE TABLE automation_rules (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    condition_text TEXT,
    action_text TEXT,
    priority VARCHAR(50),
    enabled BOOLEAN DEFAULT TRUE,
    last_executed TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SHOW TABLES;
SELECT COUNT(*) FROM performance_metrics;
SELECT COUNT(*) FROM ai_recommendations;
SELECT COUNT(*) FROM campaigns;
SELECT COUNT(*) FROM campaign_products;
SELECT COUNT(*) FROM portfolios;
SELECT COUNT(*) FROM products;





SELECT 
    COUNT(*) as total_rows, 
    MIN(acos) as min_acos, 
    MAX(acos) as max_acos, 
    AVG(sales) as avg_sales 
FROM performance_metrics;