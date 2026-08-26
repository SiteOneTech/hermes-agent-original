import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const repoRoot = fileURLToPath(new URL('..', import.meta.url))
const script = '.github/scripts/run-workspace-checks.mjs'

function runWorkspaceChecks(args: string[]) {
  return spawnSync(process.execPath, [script, ...args], {
    cwd: repoRoot,
    encoding: 'utf8',
    timeout: 1_000,
  })
}

describe('run-workspace-checks concurrency validation', () => {
  it.each([
    ['missing value', ['--concurrency']],
    ['zero', ['--concurrency', '0']],
    ['fraction', ['--concurrency', '1.5']],
    ['non-numeric value', ['--concurrency', 'not-a-number']],
  ])('fails closed for %s', (_label, args) => {
    const result = runWorkspaceChecks(args)

    expect(result.status).not.toBe(0)
    expect(result.stderr).toContain('--concurrency must be a positive integer')
  })
})
