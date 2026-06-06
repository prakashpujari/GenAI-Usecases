import { create } from 'zustand'
import { LoanIngestPayload, LoanSummary } from '@api/types'

interface LoanStore {
  // Selected loan for risk/explain queries
  selectedLoanId: string | null
  setSelectedLoanId: (id: string | null) => void

  // Recent loans cache
  recentLoans: LoanSummary[]
  addRecentLoan: (loan: LoanSummary) => void
  clearRecentLoans: () => void

  // Form draft state
  formState: LoanIngestPayload | null
  setFormState: (state: LoanIngestPayload | null) => void
}

const emptyLoanPayload: LoanIngestPayload = {
  borrower: {
    borrowerId: '',
    name: '',
    ssnHash: null,
    dob: null,
  },
  loan: {
    loanId: '',
    amount: 0,
    status: 'submitted',
    purpose: '',
    originationDate: null,
    ltv: 0,
    dti: 0,
  },
  property: {
    propertyId: '',
    address: '',
    city: '',
    state: '',
    zip: '',
    type: '',
  },
  income: {
    incomeId: '',
    type: 'w2',
    employerName: '',
    annualIncome: 0,
    startDate: null,
  },
  documents: [],
}

export const useLoanStore = create<LoanStore>((set) => ({
  selectedLoanId: null,
  setSelectedLoanId: (id) => set({ selectedLoanId: id }),

  recentLoans: [],
  addRecentLoan: (loan) =>
    set((state) => ({
      recentLoans: [loan, ...state.recentLoans.filter((l) => l.loanId !== loan.loanId)].slice(0, 20),
    })),
  clearRecentLoans: () => set({ recentLoans: [] }),

  formState: emptyLoanPayload,
  setFormState: (state) => set({ formState: state || emptyLoanPayload }),
}))
