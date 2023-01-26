import { storedProtocolData } from '../../../../redux/protocol-storage/__fixtures__'

import type {
  LoadedLabwareEntity,
  ModuleModelsById,
  PipetteNamesById,
} from '@opentrons/api-client'
import type { StoredProtocolAnalysis } from '../useStoredProtocolAnalysis'

export const LABWARE_ENTITY: LoadedLabwareEntity = {
  id: 'labware-0',
  loadName: 'fakeLoadName',
  definitionUri: 'fakeLabwareDefinitionUri',
  displayName: 'a fake labware',
}
export const MODULE_MODELS_BY_ID: ModuleModelsById = {
  'module-0': { model: 'thermocyclerModuleV1' },
}
export const PIPETTE_NAME_BY_ID: PipetteNamesById = {
  id: 'pipette-0',
  pipetteName: 'p10_single',
}

export const STORED_PROTOCOL_ANALYSIS = {
  ...storedProtocolData.mostRecentAnalysis,
  modules: MODULE_MODELS_BY_ID,
  labware: [LABWARE_ENTITY],
  pipettes: [PIPETTE_NAME_BY_ID],
} as StoredProtocolAnalysis
