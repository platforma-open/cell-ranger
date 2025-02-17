import { AnyLogHandle } from "@platforma-sdk/model";
import { computed } from "vue";
import { useApp } from "../app";

export type ResultEntry = {
  sampleLabel: string;
  cellRangerProgress?: AnyLogHandle;
  cellRangerProgressLine?: string;
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
    
    return r;
  }
);
