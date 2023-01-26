import { LabwareOffset } from '@opentrons/api-client'
import { useRunQuery } from '@opentrons/react-api-client'
import { getLoadedLabwareDefinitionsByUri } from '@opentrons/shared-data'

import { useProtocolDetailsForRun } from '../../Devices/hooks'
import { getCurrentOffsetForLabwareInLocation } from '../../Devices/ProtocolRun/utils/getCurrentOffsetForLabwareInLocation'
import { getLabwareDefinitionUri } from '../../Devices/ProtocolRun/utils/getLabwareDefinitionUri'
import { getLabwareOffsetLocation } from '../../Devices/ProtocolRun/utils/getLabwareOffsetLocation'

export function useLabwareOffsetForLabware(
  runId: string,
  labwareId: string
): LabwareOffset | null {
  const { protocolData } = useProtocolDetailsForRun(runId)
  const { data: runRecord } = useRunQuery(runId)

  if (protocolData == null) return null
  const labwareDefinitionsByUri = getLoadedLabwareDefinitionsByUri(
    protocolData.commands
  )
  const labwareDefinitionUri = getLabwareDefinitionUri(
    labwareId,
    protocolData.labware,
    labwareDefinitionsByUri
  )

  const labwareLocation = getLabwareOffsetLocation(
    labwareId,
    protocolData?.commands ?? [],
    protocolData.modules
  )
  if (labwareLocation == null) return null
  const labwareOffsets = runRecord?.data?.labwareOffsets ?? []

  return (
    getCurrentOffsetForLabwareInLocation(
      labwareOffsets,
      labwareDefinitionUri,
      labwareLocation
    ) ?? null
  )
}
