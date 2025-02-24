<script
  setup
  lang="ts"
>
import { AgGridVue } from 'ag-grid-vue3';
import {
  PlAgTextAndButtonCell,
  PlBlockPage,
  PlBtnGhost,
  PlDropdown,
  PlDropdownRef,
  PlMaskIcon24,
  PlSlideModal,
  useAgGridOptions
} from "@platforma-sdk/ui-vue";

import { plRefsEqual } from '@platforma-sdk/model';
import type { PlRef, ProgressLogWithInfo } from '@platforma-sdk/model';
import { computed, reactive } from "vue";
import { useApp } from "../app";
import ReportPanel from './Report.vue'
import { resultMap } from './results';
import { parseProgress } from '../parseProgress';
import { speciesOptions } from '../species';

const app = useApp();

const data = reactive<{
  settingsOpen: boolean,
  sampleReportOpen: boolean,
  selectedSample: string | undefined
}>({
  settingsOpen: app.model.args.ref === undefined,
  sampleReportOpen: false,
  selectedSample: undefined,
})

type Row = {
  sampleId: string;
  sampleLabel: string;
  cellRanger: ProgressLogWithInfo | undefined;
};

/** Rows for ag-table */
const results = computed<Row[] | undefined>(() => {
  if (resultMap.value === undefined) return undefined;
  const rows = []
  for (const id in resultMap.value) {
    rows.push({
      sampleId: id,
      sampleLabel: resultMap.value[id].sampleLabel,
      cellRanger: resultMap.value[id].cellRangerProgressLine
    });
  }

  return rows;
});

const { gridOptions } = useAgGridOptions<Row>(({ column }) => {
  return {
    rowData: results.value,
    rowNumbersColumn: true,
    defaultColDef: {
      suppressHeaderMenuButton: true,
      lockPinned: true,
      sortable: false
    },
    columnDefs: [
      {
        colId: 'label',
        field: 'sampleLabel',
        headerName: 'Sample',
        pinned: 'left',
        lockPinned: true,
        sortable: true,
        cellRenderer: PlAgTextAndButtonCell,
        cellRendererParams: {
          invokeRowsOnDoubleClick: true
        }
      },
      column<ProgressLogWithInfo | undefined>({
        colId: 'cellRanger',
        field: 'cellRanger',
        headerName: 'Cell Ranger Progress',
        flex: 1,
        cellStyle: {
          '--ag-cell-horizontal-padding': '0px',
          '--ag-cell-vertical-padding': '0px'
        },
        progress(cellRangerProgressLine) {
          return parseProgress(cellRangerProgressLine);
        },
      })
    ]
  };
});

function setInput(inputRef?: PlRef) {
  app.model.args.ref = inputRef;
  if (inputRef)
    app.model.args.title = app.model.outputs.dataOptions?.find(o => plRefsEqual(o.ref, inputRef))?.label
  else
    app.model.args.title = undefined;
}
</script>

<template>
  <PlBlockPage>
    <template #title>Cell Ranger</template>
    <template #append>
      <PlBtnGhost @click.stop="() => data.settingsOpen = true">
        Settings
        <template #append>
          <PlMaskIcon24 name="settings" />
        </template>
      </PlBtnGhost>
    </template>

    <AgGridVue :style="{ height: '100%' }" v-bind="gridOptions as {}" />
  </PlBlockPage>

  <PlSlideModal v-model="data.settingsOpen">
    <template #title>Settings</template>
    <PlDropdownRef :options="app.model.outputs.dataOptions" v-model="app.model.args.ref" @update:model-value="setInput"
      label="Select dataset" clearable />
    <PlDropdown :options="speciesOptions" v-model="app.model.args.species" label="Select species" />
  </PlSlideModal>

  <PlSlideModal v-model="data.sampleReportOpen" width="95%">
    <template #title>Results for {{ (data.selectedSample ? app.model.outputs.labels?.[data.selectedSample] :
      undefined) ?? "..." }}</template>
    <ReportPanel v-model="data.selectedSample" />
  </PlSlideModal>
</template>
