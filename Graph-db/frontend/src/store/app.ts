import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  name: string
  email: string
  role: 'viewer' | 'analyst' | 'admin'
}

interface AppState {
  // Layout
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void

  // Authentication (placeholder for future RBAC)
  user: User | null
  setUser: (user: User | null) => void
  isAuthenticated: boolean

  // API Configuration
  apiBaseUrl: string
  setApiBaseUrl: (url: string) => void

  // Theme
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Layout
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      // Auth
      user: null as User | null,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      isAuthenticated: false,

      // API
      apiBaseUrl: 'http://localhost:8000',
      setApiBaseUrl: (url: string) => set({ apiBaseUrl: url }),

      // Theme
      theme: 'light',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'app-store',
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        theme: state.theme,
        apiBaseUrl: state.apiBaseUrl,
      }),
    },
  ),
)
