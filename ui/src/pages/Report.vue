<script setup lang="ts">
import { PlBtnGroup, PlChartStackedBar, PlLogView, ReactiveFileContent } from '@platforma-sdk/ui-vue';
import { computed, reactive } from 'vue';
import { useApp } from '../app';
import { getMappingChartSettings } from './charts/alignmentChartSettings';
import { resultMap } from './results';

const app = useApp();
const sampleId = defineModel<string | undefined>();

const reactiveFileContent = ReactiveFileContent.useGlobal();

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
  return reactiveFileContent.getContentString(handle)?.value;// ?.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '');
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

  <template v-if="data.currentTab === 'visual'">
    <PlChartStackedBar v-if="alignmentValue" :settings="alignmentValue" />
  </template>

  <template v-if="data.currentTab === 'log'">
    <PlLogView :log-handle="logHandle" label="CellRanger Log" />
  </template>

  <template v-if="data.currentTab === 'html'">
    <iframe v-if="reportHtml" :srcdoc="reportHtml" :class="$style.iframe" />
    <div v-else>No HTML report available</div>
  </template>
</template>

<style module>
.iframe {
  flex: 1;
  border: none;
}
</style>
