<script setup lang="ts">
import type { GraphMakerProps } from '@milaboratories/graph-maker';
import { GraphMaker } from '@milaboratories/graph-maker';
import '@milaboratories/graph-maker/styles';
import { ref } from 'vue';
import { useApp } from '../app';
import type { PColumnIdAndSpec } from '@platforma-sdk/model';

const app = useApp();

function getDefaultOptions(cellMetricsPfDefaults?: PColumnIdAndSpec[]) {
  if (!cellMetricsPfDefaults) {
    return undefined;
  }

  function getIndex(name: string, pcols: PColumnIdAndSpec[]): number {
    return pcols.findIndex((p) => p.spec.name === name);
  }

  const defaults: GraphMakerProps['defaultOptions'] = [
    {
      inputName: 'y',
      selectedSource: cellMetricsPfDefaults[getIndex('pl7.app/rna-seq/totalCounts',
        cellMetricsPfDefaults)].spec,
    },
    {
      inputName: 'primaryGrouping',
      selectedSource: cellMetricsPfDefaults[getIndex('pl7.app/label',
        cellMetricsPfDefaults)].spec,
    },
  ];

  return defaults;
}

const defaultOptions = ref(getDefaultOptions(app.model.outputs.cellMetricsPfDefaults));

</script>

<template>
  <GraphMaker
    v-model="app.model.ui.graphState" chartType="discrete"
    :p-frame="app.model.outputs.cellMetricsPf" :defaultOptions="defaultOptions"
  />
</template>
