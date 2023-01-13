import * as React from 'react'
import { useTranslation } from 'react-i18next'
import { useHistory } from 'react-router-dom'
import { css } from 'styled-components'

import {
  Flex,
  SPACING,
  DIRECTION_ROW,
  ALIGN_CENTER,
  JUSTIFY_SPACE_BETWEEN,
  Icon,
  Btn,
  JUSTIFY_START,
  JUSTIFY_CENTER,
  JUSTIFY_END,
  COLORS,
} from '@opentrons/components'

import { StyledText } from '../../atoms/text'
import { SearchNetwork } from './SearchNetwork'

import type { WifiNetwork } from '../../redux/networking/types'

const NETWORK_ROW_STYLE = css`
  &:active {
    background-color: ${COLORS.blueEnabled};
    color: ${COLORS.white};
  }
  &:hover {
    background-color: ${COLORS.blueEnabled};
    color: ${COLORS.white};
  }
`

interface DisplayWifiListProps {
  list: WifiNetwork[]
  isSearching: boolean
  setSelectedSsid: (nwSsid: string) => void
  setIsShowSelectAuthenticationType: (
    isShowSelectAuthenticationType: boolean
  ) => void
}

export function DisplayWifiList({
  list,
  isSearching,
  setSelectedSsid,
  setIsShowSelectAuthenticationType,
}: DisplayWifiListProps): JSX.Element {
  return (
    <>
      <HeaderWithIPs isSearching={isSearching} />
      {list.length >= 1 ? (
        list.map(nw => (
          <Btn
            width="59rem"
            height="4rem"
            key={nw.ssid}
            backgroundColor="#d6d6d6"
            marginBottom={SPACING.spacing3}
            borderRadius="12px"
            css={NETWORK_ROW_STYLE}
            onClick={() => {
              setSelectedSsid(nw.ssid)
              setIsShowSelectAuthenticationType(true)
            }}
          >
            <Flex
              flexDirection={DIRECTION_ROW}
              padding={SPACING.spacing4}
              alignItems={ALIGN_CENTER}
            >
              <Icon name="wifi" size="2.25rem" color={COLORS.darkGreyEnabled} />
              <StyledText
                marginLeft={SPACING.spacing4}
                fontSize="1.5rem"
                lineHeight="2.0625rem"
                fontWeight="400"
              >
                {nw.ssid}
              </StyledText>
            </Flex>
          </Btn>
        ))
      ) : (
        <SearchNetwork />
      )}
    </>
  )
}

interface HeadWithIPsProps {
  isSearching: boolean
}

const HeaderWithIPs = ({ isSearching }: HeadWithIPsProps): JSX.Element => {
  const { t } = useTranslation(['device_settings', 'shared'])
  const history = useHistory()
  return (
    <Flex
      flexDirection={DIRECTION_ROW}
      justifyContent={JUSTIFY_SPACE_BETWEEN}
      alignItems={ALIGN_CENTER}
      marginBottom="3.0625rem"
    >
      <Flex justifyContent={JUSTIFY_START}>
        <Btn onClick={() => history.push('/network-setup')}>
          <Flex flexDirection={DIRECTION_ROW}>
            <Icon
              name="arrow-back"
              marginRight={SPACING.spacing2}
              size="1.875rem"
            />
            <StyledText
              fontSize="1.625rem"
              lineHeight="2.1875rem"
              fontWeight="700"
            >
              {t('shared:back')}
            </StyledText>
          </Flex>
        </Btn>
      </Flex>
      <Flex justifyContent={JUSTIFY_CENTER}>
        <StyledText fontSize="2rem" lineHeight="2.75rem" fontWeight="700">
          {t('connect_via', { type: t('wifi') })}
        </StyledText>
      </Flex>
      <Flex justifyContent={JUSTIFY_END}>
        {isSearching ? <Icon name="ot-spinner" spin size="3.3125rem" /> : null}
      </Flex>
    </Flex>
  )
}