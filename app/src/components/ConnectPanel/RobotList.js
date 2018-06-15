// @flow
// list of robots
import * as React from 'react'

import {
  ListItem,
  NotificationIcon
} from '@opentrons/components'

import type {Robot} from '../../robot'
import {ToggleButton} from '../controls'
import styles from './connect-panel.css'

type ListProps = {
  children: React.Node
}

type ItemProps = Robot & {
  availableUpdate: ?string,
  connect: () => mixed,
  disconnect: () => mixed
}

export default function RobotList (props: ListProps) {
  return (
    <ol className={styles.robot_list}>
      {props.children}
    </ol>
  )
}

export function RobotListItem (props: ItemProps) {
  const {name, wired, isConnected, availableUpdate, connect, disconnect} = props
  const onClick = isConnected
    ? disconnect
    : connect

  return (
    <ListItem
      url={`/robots/${name}`}
      className={styles.robot_item}
      activeClassName={styles.active}
    >
      <NotificationIcon
        name={wired ? 'usb' : 'wifi'}
        className={styles.robot_item_icon}
        childName={availableUpdate ? 'circle' : null}
        childClassName={styles.notification}
      />

      <p className={styles.robot_name}>
        {name}
      </p>

      <ToggleButton
        toggledOn={isConnected}
        onClick={onClick}
        className={styles.robot_item_icon}
      />
    </ListItem>
  )
}
