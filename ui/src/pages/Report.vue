<script setup lang="ts">
import { PlBtnGroup, PlChartStackedBar, PlLogView, ReactiveFileContent } from '@platforma-sdk/ui-vue';
import { computed, reactive } from 'vue';
import { useApp } from '../app';
import { getMappingChartSettings } from './charts/alignmentChartSettings';
import { resultMap } from './results';

const app = useApp();
const sampleId = defineModel<string | undefined>();

type TabId = 'visual' | 'log' | 'html';
const data = reactive<{ currentTab: TabId }>({ currentTab: 'visual' });

const tabOptions = [
  { value: 'visual', text: 'Visual Report' },
  { value: 'log', text: 'Log' },
  { value: 'html', text: 'Cell Ranger Web Summary' },
];

const report = computed(() => {
  const id = sampleId.value;
  if (id === undefined) {
    console.warn('SampleId is undefined');
    return undefined;
  }
  return app.model.outputs.webSummary?.data.find((it) => {
    return it.key.includes(id);
  })?.value;
});

const reportHtml = computed(() => {
  const handle = report.value?.handle;
  if (handle === undefined) {
    return;
  }
  return ReactiveFileContent.getContentString(handle).value;// ?.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '');
});

// const testHtml = `<!doctype html><p>Hello World!</p>`;

const sampleSummary = computed(() => {
  const id = sampleId.value;
  if (id === undefined) return undefined;
  const map = resultMap.value;
  if (map === undefined) return undefined;
  return map[id]?.summary;
});

const alignmentValue = computed(() => getMappingChartSettings(sampleSummary.value));

const logHandle = computed(() => {
  const id = sampleId.value;
  if (id === undefined) return undefined;
  const logs = app.model.outputs.cellRangerProgress;
  const entry = logs?.data.find((it) => it.key.includes(id));
  return entry?.value;
});
</script>

<template>
  <PlBtnGroup v-model="data.currentTab" :options="tabOptions" />

  <div v-if="data.currentTab === 'visual'" style="padding: 12px 0; display: flex;">
    <PlChartStackedBar v-if="alignmentValue" :settings="alignmentValue" />
  </div>

  <div v-else-if="data.currentTab === 'log'">
    <PlLogView :log-handle="logHandle" label="CellRanger Log"/>
  </div>

  <div v-else>
    <iframe v-if="reportHtml" :srcdoc="reportHtml" style="width: 100%; height: 80vh; border: 0;" />
    <div v-else>No HTML report available</div>
  </div>
</template>
