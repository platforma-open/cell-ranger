<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3';
import {
  AgGridTheme,
  PlAgOverlayLoading,
  PlAgOverlayNoRows,
  PlAgTextAndButtonCell,
  PlBlockPage,
  PlBtnGhost,
  PlDropdown,
  PlDropdownRef,
  PlMaskIcon24,
  PlSlideModal
} from "@platforma-sdk/ui-vue";

import { ColDef, GridApi, GridOptions, GridReadyEvent, ModuleRegistry, ClientSideRowModelModule } from 'ag-grid-enterprise';
import { PlRef } from '@platforma-sdk/model';
import { computed, reactive, shallowRef } from "vue";
import { useApp } from "../app";
import ProgressCell from './components/ProgressCell.vue';
import ReportPanel from './Report.vue'
import { resultMap } from './results';

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


const speciesOptions = [
  { text: "Homo sapiens (GRCh38)", value: "homo-sapiens" },
  { text: "Mus musculus (GRCm39)", value: "mus-musculus" },
  { text: "Saccharomyces cerevisiae (R64-1-1)", value: "saccharomyces-cerevisiae" },
  { text: "Rattus norvegicus (mRatBN7.2)", value: "rattus-norvegicus" },
  { text: "Danio rerio (GRCz11)", value: "danio-rerio" },
  { text: "Drosophila Melanogaster (BDGP6.46)", value: "drosophila-melanogaster" },
  { text: "Arabidopsis Thaliana (TAIR10)", value: "arabidopsis-thaliana" },
  { text: "Caenorhabditis Elegans (WBcel235)", value: "caenorhabditis-elegans" },
  { text: "Gallus Gallus (GRCg7b)", value: "gallus-gallus" },
  { text: "Bos Taurus (ARS-UCD1.3)", value: "bos-taurus" },
  { text: "Sus Scrofa (Sscrofa11.1)", value: "sus-scrofa" },
  { text: "Test genome (v1)", value: "test-species" },
];


/** Rows for ag-table */
const results = computed<any[] | undefined>(() => {

  if (resultMap.value === undefined) return undefined;
  const rows = []
  for (const id in resultMap.value) {
    rows.push({
      "sampleId": id,
      "sampleLabel": resultMap.value[id].sampleLabel,
      "cellRanger": resultMap.value[id].cellRangerProgressLine
    });
  }

  return rows;
});

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const gridApi = shallowRef<GridApi<any>>();
const onGridReady = (params: GridReadyEvent) => {
  gridApi.value = params.api;
};

const defaultColDef: ColDef = {
  suppressHeaderMenuButton: true,
  lockPinned: true,
  sortable: false
};

const columnDefs: ColDef[] = [
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
  {
    colId: 'cellRanger',
    field: 'cellRanger',
    cellRenderer: ProgressCell,
    headerName: 'Cell Ranger Progress',
    cellStyle: {
      '--ag-cell-horizontal-padding': '0px',
      '--ag-cell-vertical-padding': '0px'
    },
  }
];

const gridOptions: GridOptions = {
  getRowId: (row) => row.data.sampleId,
  onRowDoubleClicked: (e) => {
    data.selectedSample = e.data?.sampleId
    data.sampleReportOpen = data.selectedSample !== undefined;
  },
  components: {
    // AlignmentStatsCell,
    // FeatureCountsStatsCell,
    PlAgTextAndButtonCell,
    ProgressCell
  }
};

/* @deprecated Migrate to SDK method when will be published */
function plRefsEqual(ref1: PlRef, ref2: PlRef) {
  return ref1.blockId === ref2.blockId && ref1.name === ref2.name;
}

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

    <AgGridVue :theme="AgGridTheme" :style="{ height: '100%' }"
      @grid-ready="onGridReady"
      :rowData="results"
      :columnDefs="columnDefs"
      :grid-options="gridOptions" :loadingOverlayComponentParams="{ notReady: true }"
      :defaultColDef="defaultColDef" :loadingOverlayComponent=PlAgOverlayLoading
      :noRowsOverlayComponent=PlAgOverlayNoRows />
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
