<script setup lang="ts">
import { useApp } from '../app';
import { computed } from 'vue';
import { ReactiveFileContent } from '@platforma-sdk/ui-vue';
const app = useApp();
const sampleId = defineModel<string | undefined>();

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
</script>

<template>
  <div v-if="false" title="Frame" width="1100" height="800" v-html="reportHtml" />
  <iframe v-if="false" :srcdoc="reportHtml" />

  {{ reportHtml }}
</template>
