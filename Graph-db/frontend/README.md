# Mortgage Graph Platform - React UI

A production-grade React + TypeScript frontend for the Mortgage Graph Platform, replacing the legacy Streamlit UI.

## Quick Start

### Prerequisites

- Node.js 20+
- npm or yarn
- Backend API running on http://localhost:8000 (or configured in .env.local)

### Development

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Start dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

### Building for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── api/                    # HTTP client and API endpoints
│   ├── client.ts          # Axios instance with error handling
│   ├── types.ts           # Shared API type definitions
│   └── endpoints/         # Feature-specific API modules
│       ├── loans.ts
│       ├── risk.ts
│       ├── graph.ts
│       ├── health.ts
│       └── jobs.ts
├── components/            # Reusable UI components
│   └── layout/           # Page layouts
├── pages/                # Route-level pages
│   ├── Dashboard.tsx
│   ├── LoanIngestion.tsx
│   ├── RiskAnalysis.tsx
│   ├── GraphExplorer.tsx
│   └── JobsMonitor.tsx
├── hooks/               # Custom React hooks
│   ├── useLoans.ts
│   ├── useRisk.ts
│   ├── useHealth.ts
│   └── useGraph.ts
├── store/              # Zustand state management
│   ├── app.ts
│   ├── loans.ts
│   └── graph.ts
├── App.tsx             # Root component
└── main.tsx            # Entry point
```

## Features

### Dashboard
- Real-time API health status
- Key metrics: total loans, average risk score
- Last GDS job status

### Loan Ingestion
- Form to submit loan bundles (borrower, loan, property, income, documents)
- Client-side validation with Zod
- Recent submissions table
- Unsaved changes warning

### Risk & Explainability
- Search loans by ID
- View risk metrics: composite score, LTV, DTI, network signals
- Display rules, regulations, and graph signal contributions
- Violation alerts

### Graph Explorer
- Execute custom Cypher queries
- Preset queries for common patterns
- Layout options: force-directed, grid, circle
- Results shown as JSON (Cytoscape visualization in progress)

### Jobs Monitor
- View active and recent GDS/ETL jobs
- Trigger jobs: project-fraud, project-risk, community-detection, centrality, similarity
- Real-time progress tracking with fallback polling
- View job logs

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 18 + TypeScript | Type-safe UI development |
| **Build** | Vite | Fast development and optimized builds |
| **UI Components** | Material-UI (MUI) | Professional, accessible components |
| **HTTP Client** | Axios | REST API communication with retry logic |
| **Server State** | React Query | Caching, fetching, synchronization |
| **Client State** | Zustand | Lightweight state management |
| **Styling** | Tailwind CSS + MUI | Utility-first + component styling |
| **Form Validation** | Zod | Runtime type validation |
| **Routing** | React Router v6 | Client-side navigation |
| **Notifications** | Sonner | Toast messages |
| **Graph Viz** | Cytoscape.js | (Future) Interactive graph rendering |

## Configuration

### Environment Variables

Create `.env.local` from `.env.example`:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_GRAPH_EXPLORER=true
VITE_ENABLE_JOB_MONITOR=true
VITE_ENABLE_RBAC=false

# Optional: Error Tracking
# VITE_SENTRY_DSN=https://...
```

## Development Workflows

### Adding a New Page

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation item in `src/components/layout/SidebarNav.tsx`

Example:

```typescript
// src/pages/MyNewPage.tsx
import React from 'react'
import { Box, Typography } from '@mui/material'

const MyNewPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4">My New Page</Typography>
      {/* ... */}
    </Box>
  )
}

export default MyNewPage
```

### Adding a New API Endpoint

1. Define types in `src/api/types.ts`
2. Create endpoint module in `src/api/endpoints/`
3. Create React Query hook in `src/hooks/`
4. Use hook in component with `useQuery` or `useMutation`

Example:

```typescript
// src/api/endpoints/example.ts
export const exampleApi = {
  getExample: (id: string) =>
    httpClient.get<ExampleResponse>(`/example/${id}`),
}

// src/hooks/useExample.ts
export const useExampleQuery = (id?: string) =>
  useQuery({
    queryKey: ['example', id],
    queryFn: () => exampleApi.getExample(id!),
    enabled: !!id,
  })

// In component
const { data } = useExampleQuery(id)
```

### Managing State

**Server State** (React Query): Use for data from backend
- Caching and deduplication
- Automatic refetching
- Mutation side effects (invalidation)

**Client State** (Zustand): Use for UI preferences
- Sidebar open/closed
- Form drafts
- Selected loan ID
- Graph layout preference

## Testing

### Unit Tests

```bash
npm test
npm test -- --watch
npm test -- --ui
```

### Build Check

```bash
npm run type-check
npm run lint
npm run build
```

## Performance

### Code Splitting
Routes are lazy-loaded to reduce initial bundle size:

```typescript
const GraphExplorer = lazy(() => import('@pages/GraphExplorer'))
```

### Caching Strategy
- **Loans**: 60s stale time (invalidated on ingest)
- **Risk**: 30s stale time
- **Health**: 10s stale (refetch every 30s)
- **Graph**: 30s stale time

### Bundle Size Targets
- Main: < 200KB (gzipped)
- CSS: < 50KB (gzipped)
- Per-route chunks: < 100KB (gzipped)

## Security

### Input Validation
- All form inputs validated with Zod
- Cypher queries validated on backend (blocklist dangerous patterns)
- XSS protection via React's default escaping

### Authentication (Future)
- JWT token support ready in HTTP client
- RBAC context placeholder in `useAppStore`
- Will be integrated with backend auth system

### API Security
- CORS configured on backend
- Rate limiting on expensive endpoints (graph queries)
- Timeout enforcement (20s default)

## Troubleshooting

### API Connection Issues

**Problem**: "Failed to fetch" errors

**Solutions**:
1. Check `VITE_API_BASE_URL` in `.env.local`
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check browser network tab for actual request URL
4. Ensure CORS is enabled on backend

### State Management Issues

**Problem**: Form state not persisting

**Solution**: Check Zustand persist middleware is working
```bash
# Browser DevTools → Application → LocalStorage
# Look for "loans-store" key
```

### Build Errors

**Problem**: TypeScript compilation errors

**Solutions**:
```bash
npm run type-check  # See all errors
npm run lint        # Check code style
```

## Deployment

### Docker

```bash
docker build -f frontend/Dockerfile -t mortgage-graph-frontend .
docker run -p 3000:3000 mortgage-graph-frontend
```

### Production Environment

Set environment variables before build:

```bash
VITE_API_BASE_URL=https://api.mortgage-graph.com npm run build
```

### Via Docker Compose

See `docker-compose.prod.yml` for full stack deployment.

## Support

- Development issues: Check `CLAUDE.md` for backend setup
- Component issues: Refer to [Material-UI docs](https://mui.com/)
- API integration: See `src/api/types.ts` for backend contract
- State management: See `src/store/` for store documentation

## License

Same as parent Mortgage Graph Platform project.
