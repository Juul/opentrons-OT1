import { LabwarePositionCheckCommand } from '../types'
import { useSteps } from './useSteps'

export function useCommands(): LabwarePositionCheckCommand[] {
  return useSteps().reduce<LabwarePositionCheckCommand[]>(
    (steps, currentStep) => {
      return [...steps, ...currentStep.commands]
    },
    []
  )
}
