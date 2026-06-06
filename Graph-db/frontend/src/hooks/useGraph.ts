import { useMutation, useQuery } from '@tanstack/react-query'
import { graphApi } from '@api/endpoints/graph'
import { GraphQueryRequest } from '@api/types'
import { handleApiError } from '@api/client'

const GRAPH_QUERY_KEY = (cypher: string) => ['graph', cypher]
const NODE_DETAILS_KEY = (nodeId: string) => ['node', nodeId]

/**
 * Hook to query Neo4j with Cypher
 */
export const useGraphQueryMutation = () => {
  return useMutation({
    mutationFn: (request: GraphQueryRequest) => graphApi.queryGraph(request),
    onError: (error: unknown) => {
      handleApiError(error, 'Failed to execute graph query')
    },
  })
}

/**
 * Hook to get node details
 */
export const useNodeDetailsQuery = (nodeId?: string) => {
  return useQuery({
    queryKey: NODE_DETAILS_KEY(nodeId || ''),
    queryFn: () => graphApi.getNodeDetails(nodeId!),
    enabled: !!nodeId,
    staleTime: 30000,
  })
}

/**
 * Hook to find path between two nodes
 */
export const usePathQuery = (startNodeId?: string, endNodeId?: string, maxLength = 5) => {
  return useQuery({
    queryKey: ['path', startNodeId, endNodeId, maxLength],
    queryFn: () => graphApi.getPathBetween(startNodeId!, endNodeId!, maxLength),
    enabled: !!startNodeId && !!endNodeId,
    staleTime: 30000,
  })
}
