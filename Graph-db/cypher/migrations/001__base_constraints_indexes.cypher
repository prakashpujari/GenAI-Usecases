CREATE CONSTRAINT borrower_id_unique IF NOT EXISTS FOR (n:Borrower) REQUIRE n.borrowerId IS UNIQUE;
CREATE CONSTRAINT loan_id_unique IF NOT EXISTS FOR (n:Loan) REQUIRE n.loanId IS UNIQUE;
CREATE CONSTRAINT property_id_unique IF NOT EXISTS FOR (n:Property) REQUIRE n.propertyId IS UNIQUE;
CREATE CONSTRAINT income_id_unique IF NOT EXISTS FOR (n:IncomeSource) REQUIRE n.incomeId IS UNIQUE;
CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (n:Document) REQUIRE n.documentId IS UNIQUE;
CREATE CONSTRAINT rule_id_unique IF NOT EXISTS FOR (n:UnderwritingRule) REQUIRE n.ruleId IS UNIQUE;
CREATE CONSTRAINT reg_id_unique IF NOT EXISTS FOR (n:Regulation) REQUIRE n.regId IS UNIQUE;
CREATE INDEX loan_status_idx IF NOT EXISTS FOR (n:Loan) ON (n.status);
CREATE INDEX borrower_name_idx IF NOT EXISTS FOR (n:Borrower) ON (n.name);
