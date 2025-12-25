-- Table for storing stock and financial indicators data
CREATE TABLE IF NOT EXISTS stock_indicators (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    price_min DECIMAL(10,2),
    price_max DECIMAL(10,2),
    p_target DECIMAL(10,2),
    is_net_income BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    p_l DECIMAL(10,2),
    dy DECIMAL(10,2),
    p_vp DECIMAL(10,2),
    p_ebit DECIMAL(10,2),
    p_ativo DECIMAL(10,2),
    ev_ebit DECIMAL(10,2),
    margem_bruta DECIMAL(10,2),
    margem_ebit DECIMAL(10,2),
    margem_liquida DECIMAL(10,2),
    p_sr DECIMAL(10,2),
    p_ativo_circulante DECIMAL(10,2),
    giro_ativos DECIMAL(10,2),
    roe DECIMAL(10,2),
    roa DECIMAL(10,2),
    pl_ativo DECIMAL(10,2),
    passivo_ativo DECIMAL(10,2),
    peg_ratio DECIMAL(10,2),
    receitas_cagr5 DECIMAL(10,2),
    lucros_cagr5 DECIMAL(10,2),
    liquidez_media_diaria DECIMAL(20,2),
    vpa DECIMAL(10,2),
    lpa DECIMAL(10,2),
    valor_mercado DECIMAL(20,2),
    segment_id INTEGER,
    sector_id INTEGER,
    subsector_id INTEGER,
    subsector_name VARCHAR(100),
    segment_name VARCHAR(100),
    sector_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_ticker UNIQUE (ticker),
    CONSTRAINT positive_price CHECK (price >= 0),
    CONSTRAINT positive_valor_mercado CHECK (valor_mercado >= 0)
);

-- Indexes for better query performance
CREATE INDEX idx_stock_indicators_ticker ON stock_indicators(ticker);
CREATE INDEX idx_stock_indicators_company_id ON stock_indicators(company_id);
CREATE INDEX idx_stock_indicators_sector_id ON stock_indicators(sector_id);

-- Trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_stock_indicators_updated_at
    BEFORE UPDATE ON stock_indicators
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 


--docker exec -i yfinance-postgres psql -U postgres -d yfinance < src_refator_version/database/schema.sql