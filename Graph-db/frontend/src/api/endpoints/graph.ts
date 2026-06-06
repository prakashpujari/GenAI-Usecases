import { httpClient } from '../client'
import { GraphQueryRequest, GraphQueryResponse, NodeDetailsResponse } from '../types'

export const graphApi = {
  /**
   * Execute a custom Cypher query against Neo4j
   */
  queryGraph: (request: GraphQueryRequest) =>
    httpClient.post<GraphQueryResponse>('/graph/query', request),

  /**
   * Get details about a specific node
   */
  getNodeDetails: (nodeId: string) =>
    httpClient.get<NodeDetailsResponse>(`/graph/nodes/${nodeId}`),

  /**
   * Find shortest path between two nodes
   */
  getPathBetween: (startNodeId: string, endNodeId: string, maxLength = 5) =>
    httpClient.get<GraphQueryResponse>('/graph/paths', {
      params: { start: startNodeId, end: endNodeId, maxLength },
    }),
}
