import React, { useState } from 'react'
import { Box, Grid, Paper, Typography, TextField, Button, CircularProgress, Select, MenuItem, FormControl, InputLabel, Alert } from '@mui/material'
import { PlayArrow as PlayIcon, Refresh as RefreshIcon } from '@mui/icons-material'
import { useGraphQueryMutation } from '@hooks/useGraph'
import { useGraphStore } from '@store/graph'
import { GraphQueryRequest } from '@api/types'

const GraphExplorer: React.FC = () => {
  const { mutate: queryGraph, isPending, data: queryResult, error: queryError } = useGraphQueryMutation()
  const { cypher, setCypher, graphLayout, setGraphLayout, presetQueries } = useGraphStore()
  const [selectedPreset, setSelectedPreset] = useState('')

  const handleExecuteQuery = () => {
    const request: GraphQueryRequest = {
      cypher: cypher,
      params: {},
    }
    queryGraph(request)
  }

  const handlePresetSelect = (preset: string) => {
    setCypher(presetQueries[preset] || '')
    setSelectedPreset(preset)
  }

  const handleKeyDown = (e: any) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleExecuteQuery()
    }
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Graph Explorer
      </Typography>

      <Grid container spacing={3}>
        {/* Query Panel */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Cypher Query
            </Typography>

            {/* Presets */}
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>Preset Queries</InputLabel>
              <Select value={selectedPreset} onChange={(e) => handlePresetSelect(e.target.value)} label="Preset Queries">
                <MenuItem value="">-- Custom Query --</MenuItem>
                {Object.keys(presetQueries).map((name) => (
                  <MenuItem key={name} value={name}>
                    {name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Cypher Input */}
            <TextField
              label="Enter Cypher Query"
              value={cypher}
              onChange={(e) => setCypher(e.target.value)}
              onKeyDown={handleKeyDown}
              multiline
              rows={8}
              fullWidth
              variant="outlined"
              sx={{ mb: 2, fontFamily: 'monospace', fontSize: '0.85rem' }}
              placeholder="MATCH (n) LIMIT 50 RETURN n"
            />

            {/* Graph Layout */}
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>Layout</InputLabel>
              <Select value={graphLayout} onChange={(e) => setGraphLayout(e.target.value as any)} label="Layout">
                <MenuItem value="force">Force-Directed</MenuItem>
                <MenuItem value="grid">Grid</MenuItem>
                <MenuItem value="circle">Circle</MenuItem>
              </Select>
            </FormControl>

            {/* Execute Button */}
            <Button
              variant="contained"
              fullWidth
              startIcon={isPending ? <CircularProgress size={20} /> : <PlayIcon />}
              onClick={handleExecuteQuery}
              disabled={isPending || !cypher.trim()}
            >
              {isPending ? 'Executing...' : 'Execute'}
            </Button>
          </Paper>
        </Grid>

        {/* Results Panel */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Results</Typography>
              <Button startIcon={<RefreshIcon />} onClick={handleExecuteQuery} disabled={isPending}>
                Refresh
              </Button>
            </Box>

            {queryError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {String(queryError)}
              </Alert>
            )}

            {!queryResult ? (
              <Alert severity="info">Execute a Cypher query to visualize graph data. Use presets or write custom Cypher.</Alert>
            ) : (
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Rows: {queryResult.rows.length}
                </Typography>

                {queryResult.rows.length > 0 ? (
                  <Box
                    sx={{
                      backgroundColor: '#f5f5f5',
                      p: 2,
                      borderRadius: 1,
                      maxHeight: '500px',
                      overflowY: 'auto',
                      fontFamily: 'monospace',
                      fontSize: '0.75rem',
                    }}
                  >
                    <pre>{JSON.stringify(queryResult.rows.slice(0, 20), null, 2)}</pre>
                  </Box>
                ) : (
                  <Alert severity="warning">No results returned. Check your Cypher query.</Alert>
                )}

                <Typography variant="caption" sx={{ mt: 2, display: 'block', color: 'textSecondary' }}>
                  Showing first 20 rows. Total: {queryResult.rows.length}
                </Typography>
              </Box>
            )}

            {/* Future: Cytoscape.js graph visualization would be integrated here */}
            <Alert severity="info" sx={{ mt: 2 }}>
              Graph visualization using Cytoscape.js will be rendered here in production. Currently showing query results in JSON format.
            </Alert>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default GraphExplorer
