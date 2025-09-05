<script setup lang="ts">
import {
  AgGridTheme,
  PlAgChartStackedBarCell,
  PlAgOverlayLoading,
  PlAgOverlayNoRows,
  PlAgTextAndButtonCell,
  PlBlockPage,
  PlBtnGhost,
  PlMaskIcon24,
  PlSlideModal,
  createAgGridColDef,
  makeRowNumberColDef,
} from '@platforma-sdk/ui-vue';
import { AgGridVue } from 'ag-grid-vue3';

import type { ProgressLogWithInfo } from '@platforma-sdk/model';
import { autoSizeRowNumberColumn } from '@platforma-sdk/ui-vue';
import { whenever } from '@vueuse/core';
import type { ColDef, GridApi, GridOptions, GridReadyEvent, ValueGetterParams } from 'ag-grid-enterprise';
import { computed, reactive, shallowRef, watch } from 'vue';
import { useApp } from '../app';
import { parseProgress } from '../parseProgress';
import { getMappingChartSettings } from './charts/alignmentChartSettings';
import ReportPanel from './Report.vue';
import { resultMap } from './results';
import SettingsPanel from './SettingsPanel.vue';

const app = useApp();

const data = reactive<{
  settingsOpen: boolean;
  mnzOpen: boolean;
  sampleReportOpen: boolean;
  selectedSample: string | undefined;
}>({
  settingsOpen: app.model.args.ref === undefined,
  mnzOpen: false,
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
  summary?: Record<string, string>;
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
      summary: resultMap.value[id].summary,
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

const columnDefs = computed<ColDef<Row>[]>(() => {
  const cols: ColDef<Row>[] = [
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
      minWidth: 200,
      cellStyle: {
        '--ag-cell-horizontal-padding': '0px',
        '--ag-cell-vertical-padding': '0px',
      },
      progress(cellRangerProgressLine) {
        return parseProgress(cellRangerProgressLine);
      },
    }),
    createAgGridColDef<Row, string>({
      colId: 'alignmentStats',
      headerName: 'Alignments',
      flex: 1,
      minWidth: 200,
      cellStyle: {
        '--ag-cell-horizontal-padding': '12px',
      },
      cellRendererSelector: (cellData) => {
        const value = getMappingChartSettings(cellData.data?.summary);
        return {
          component: PlAgChartStackedBarCell,
          params: { value },
        };
      },
    }),
  ];

  // Add only specified summary CSV columns in the required order
  const desiredSummaryHeaders: string[] = [
    'Estimated Number of Cells',
    'Mean Reads per Cell',
    'Median Genes per Cell',
    'Sequencing Saturation',
    'Valid Barcodes',
    'Fraction Reads in Cells',
    'Q30 Bases in Barcode',
    'Q30 Bases in RNA Read',
    'Q30 Bases in UMI',
  ];

  for (const header of desiredSummaryHeaders) {
    cols.push(
      createAgGridColDef<Row, string>({
        colId: `summary:${header}`,
        headerName: header,
        minWidth: 100,
        maxWidth: 200,
        valueGetter: (p: ValueGetterParams<Row, string>) => p.data?.summary?.[header] ?? '',
      }),
    );
  }

  return cols;
});

const gridOptions: GridOptions<Row> = {
  getRowId: (row) => row.data.sampleId,
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
    <div :style="{ flex: 1 }">
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
    </div>
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

  <PlSlideModal v-model="data.mnzOpen">
    <template #title>
      Subscription Status
    </template>
  </PlSlideModal>
</template>
