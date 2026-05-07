
import * as fs from 'fs';

export interface PlaywrightTestResult {
    name: string;
    status: string;
    duration: number;
    error?: string;
}

export function parsePlaywrightReport(filePath: string): PlaywrightTestResult[] {
    const reportData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    const results: PlaywrightTestResult[] = [];

    for (const project of reportData.suites) {
        for (const suite of project.suites) {
            for (const test of suite.tests) {
                results.push({
                    name: test.title.join(' > '),
                    status: test.outcome,
                    duration: test.results[0]?.duration || 0,
                    error: test.results[0]?.error?.message,
                });
            }
        }
    }

    return results;
}
