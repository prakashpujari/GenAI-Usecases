import React, { useState } from 'react'
import { Box, Grid, Paper, Typography, TextField, Button, CircularProgress, Tabs, Tab, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, LinearProgress } from '@mui/material'
import { Search as SearchIcon } from '@mui/icons-material'
import { useRiskQuery, useExplainQuery } from '@hooks/useRisk'
import { useLoanStore } from '@store/loans'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
    </div>
  )
}

const RiskAnalysis: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [loanIdInput, setLoanIdInput] = useState('')
  const { selectedLoanId, setSelectedLoanId } = useLoanStore()

  const { data: risk, isLoading: riskLoading, error: riskError } = useRiskQuery(selectedLoanId || undefined)
  const { data: explain, isLoading: explainLoading, error: explainError } = useExplainQuery(selectedLoanId || undefined)

  const handleSearch = () => {
    setSelectedLoanId(loanIdInput.trim() || null)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Risk & Explainability Analysis
      </Typography>

      {/* Search Panel */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Search Loan
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            label="Enter Loan ID"
            value={loanIdInput}
            onChange={(e) => setLoanIdInput(e.target.value)}
            onKeyPress={handleKeyPress}
            size="small"
            sx={{ flex: 1 }}
          />
          <Button variant="contained" startIcon={<SearchIcon />} onClick={handleSearch}>
            Search
          </Button>
        </Box>
      </Paper>

      {!selectedLoanId ? (
        <Alert severity="info">Enter a Loan ID to view risk metrics and explainability details.</Alert>
      ) : (
        <Grid container spacing={3}>
          {/* Risk Metrics */}
          {riskError && (
            <Grid item xs={12}>
              <Alert severity="error">{String(riskError)}</Alert>
            </Grid>
          )}

          {riskLoading ? (
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                <CircularProgress />
              </Box>
            </Grid>
          ) : risk ? (
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Risk Metrics
                </Typography>

                {/* Risk Score Gauge */}
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Composite Risk Score</Typography>
                    <Typography variant="h5" sx={{ color: risk.riskScore > 70 ? 'error.main' : risk.riskScore > 40 ? 'warning.main' : 'success.main' }}>
                      {risk.riskScore.toFixed(1)}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={risk.riskScore}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: risk.riskScore > 70 ? '#f44336' : risk.riskScore > 40 ? '#ff9800' : '#4caf50',
                      },
                    }}
                  />
                </Box>

                {/* Key Metrics Table */}
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 500 }}>LTV</TableCell>
                        <TableCell align="right">{risk.ltv.toFixed(2)}%</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 500 }}>DTI</TableCell>
                        <TableCell align="right">{risk.dti.toFixed(2)}%</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 500 }}>Network Risk Score</TableCell>
                        <TableCell align="right">{risk.networkRiskScore.toFixed(2)}</TableCell>
                      </TableRow>
                      {risk.fraudCommunity !== undefined && (
                        <TableRow>
                          <TableCell sx={{ fontWeight: 500 }}>Fraud Community</TableCell>
                          <TableCell align="right">{risk.fraudCommunity}</TableCell>
                        </TableRow>
                      )}
                      {risk.riskCentrality !== undefined && (
                        <TableRow>
                          <TableCell sx={{ fontWeight: 500 }}>Risk Centrality</TableCell>
                          <TableCell align="right">{risk.riskCentrality.toFixed(4)}</TableCell>
                        </TableRow>
                      )}
                      {risk.sharedContacts !== undefined && (
                        <TableRow>
                          <TableCell sx={{ fontWeight: 500 }}>Shared Contacts</TableCell>
                          <TableCell align="right">{risk.sharedContacts}</TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>

                {risk.violations.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 500, mb: 1 }}>
                      Violations
                    </Typography>
                    <Box sx={{ backgroundColor: '#ffebee', p: 1.5, borderRadius: 1 }}>
                      {risk.violations.map((violation, idx) => (
                        <Typography key={idx} variant="caption" sx={{ display: 'block', color: '#c62828' }}>
                          • {violation}
                        </Typography>
                      ))}
                    </Box>
                  </Box>
                )}
              </Paper>
            </Grid>
          ) : null}

          {/* Rules & Regulations */}
          {explainError && (
            <Grid item xs={12}>
              <Alert severity="error">{String(explainError)}</Alert>
            </Grid>
          )}

          {explainLoading ? (
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                <CircularProgress />
              </Box>
            </Grid>
          ) : explain ? (
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Tabs value={tabValue} onChange={(_, val) => setTabValue(val)}>
                  <Tab label={`Rules (${explain.rules.length})`} />
                  <Tab label={`Regulations (${explain.regulations.length})`} />
                  <Tab label={`Graph Signals (${explain.graphSignals.length})`} />
                </Tabs>

                <TabPanel value={tabValue} index={0}>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                          <TableCell>Rule ID</TableCell>
                          <TableCell>Name</TableCell>
                          <TableCell>Severity</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {explain.rules.map((rule) => (
                          <TableRow key={rule.ruleId}>
                            <TableCell sx={{ fontSize: '0.875rem' }}>{rule.ruleId}</TableCell>
                            <TableCell sx={{ fontSize: '0.875rem' }}>{rule.name}</TableCell>
                            <TableCell>
                              <Typography
                                variant="caption"
                                sx={{
                                  backgroundColor:
                                    rule.severity === 'critical'
                                      ? '#f44336'
                                      : rule.severity === 'high'
                                        ? '#ff9800'
                                        : rule.severity === 'medium'
                                          ? '#ffc107'
                                          : '#4caf50',
                                  color: '#fff',
                                  px: 1,
                                  py: 0.5,
                                  borderRadius: 1,
                                  textTransform: 'capitalize',
                                }}
                              >
                                {rule.severity}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </TabPanel>

                <TabPanel value={tabValue} index={1}>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                          <TableCell>Regulation ID</TableCell>
                          <TableCell>Name</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {explain.regulations.map((reg) => (
                          <TableRow key={reg.regulationId}>
                            <TableCell sx={{ fontSize: '0.875rem' }}>{reg.regulationId}</TableCell>
                            <TableCell sx={{ fontSize: '0.875rem' }}>{reg.regulationName}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </TabPanel>

                <TabPanel value={tabValue} index={2}>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                          <TableCell>Signal</TableCell>
                          <TableCell align="right">Value</TableCell>
                          <TableCell align="right">Contribution</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {explain.graphSignals.map((signal) => (
                          <TableRow key={signal.signalName}>
                            <TableCell sx={{ fontSize: '0.875rem' }}>{signal.signalName}</TableCell>
                            <TableCell align="right" sx={{ fontSize: '0.875rem' }}>
                              {signal.value.toFixed(4)}
                            </TableCell>
                            <TableCell align="right" sx={{ fontSize: '0.875rem' }}>
                              {(signal.contribution * 100).toFixed(1)}%
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </TabPanel>
              </Paper>
            </Grid>
          ) : null}
        </Grid>
      )}
    </Box>
  )
}

export default RiskAnalysis
