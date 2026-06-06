import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { postQuery, getHealth, uploadPdfs } from '@/services/api'
import type { ChatMessage, HealthResponse, IngestResponse, QueryResponse } from '@/types'

// ---------------------------------------------------------------------------
// Helper – crypto uuid shim (browser + Node compatible)
// ---------------------------------------------------------------------------
function newId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  // Fallback: timestamp + random
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

// ---------------------------------------------------------------------------
// Store shape
// ---------------------------------------------------------------------------
interface AgentStore {
  // Chat
  messages:    ChatMessage[]
  isLoading:   boolean
  error:       string | null

  // Health / sidebar
  health:      HealthResponse | null
  healthError: string | null

  // Currently selected message (for pipeline trace panel)
  selectedId:  string | null

  // PDF ingestion
  isIngesting:  boolean
  ingestResult: IngestResponse | null
  ingestError:  string | null

  // Actions
  sendQuestion:  (question: string) => Promise<void>
  selectMessage: (id: string | null) => void
  clearChat:     () => void
  fetchHealth:   () => Promise<void>
  ingestPdfs:    (files: File[], replace?: boolean) => Promise<void>
}

// ---------------------------------------------------------------------------
// Store implementation
// ---------------------------------------------------------------------------
export const useAgentStore = create<AgentStore>()(
  devtools(
    (set) => ({
      messages:    [],
      isLoading:   false,
      error:       null,
      health:      null,
      healthError: null,
      selectedId:  null,
      isIngesting:  false,
      ingestResult: null,
      ingestError:  null,

      // ------------------------------------------------------------------
      sendQuestion: async (question: string) => {
        const userMsg: ChatMessage = {
          id:        newId(),
          role:      'user',
          content:   question,
          timestamp: new Date(),
        }

        set((s) => ({
          messages:  [...s.messages, userMsg],
          isLoading: true,
          error:     null,
        }))

        try {
          const response: QueryResponse = await postQuery({ question })

          const assistantMsg: ChatMessage = {
            id:        newId(),
            role:      'assistant',
            content:   response.final_answer,
            timestamp: new Date(),
            response,
          }

          set((s) => ({
            messages:   [...s.messages, assistantMsg],
            isLoading:  false,
            selectedId: assistantMsg.id,
          }))
        } catch (err) {
          const msg = err instanceof Error ? err.message : 'Request failed'
          set({ isLoading: false, error: msg })
        }
      },

      // ------------------------------------------------------------------
      selectMessage: (id) => set({ selectedId: id }),

      // ------------------------------------------------------------------
      clearChat: () =>
        set({ messages: [], selectedId: null, error: null }),

      // ------------------------------------------------------------------
      fetchHealth: async () => {
        try {
          const health = await getHealth()
          set({ health, healthError: null })
        } catch (err) {
          const msg = err instanceof Error ? err.message : 'Health check failed'
          set({ healthError: msg })
        }
      },

      // ------------------------------------------------------------------
      ingestPdfs: async (files: File[], replace = false) => {
        set({ isIngesting: true, ingestResult: null, ingestError: null })
        try {
          const result = await uploadPdfs(files, replace)
          set({ isIngesting: false, ingestResult: result })
        } catch (err) {
          const msg = err instanceof Error ? err.message : 'Ingestion failed'
          set({ isIngesting: false, ingestError: msg })
        }
      },
    }),
    { name: 'AgentStore' },
  ),
)
