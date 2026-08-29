import type { PluginOs } from '@hermes/plugin-sdk'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { KanbanText } from './i18n'

const { apiMocks, hostMock } = vi.hoisted(() => ({
  apiMocks: {
    exportBoard: vi.fn(),
    importBoard: vi.fn()
  },
  hostMock: {
    notify: vi.fn(),
    state: { connectionMode: { get: vi.fn<() => null | 'local' | 'remote'>() } }
  }
}))

vi.mock('@hermes/plugin-sdk', () => ({ host: hostMock }))
vi.mock('./api', () => apiMocks)
vi.mock('./ui', () => ({ errText: (error: unknown) => String(error) }))

import { runExportBoardFlow, runImportBoardFlow } from './transfer'

const k = {
  boardExported: (path: string) => `exported ${path}`,
  boardImported: (name: string) => `imported ${name}`,
  boardImportedAs: (slug: string) => `renamed ${slug}`,
  exportBoardTitle: 'Export board',
  importBoardTitle: 'Import board',
  remoteTransferUnavailable: 'Board import and export are unavailable for remote connections.'
} as KanbanText

function osDoor(): PluginOs {
  return {
    notify: vi.fn(),
    openExternal: vi.fn(),
    pickOpenPath: vi.fn(async () => '/Users/me/board.tar.gz'),
    pickSavePath: vi.fn(async () => '/Users/me/out.tar.gz'),
    revealPath: vi.fn(),
    writeClipboard: vi.fn()
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  hostMock.state.connectionMode.get.mockReturnValue('local')
})

describe('kanban board transfer', () => {
  it('does not pass a client save path to a remote backend', async () => {
    const os = osDoor()
    hostMock.state.connectionMode.get.mockReturnValue('remote')

    await expect(runExportBoardFlow(os, k, 'shipping')).resolves.toBeNull()

    expect(os.pickSavePath).not.toHaveBeenCalled()
    expect(apiMocks.exportBoard).not.toHaveBeenCalled()
    expect(hostMock.notify).toHaveBeenCalledWith({
      kind: 'error',
      message: k.remoteTransferUnavailable
    })
  })

  it('does not pass a client archive path to a remote backend', async () => {
    const os = osDoor()
    hostMock.state.connectionMode.get.mockReturnValue('remote')

    await expect(runImportBoardFlow(os, k)).resolves.toBeNull()

    expect(os.pickOpenPath).not.toHaveBeenCalled()
    expect(apiMocks.importBoard).not.toHaveBeenCalled()
    expect(hostMock.notify).toHaveBeenCalledWith({
      kind: 'error',
      message: k.remoteTransferUnavailable
    })
  })

  it('fails closed while the gateway location is unresolved', async () => {
    const os = osDoor()
    hostMock.state.connectionMode.get.mockReturnValue(null)

    await expect(runExportBoardFlow(os, k, 'shipping')).resolves.toBeNull()

    expect(os.pickSavePath).not.toHaveBeenCalled()
    expect(apiMocks.exportBoard).not.toHaveBeenCalled()
  })

  it('keeps the local path-based export flow', async () => {
    const os = osDoor()
    apiMocks.exportBoard.mockResolvedValue({ archive: '/Users/me/out.tar.gz' })

    await expect(runExportBoardFlow(os, k, 'shipping')).resolves.toBe('/Users/me/out.tar.gz')

    expect(apiMocks.exportBoard).toHaveBeenCalledWith('shipping', '/Users/me/out.tar.gz')
  })
})
