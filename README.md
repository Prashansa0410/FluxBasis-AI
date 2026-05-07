
# Flakeguard AI

// ...existing content...

## Playwright JSON Report Support

Flakeguard AI now supports parsing Playwright JSON reports. To use this feature:

1. Ensure your Playwright tests generate a JSON report:
   ```bash
   npx playwright test --reporter=json
   ```

2. Use the `parsePlaywrightReport` function to parse the report:
   ```typescript
   import { parsePlaywrightReport } from './playwrightReportParser';

   const results = parsePlaywrightReport('path/to/report.json');
   console.log(results);
   ```

This will extract test names, statuses, durations, and errors (if any) from the report.
