CREATE INDEX loan_risk_score_idx IF NOT EXISTS FOR (n:Loan) ON (n.riskScore);
CREATE INDEX loan_network_risk_score_idx IF NOT EXISTS FOR (n:Loan) ON (n.networkRiskScore);
CREATE INDEX loan_fraud_community_idx IF NOT EXISTS FOR (n:Loan) ON (n.fraudCommunity);
