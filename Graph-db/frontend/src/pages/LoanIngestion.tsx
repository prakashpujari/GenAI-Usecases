import React, { useState } from 'react'
import { Box, Grid, Paper, Typography, TextField, Button, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Alert } from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import { useIngestLoanMutation, useLoansQuery } from '@hooks/useLoans'
import { LoanIngestPayload } from '@api/types'
import { useLoanStore } from '@store/loans'

const LoanIngestion: React.FC = () => {
  const { mutate: ingestLoan, isPending } = useIngestLoanMutation()
  const { data: loansList, isLoading: loansLoading } = useLoansQuery(10, 0)
  const { formState, setFormState } = useLoanStore()

  const [unsavedChanges, setUnsavedChanges] = useState(false)

  const handleFormChange = (field: string, value: unknown) => {
    setFormState({
      ...formState!,
      [field]: value,
    })
    setUnsavedChanges(true)
  }

  const handleSubmit = () => {
    if (!formState) return
    ingestLoan(formState, {
      onSuccess: () => {
        setFormState(null)
        setUnsavedChanges(false)
      },
    })
  }

  const isFormValid =
    formState?.borrower.borrowerId &&
    formState?.loan.loanId &&
    formState?.property.propertyId &&
    formState?.income.incomeId

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Loan Ingestion
      </Typography>

      <Grid container spacing={3}>
        {/* Form Panel */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Submit New Loan
            </Typography>

            {unsavedChanges && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                You have unsaved changes
              </Alert>
            )}

            {/* Borrower Section */}
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 600 }}>
              Borrower Information
            </Typography>
            <TextField
              fullWidth
              label="Borrower ID"
              size="small"
              value={formState?.borrower.borrowerId || ''}
              onChange={(e) => handleFormChange('borrower', { ...formState?.borrower, borrowerId: e.target.value })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="Full Name"
              size="small"
              value={formState?.borrower.name || ''}
              onChange={(e) => handleFormChange('borrower', { ...formState?.borrower, name: e.target.value })}
              sx={{ mb: 2 }}
            />

            {/* Loan Section */}
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 600 }}>
              Loan Details
            </Typography>
            <TextField
              fullWidth
              label="Loan ID"
              size="small"
              value={formState?.loan.loanId || ''}
              onChange={(e) => handleFormChange('loan', { ...formState?.loan, loanId: e.target.value })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="Loan Amount ($)"
              type="number"
              size="small"
              value={formState?.loan.amount || 0}
              onChange={(e) => handleFormChange('loan', { ...formState?.loan, amount: parseFloat(e.target.value) })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="Purpose"
              size="small"
              value={formState?.loan.purpose || ''}
              onChange={(e) => handleFormChange('loan', { ...formState?.loan, purpose: e.target.value })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="LTV (%)"
              type="number"
              size="small"
              value={formState?.loan.ltv || 0}
              onChange={(e) => handleFormChange('loan', { ...formState?.loan, ltv: parseFloat(e.target.value) })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="DTI (%)"
              type="number"
              size="small"
              value={formState?.loan.dti || 0}
              onChange={(e) => handleFormChange('loan', { ...formState?.loan, dti: parseFloat(e.target.value) })}
              sx={{ mb: 2 }}
            />

            {/* Property Section */}
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 600 }}>
              Property Information
            </Typography>
            <TextField
              fullWidth
              label="Property ID"
              size="small"
              value={formState?.property.propertyId || ''}
              onChange={(e) => handleFormChange('property', { ...formState?.property, propertyId: e.target.value })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="Address"
              size="small"
              value={formState?.property.address || ''}
              onChange={(e) => handleFormChange('property', { ...formState?.property, address: e.target.value })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="City"
              size="small"
              value={formState?.property.city || ''}
              onChange={(e) => handleFormChange('property', { ...formState?.property, city: e.target.value })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="State"
              size="small"
              value={formState?.property.state || ''}
              onChange={(e) => handleFormChange('property', { ...formState?.property, state: e.target.value })}
              sx={{ mb: 2 }}
            />

            {/* Income Section */}
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 600 }}>
              Income Information
            </Typography>
            <TextField
              fullWidth
              label="Income ID"
              size="small"
              value={formState?.income.incomeId || ''}
              onChange={(e) => handleFormChange('income', { ...formState?.income, incomeId: e.target.value })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="Employer Name"
              size="small"
              value={formState?.income.employerName || ''}
              onChange={(e) => handleFormChange('income', { ...formState?.income, employerName: e.target.value })}
              sx={{ mb: 1 }}
            />
            <TextField
              fullWidth
              label="Annual Income ($)"
              type="number"
              size="small"
              value={formState?.income.annualIncome || 0}
              onChange={(e) => handleFormChange('income', { ...formState?.income, annualIncome: parseFloat(e.target.value) })}
              sx={{ mb: 2 }}
            />

            {/* Submit Button */}
            <Button
              variant="contained"
              fullWidth
              startIcon={isPending ? <CircularProgress size={20} /> : <AddIcon />}
              onClick={handleSubmit}
              disabled={!isFormValid || isPending}
              sx={{ mt: 2 }}
            >
              {isPending ? 'Submitting...' : 'Submit Loan'}
            </Button>
          </Paper>
        </Grid>

        {/* Recent Loans List */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Recent Submissions
            </Typography>

            {loansLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                      <TableCell>Loan ID</TableCell>
                      <TableCell>Borrower</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell align="center">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {loansList?.items.map((loan) => (
                      <TableRow key={loan.loanId}>
                        <TableCell sx={{ fontSize: '0.875rem' }}>{loan.loanId}</TableCell>
                        <TableCell sx={{ fontSize: '0.875rem' }}>{loan.borrowerName}</TableCell>
                        <TableCell align="right" sx={{ fontSize: '0.875rem' }}>
                          ${loan.amount.toLocaleString()}
                        </TableCell>
                        <TableCell align="center">
                          <Typography
                            variant="caption"
                            sx={{
                              backgroundColor: loan.status === 'ingested' ? '#c8e6c9' : '#fff9c4',
                              px: 1,
                              py: 0.5,
                              borderRadius: 1,
                              textTransform: 'capitalize',
                            }}
                          >
                            {loan.status}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default LoanIngestion
