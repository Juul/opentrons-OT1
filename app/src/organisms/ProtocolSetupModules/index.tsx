import * as React from 'react'
// import { useTranslation } from 'react-i18next'
import {
  DIRECTION_COLUMN,
  Flex,
  // JUSTIFY_CENTER,
  SPACING,
  // useHoverTooltip,
} from '@opentrons/components'
import { getDeckDefFromRobotType } from '@opentrons/shared-data'

import { BackButton } from '../../atoms/buttons'
import { getProtocolModulesInfo } from '../../organisms/Devices/ProtocolRun/utils/getProtocolModulesInfo'
import { useMostRecentCompletedAnalysis } from '../../organisms/LabwarePositionCheck/useMostRecentCompletedAnalysis'
import { ROBOT_MODEL_OT3 } from '../../redux/discovery'
// import { useRunHasStarted, useUnmatchedModulesForProtocol } from '../../hooks'
// import { useToggleGroup } from '../../../../molecules/ToggleGroup/useToggleGroup'
// import { PrimaryButton } from '../../../../atoms/buttons'
// import { Tooltip } from '../../../../atoms/Tooltip'
// import { SetupModulesMap } from './SetupModulesMap'
// import { SetupModulesList } from './SetupModulesList'

import type { SetupScreens } from '../../pages/OnDeviceDisplay/ProtocolSetup'

interface ProtocolSetupModulesProps {
  // robotName: string
  runId: string
  setSetupScreen: React.Dispatch<React.SetStateAction<SetupScreens>>
}

/**
 * an ODD screen on the Protocol Setup page
 * @param param0
 * @returns
 */
export const ProtocolSetupModules = ({
  runId,
  setSetupScreen,
}: ProtocolSetupModulesProps): JSX.Element => {
  // const { t } = useTranslation('protocol_setup')
  // const [selectedValue, toggleGroup] = useToggleGroup(
  //   t('list_view'),
  //   t('map_view')
  // )
  // const { missingModuleIds } = useUnmatchedModulesForProtocol(robotName, runId)
  // const runHasStarted = useRunHasStarted(runId)
  // const [targetProps, tooltipProps] = useHoverTooltip()
  const mostRecentAnalysis = useMostRecentCompletedAnalysis(runId)
  console.log('mostRecentAnalysis', mostRecentAnalysis)
  const deckDef = getDeckDefFromRobotType(ROBOT_MODEL_OT3)
  // schema adapter adjustment?
  // const protocolModulesInfo = getProtocolModulesInfo(
  //   mostRecentAnalysis,
  //   deckDef
  // )
  return (
    <>
      <BackButton onClick={() => setSetupScreen('prepare to run')} />
      <Flex flexDirection={DIRECTION_COLUMN} marginTop={SPACING.spacing6}>
        Protocol Setup Modules Screen
        {/* {toggleGroup}
        {selectedValue === t('list_view') ? (
          <SetupModulesList robotName={robotName} runId={runId} />
        ) : (
          <SetupModulesMap robotName={robotName} runId={runId} />
        )}
      </Flex>
      <Flex justifyContent={JUSTIFY_CENTER}>
        <PrimaryButton
          disabled={missingModuleIds.length > 0 || runHasStarted}
          onClick={expandLabwareSetupStep}
          id="ModuleSetup_proceedToLabwareSetup"
          padding={`${String(SPACING.spacing3)} ${String(SPACING.spacing4)}`}
          {...targetProps}
        >
          {t('proceed_to_labware_setup_prep')}
        </PrimaryButton> */}
      </Flex>
    </>
  )
}
