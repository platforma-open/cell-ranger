<script setup lang="ts">
import { GraphMaker, GraphMakerProps } from "@milaboratories/graph-maker";
import '@milaboratories/graph-maker/styles';
import { computed, ref } from "vue";
import { useApp } from "../app";
import { PColumnIdAndSpec } from "@platforma-sdk/model";

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
  <GraphMaker chartType="discrete" :p-frame="app.model.outputs.cellMetricsPf"
    v-model="app.model.ui.graphState" :defaultOptions="defaultOptions" 
  />
</template>