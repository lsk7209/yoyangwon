import { readFile } from 'node:fs/promises';

const workflowPath = '.github/workflows/release-due-posts.yml';
const source = await readFile(workflowPath, 'utf8');

const checks = {
  manualOnly: /\n\s*workflow_dispatch:\s*\n/.test(source)
    && !/\n\s*schedule:\s*\n/.test(source)
    && !/\bcron:\s*["']/.test(source),
  explicitConfirmationInput: /confirmation:\s*\n[\s\S]*?required:\s*true/.test(source),
  exactJobGate: /if:\s*github\.event\.inputs\.confirmation\s*==\s*'REFRESH_HELD_PREVIEW'/.test(source),
  serialized: /concurrency:\s*\n[\s\S]*?group:\s*caregos-held-preview/.test(source),
  boundedRuntime: /timeout-minutes:\s*15/.test(source),
  holdStillApplied: /^\s*python scripts\/apply_adsense_review_hold\.py\s*$/m.test(source),
  failClosedHoldVerifier: /^\s*python scripts\/apply_adsense_review_hold\.py --verify-only\s*$/m.test(source),
  noInvertedGreps: !/^\s*!\s+grep\b/m.test(source),
  noGscDependencyInstall: !/google-api-python-client|google-auth/.test(source),
  noGscSubmission: !/gsc_submit_sitemap\.py|Submit sitemap to Google Search Console/.test(source),
  noAlwaysOnMutation: !/if:\s*always\(\)/.test(source),
  writeScopeRetained: /permissions:\s*\n\s*contents:\s*write/.test(source),
};

const failures = Object.entries(checks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);

console.log(JSON.stringify({ workflowPath, checks, failures }, null, 2));
if (failures.length > 0) {
  process.exitCode = 1;
}
