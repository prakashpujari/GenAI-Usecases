import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, Container } from '@mui/material'

import DashboardLayout from '@components/layout/DashboardLayout'
import Dashboard from '@pages/Dashboard'
import LoanIngestion from '@pages/LoanIngestion'
import RiskAnalysis from '@pages/RiskAnalysis'
import GraphExplorer from '@pages/GraphExplorer'
import JobsMonitor from '@pages/JobsMonitor'

function App() {
  return (
    <DashboardLayout>
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/loans" element={<LoanIngestion />} />
          <Route path="/risk" element={<RiskAnalysis />} />
          <Route path="/graph" element={<GraphExplorer />} />
          <Route path="/jobs" element={<JobsMonitor />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
    </DashboardLayout>
  )
}

export default App
