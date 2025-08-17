<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3';
import {
  PlAgTextAndButtonCell,
  PlBlockPage,
  PlBtnGhost,
  PlMaskIcon24,
  PlSlideModal,
  createAgGridColDef,
  makeRowNumberColDef,
  AgGridTheme,
  PlAgOverlayLoading,
  PlAgOverlayNoRows,
} from '@platforma-sdk/ui-vue';

import type { ProgressLogWithInfo } from '@platforma-sdk/model';
import { computed, reactive, shallowRef, watch } from 'vue';
import { useApp } from '../app';
import ReportPanel from './Report.vue';
import { resultMap } from './results';
import { parseProgress } from '../parseProgress';
import SettingsPanel from './SettingsPanel.vue';
import type { ColDef, GridApi, GridOptions, GridReadyEvent } from 'ag-grid-enterprise';
import { autoSizeRowNumberColumn } from '@platforma-sdk/ui-vue';
import { whenever } from '@vueuse/core';

const app = useApp();

const data = reactive<{
  settingsOpen: boolean;
  sampleReportOpen: boolean;
  selectedSample: string | undefined;
}>({
  settingsOpen: app.model.args.ref === undefined,
  sampleReportOpen: false,
  selectedSample: undefined,
});

watch(
  () => app.model.outputs.isRunning,
  (newVal, oldVal) => {
    if (oldVal === false && newVal === true)
      data.settingsOpen = false;
    if (oldVal === true && newVal === false)
      data.settingsOpen = true;
  },
);

whenever(
  () => data.settingsOpen,
  () => (data.sampleReportOpen = false),
);
whenever(
  () => data.sampleReportOpen,
  () => (data.settingsOpen = false),
);

type Row = {
  sampleId: string;
  sampleLabel: string;
  cellRanger: ProgressLogWithInfo | undefined;
};

/** Rows for ag-table */
const results = computed<Row[] | undefined>(() => {
  if (resultMap.value === undefined)
    return undefined;
  const rows = [];
  for (const id in resultMap.value) {
    rows.push({
      sampleId: id,
      sampleLabel: resultMap.value[id].sampleLabel,
      cellRanger: resultMap.value[id].cellRangerProgressLine,
    });
  }

  return rows;
});

const gridApi = shallowRef<GridApi>();
const onGridReady = (params: GridReadyEvent) => {
  gridApi.value = params.api;
  autoSizeRowNumberColumn(params.api);
};

const defaultColumnDef: ColDef = {
  suppressHeaderMenuButton: true,
  lockPinned: true,
  sortable: false,
};

const columnDefs: ColDef<Row>[] = [
  makeRowNumberColDef(),
  createAgGridColDef<Row, string>({
    colId: 'label',
    field: 'sampleLabel',
    headerName: 'Sample',
    pinned: 'left',
    lockPinned: true,
    sortable: true,
    cellRenderer: PlAgTextAndButtonCell,
    cellRendererParams: {
      invokeRowsOnDoubleClick: true,
    },
  }),
  createAgGridColDef<Row, ProgressLogWithInfo | undefined>({
    colId: 'cellRanger',
    field: 'cellRanger',
    headerName: 'Cell Ranger Progress',
    flex: 1,
    cellStyle: {
      '--ag-cell-horizontal-padding': '0px',
      '--ag-cell-vertical-padding': '0px',
    },
    progress(cellRangerProgressLine) {
      return parseProgress(cellRangerProgressLine);
    },
  }),
] as any;

const gridOptions: GridOptions<Row> = {
  getRowId: row => row.data.sampleId,
  onRowDoubleClicked: (e) => {
    data.selectedSample = e.data?.sampleId;
    data.sampleReportOpen = data.selectedSample !== undefined;
  },
  components: {
    PlAgTextAndButtonCell,
  },
};
</script>

<template>
  <PlBlockPage>
    <template #title>
      Cell Ranger
    </template>
    <template #append>
      <PlBtnGhost @click.stop="() => (data.settingsOpen = true)">
        Settings
        <template #append>
          <PlMaskIcon24 name="settings" />
        </template>
      </PlBtnGhost>
    </template>

    <AgGridVue
      :theme="AgGridTheme"
      :style="{ height: '100%' }"
      :rowData="results"
      :defaultColDef="defaultColumnDef"
      :columnDefs="columnDefs"
      :grid-options="gridOptions as any"
      :loadingOverlayComponentParams="{ notReady: true }"
      :loadingOverlayComponent="PlAgOverlayLoading"
      :noRowsOverlayComponent="PlAgOverlayNoRows"
      @grid-ready="onGridReady"
    />
  </PlBlockPage>

  <PlSlideModal
    v-model="data.settingsOpen"
    :shadow="true"
    :close-on-outside-click="!app.model.outputs.isRunning"
  >
    <template #title>
      Settings
    </template>
    <SettingsPanel />
  </PlSlideModal>

  <PlSlideModal
    v-model="data.sampleReportOpen"
    :close-on-outside-click="!app.model.outputs.isRunning"
    width="95%"
  >
    <template #title>
      Results for
      {{
        (data.selectedSample ? app.model.outputs.labels?.[data.selectedSample] : undefined) ?? '...'
      }}
    </template>
    <ReportPanel v-model="data.selectedSample" />
  </PlSlideModal>
</template>
