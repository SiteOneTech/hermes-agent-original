import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { HermesConnection } from '@/global'
import { $cronReviewRequest } from '@/store/cron'
import { $notifications, clearNotifications } from '@/store/notifications'
import { $activeGatewayProfile } from '@/store/profile'
import { setConnection } from '@/store/session'
import type { ModelAssignmentResponse } from '@/types/hermes'

import { deferred } from '../test/deferred'

const hermesMock = vi.hoisted(() => {
  let apiProfile: null | string = 'default'

  return {
    getApiRequestProfile: vi.fn(() => apiProfile),
    resetApiProfile: (profile: null | string = 'default') => {
      apiProfile = profile
    },
    setApiRequestProfile: vi.fn((profile: null | string) => {
      apiProfile = profile || null
    }),
    setModelAssignment: vi.fn()
  }
})

vi.mock('@/hermes', async importOriginal => {
  const actual = await importOriginal<Record<string, unknown>>()

  return {
    ...actual,
    getApiRequestProfile: () => hermesMock.getApiRequestProfile(),
    setApiRequestProfile: (profile: null | string) => hermesMock.setApiRequestProfile(profile),
    setModelAssignment: (...args: unknown[]) => hermesMock.setModelAssignment(...args)
  }
})

vi.mock('@/i18n', () => ({
  translateNow: (key: string, ...args: unknown[]) => {
    if (key === 'cron.modelImpact.title') {
      return 'Scheduled jobs stay on their original model'
    }

    if (key === 'cron.modelImpact.message') {
      return `${args[0]} unpinned scheduled job keeps running on the model it was created under`
    }

    if (key === 'cron.modelImpact.review') {
      return 'Review scheduled jobs'
    }

    return key
  }
}))

import { setMainModelAssignment } from './model-assignment'

const CRON_MODEL_IMPACT_NOTIFICATION_ID = 'cron-model-impact'

function connection(
  baseUrl: string,
  wsUrl: string,
  overrides: Partial<HermesConnection> = {}
): HermesConnection {
  return {
    baseUrl,
    isFullscreen: false,
    logs: [],
    mode: 'remote',
    nativeOverlayWidth: 0,
    token: 'secret-not-part-of-identity',
    windowButtonPosition: null,
    wsUrl,
    ...overrides
  }
}

function response(impact: ModelAssignmentResponse['cron_model_impact']): ModelAssignmentResponse {
  return {
    ok: true,
    scope: 'main',
    provider: 'nous',
    model: 'new/model',
    cron_model_impact: impact
  }
}

function positive(name = 'Morning summary'): ModelAssignmentResponse['cron_model_impact'] {
  return {
    available: true,
    affected_count: 1,
    truncated: false,
    jobs: [{ id: 'job-1', name, drifted_axes: ['provider', 'model'] }]
  }
}

function currentImpactNotification() {
  return $notifications.get().find(item => item.id === CRON_MODEL_IMPACT_NOTIFICATION_ID)
}

beforeEach(() => {
  hermesMock.setModelAssignment.mockReset()
  hermesMock.getApiRequestProfile.mockClear()
  hermesMock.setApiRequestProfile.mockClear()
  hermesMock.resetApiProfile('default')
  setConnection(connection('https://one.example', 'wss://one.example?ticket=first'))
  $activeGatewayProfile.set('default')
  clearNotifications()
})

describe('setMainModelAssignment cron impact', () => {
  it('publishes an unscoped cron review notification with a read-only review action', async () => {
    hermesMock.setModelAssignment.mockResolvedValue(response(positive()))
    const requestCount = $cronReviewRequest.get()

    await setMainModelAssignment({ provider: 'nous', model: 'new/model' })

    expect(hermesMock.setModelAssignment).toHaveBeenCalledWith({
      scope: 'main',
      provider: 'nous',
      model: 'new/model'
    })
    const notification = currentImpactNotification()
    expect(notification?.kind).toBe('info')
    expect(notification?.title).toBe('Scheduled jobs stay on their original model')
    expect(notification?.message).toContain('1 unpinned scheduled job keeps running on the model it was created under')
    expect(notification?.detail).toContain('Morning summary')
    expect(notification?.action?.label).toBe('Review scheduled jobs')

    notification?.action?.onClick()
    expect($cronReviewRequest.get()).toBe(requestCount + 1)
    expect(hermesMock.setModelAssignment).toHaveBeenCalledTimes(1)
  })

  it('does not replace an existing valid warning with malformed impact data', async () => {
    hermesMock.setModelAssignment.mockResolvedValueOnce(response(positive('Original job')))
    await setMainModelAssignment({ provider: 'nous', model: 'one' })
    expect(currentImpactNotification()?.detail).toContain('Original job')

    hermesMock.setModelAssignment.mockResolvedValueOnce(
      response({
        available: true,
        affected_count: 2,
        truncated: false,
        jobs: [{ id: 'job-1', name: 'Malformed replacement', drifted_axes: ['provider'] }]
      })
    )
    await setMainModelAssignment({ provider: 'nous', model: 'two' })

    expect(currentImpactNotification()?.detail).toContain('Original job')
    expect(currentImpactNotification()?.detail).not.toContain('Malformed replacement')
  })

  it('publishes only the latest same-profile assignment when responses reverse', async () => {
    const first = deferred<ModelAssignmentResponse>()
    const second = deferred<ModelAssignmentResponse>()
    hermesMock.setModelAssignment.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise)

    const firstCall = setMainModelAssignment({ provider: 'nous', model: 'first' })
    const secondCall = setMainModelAssignment({ provider: 'nous', model: 'second' })
    second.resolve(response(positive('Second job')))
    await secondCall
    first.resolve(response(positive('Stale first job')))
    await firstCall

    const notification = currentImpactNotification()
    expect(notification?.detail).toContain('Second job')
    expect(notification?.detail).not.toContain('Stale first job')
  })

  it('dismisses stale notifications and pending responses when profile or connection changes', async () => {
    const pending = deferred<ModelAssignmentResponse>()
    hermesMock.setModelAssignment.mockReturnValueOnce(pending.promise)
    const call = setMainModelAssignment({ provider: 'nous', model: 'pending' })

    $activeGatewayProfile.set('other')
    pending.resolve(response(positive('Stale job')))
    await call
    expect(currentImpactNotification()).toBeUndefined()

    hermesMock.setModelAssignment.mockResolvedValueOnce(response(positive('Current job')))
    $activeGatewayProfile.set('default')
    await setMainModelAssignment({ provider: 'nous', model: 'current' })
    const action = currentImpactNotification()?.action
    const requestCount = $cronReviewRequest.get()

    setConnection(connection('https://two.example', 'wss://two.example?ticket=second'))
    expect(currentImpactNotification()).toBeUndefined()

    action?.onClick()
    expect($cronReviewRequest.get()).toBe(requestCount)
  })

  it('does not publish cron review notifications for scoped assignments', async () => {
    hermesMock.setModelAssignment.mockResolvedValue(response(positive('Other profile job')))

    await setMainModelAssignment({ provider: 'nous', model: 'new/model' }, 'other')

    expect(hermesMock.setModelAssignment).toHaveBeenCalledWith(
      {
        scope: 'main',
        provider: 'nous',
        model: 'new/model'
      },
      'other'
    )
    expect(currentImpactNotification()).toBeUndefined()
  })
})
