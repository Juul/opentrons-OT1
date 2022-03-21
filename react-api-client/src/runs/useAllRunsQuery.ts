import { HostConfig, RunSummaries, getRuns } from '@opentrons/api-client'
import { UseQueryResult, useQuery } from 'react-query'
import { useHost } from '../api'

export function useAllRunsQuery(): UseQueryResult<RunSummaries> {
  const host = useHost()
  const query = useQuery(
    [host, 'runs', 'details'],
    () => getRuns(host as HostConfig).then(response => response.data),
    { enabled: host !== null }
  )

  return query
}