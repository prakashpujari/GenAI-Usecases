import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface GraphStore {
  // Cypher query
  cypher: string
  setCypher: (query: string) => void

  // Selection state
  selectedNodeId: string | null
  setSelectedNodeId: (id: string | null) => void

  // Layout options
  graphLayout: 'force' | 'grid' | 'circle'
  setGraphLayout: (layout: 'force' | 'grid' | 'circle') => void

  // UI state
  showLegend: boolean
  setShowLegend: (show: boolean) => void

  showFilters: boolean
  setShowFilters: (show: boolean) => void

  // Filtered node types (for legend filtering)
  visibleNodeTypes: string[]
  toggleNodeTypeVisibility: (type: string) => void

  // Query presets
  presetQueries: Record<string, string>
  addPresetQuery: (name: string, cypher: string) => void
}

export const useGraphStore = create<GraphStore>()(
  persist(
    (set) => ({
      cypher: 'MATCH (n) LIMIT 50 RETURN n',
      setCypher: (query) => set({ cypher: query }),

      selectedNodeId: null as string | null,
      setSelectedNodeId: (id) => set({ selectedNodeId: id }),

      graphLayout: 'force',
      setGraphLayout: (layout) => set({ graphLayout: layout }),

      showLegend: true,
      setShowLegend: (show) => set({ showLegend: show }),

      showFilters: false,
      setShowFilters: (show) => set({ showFilters: show }),

      visibleNodeTypes: ['Borrower', 'Loan', 'Property', 'IncomeSource', 'Document', 'UnderwritingRule', 'Regulation'],
      toggleNodeTypeVisibility: (type) =>
        set((state) => ({
          visibleNodeTypes: state.visibleNodeTypes.includes(type)
            ? state.visibleNodeTypes.filter((t) => t !== type)
            : [...state.visibleNodeTypes, type],
        })),

      presetQueries: {
        'All Loans': 'MATCH (n:Loan) LIMIT 50 RETURN n',
        'Loan Network': 'MATCH (l:Loan)-[r]->(n) LIMIT 100 RETURN l, r, n',
        'High-Risk Loans': 'MATCH (l:Loan) WHERE l.riskScore > 70 RETURN l LIMIT 50',
        'Recent Ingestions': 'MATCH (b:Borrower)-[:OWNS]->(l:Loan) RETURN b, l ORDER BY l.createdAt DESC LIMIT 50',
      },
      addPresetQuery: (name, cypher) =>
        set((state) => ({
          presetQueries: { ...state.presetQueries, [name]: cypher },
        })),
    }),
    {
      name: 'graph-store',
      partialize: (state) => ({
        graphLayout: state.graphLayout,
        visibleNodeTypes: state.visibleNodeTypes,
        presetQueries: state.presetQueries,
      }),
    },
  ),
)
