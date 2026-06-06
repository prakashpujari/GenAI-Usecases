import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider } from '@mui/material'
import {
  Dashboard as DashboardIcon,
  AccountBalance as LoansIcon,
  TrendingUp as RiskIcon,
  AccountTree as GraphIcon,
  Settings as JobsIcon,
} from '@mui/icons-material'

interface NavItem {
  label: string
  path: string
  icon: React.ReactNode
}

const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Loan Ingestion', path: '/loans', icon: <LoansIcon /> },
  { label: 'Risk & Explain', path: '/risk', icon: <RiskIcon /> },
  { label: 'Graph Explorer', path: '/graph', icon: <GraphIcon /> },
  { label: 'Jobs Monitor', path: '/jobs', icon: <JobsIcon /> },
]

interface SidebarNavProps {
  onItemClick?: () => void
}

const SidebarNav: React.FC<SidebarNavProps> = ({ onItemClick }) => {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const handleNavigate = (path: string) => {
    navigate(path)
    onItemClick?.()
  }

  return (
    <List>
      {navItems.map((item) => (
        <ListItem key={item.path} disablePadding>
          <ListItemButton
            selected={pathname === item.path}
            onClick={() => handleNavigate(item.path)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  )
}

export default SidebarNav
