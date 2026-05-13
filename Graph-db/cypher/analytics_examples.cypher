// High-risk loans inside high-risk communities
MATCH (l:Loan)
WHERE l.riskScore >= 70 AND l.networkRiskScore >= 60
RETURN l.loanId, l.riskScore, l.networkRiskScore, l.fraudCommunity
ORDER BY l.riskScore DESC;

// Properties securing multiple loans from unrelated borrowers in a time window
MATCH (p:Property)<-[:SECURED_BY]-(l:Loan)<-[:APPLIES_FOR]-(b:Borrower)
WHERE date(l.originationDate) >= date('2025-01-01')
WITH p, collect(DISTINCT l.loanId) AS loans, collect(DISTINCT b.borrowerId) AS borrowers
WHERE size(loans) > 1 AND size(borrowers) > 1
RETURN p.propertyId, loans, borrowers, size(loans) AS loanCount;

// Investigation utility: shortest path between borrowers through loan/property/document network
MATCH (b1:Borrower {borrowerId: $borrowerA}), (b2:Borrower {borrowerId: $borrowerB})
CALL gds.shortestPath.dijkstra.stream('fraudGraph', {
  sourceNode: id(b1),
  targetNode: id(b2)
})
YIELD totalCost, nodeIds
RETURN totalCost, nodeIds;
