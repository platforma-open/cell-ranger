import type { AnyLogHandle, ProgressLogWithInfo } from '@platforma-sdk/model';
import { computed } from 'vue';
import { useApp } from '../app';

export type ResultEntry = {
  sampleLabel: string;
  cellRangerProgress?: AnyLogHandle;
  cellRangerProgressLine?: ProgressLogWithInfo;
  summary?: Record<string, string>;
};

// return a map of sampleId => ResultEntry
export const resultMap = computed(
  (): Record<string, ResultEntry> | undefined => {
    const app = useApp();

    const labels = app.model.outputs.labels;
    if (labels === undefined) return undefined;

    const starProgress = app.model.outputs.cellRangerProgress;
    if (starProgress === undefined) return undefined;

    const r: Record<string, ResultEntry> = {};
    for (const prog of starProgress.data) {
      const sampleId = prog.key[0];
      r[sampleId] = {
        sampleLabel: labels[sampleId],
        cellRangerProgress: prog.value,
      };
    }

    const cellRangerProgressLine = app.model.outputs.cellRangerProgressLine;
    if (cellRangerProgressLine !== undefined) {
      for (const prog of cellRangerProgressLine.data) {
        r[prog.key[0]].cellRangerProgressLine = prog.value;
      }
    }

    // Parse and attach summary CSV content if available
    const summaryContent = app.model.outputs.summaryContent;
    if (summaryContent !== undefined) {
      const parseCsvLine = (line: string): string[] => {
        const values: string[] = [];
        let current = '';
        let inQuotes = false;
        for (let i = 0; i < line.length; i++) {
          const ch = line[i];
          if (ch === '"') {
            inQuotes = !inQuotes;
            continue;
          }
          if (ch === ',' && !inQuotes) {
            values.push(current);
            current = '';
          } else {
            current += ch;
          }
        }
        values.push(current);
        return values.map((v) => v.trim());
      };

      // Determine headers once (from the first entry with a valid header line)
      let headers: string[] | undefined = undefined;
      for (const entry of summaryContent.data) {
        const text = (entry.value ?? '').trim();
        const nl = text.indexOf('\n');
        if (nl !== -1) {
          headers = parseCsvLine(text.slice(0, nl));
          break;
        }
      }

      for (const prog of summaryContent.data) {
        const sampleId = prog.key[0];
        if (r[sampleId] === undefined) {
          r[sampleId] = {
            sampleLabel: labels[sampleId],
          } as ResultEntry;
        }
        const trimmed = (prog.value ?? '').trim();
        const newlineIndex = trimmed.indexOf('\n');
        if (newlineIndex === -1) {
          r[sampleId].summary = {};
          continue;
        }
        if (headers === undefined) {
          headers = parseCsvLine(trimmed.slice(0, newlineIndex));
        }
        const valueLine = trimmed.slice(newlineIndex + 1).split('\n')[0] ?? '';
        const values = parseCsvLine(valueLine).map((v) => {
          if (v.startsWith('"') && v.endsWith('"') && v.length >= 2) {
            return v.slice(1, -1);
          }
          return v;
        });
        const map: Record<string, string> = {};
        if (headers !== undefined) {
          for (let i = 0; i < headers.length; i++) {
            map[headers[i]] = values[i] ?? '';
          }
        }
        r[sampleId].summary = map;
      }
    }

    return r;
  },
);
