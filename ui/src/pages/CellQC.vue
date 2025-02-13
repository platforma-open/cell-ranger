<script setup lang="ts">
import { GraphMaker, GraphMakerProps } from "@milaboratories/graph-maker";
import '@milaboratories/graph-maker/styles';
import { computed } from "vue";
import { useApp } from "../app";

const app = useApp();

</script>

<template>
  <GraphMaker chartType="discrete" :p-frame="app.model.outputs.cellMetricsPf" v-model="app.model.ui.graphState" />
</template>