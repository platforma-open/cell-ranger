<script setup lang="ts">
import { ICellRendererParams } from 'ag-grid-enterprise';
import { computed, unref } from 'vue';
import { PlAgCellProgress, PlProgressCellProps } from '@platforma-sdk/ui-vue';

const props = defineProps<{
  params: ICellRendererParams;
}>();

const progressString = computed(() => {
  return props.params.value ?? 'Unknown';
});

type Parsed = {
  raw?: string;
  stage?: string;
  time?: string;
  percentage?: string;
  percentageLabel?: string;
};

const parsed = computed<Parsed>(() => {
  const raw = unref(progressString);

  const res: Parsed = {
    raw
  };

  if (!raw) {
    return res;
  }

  console.log(raw);
  if (raw.indexOf('SC_RNA_COUNTER_CS.') < 0) {
    return res;
  }

  const parts = raw.split('SC_RNA_COUNTER_CS.');

  res.time = parts[0].trim();
  res.stage = parts[1].trim();

  switch (res.stage) {
    case 'SC_MULTI_CORE.MULTI_GEM_WELL_PROCESSOR.COUNT_GEM_WELL_PROCESSOR._BASIC_SC_RNA_COUNTER._MATRIX_COMPUTER.WRITE_BARCODE_INDEX.fork0.split':
      res.percentage = '20';
      break;
    case 'SC_MULTI_CORE.MULTI_GEM_WELL_PROCESSOR.COUNT_GEM_WELL_PROCESSOR._BASIC_SC_RNA_COUNTER._MATRIX_COMPUTER.ALIGN_AND_COUNT.fork0.chnk0.main':
      res.percentage = '50';
      break;
    case 'SC_MULTI_CORE.MULTI_GEM_WELL_PROCESSOR.COUNT_GEM_WELL_PROCESSOR._BASIC_SC_RNA_COUNTER.WRITE_POS_BAM.fork0.join':
      res.percentage = '75';
      break;
    case 'SC_MULTI_CORE.MULTI_REPORTER.CHOOSE_CLOUPE.fork0.chnk0.main':
      res.percentage = '100';
      break;
  }

  if (res.percentage) {
    res.percentageLabel = res.percentage + '%';
  }

  return res;
});

const ProgressProps = computed<PlProgressCellProps>(() => {
  return {
    stage: parsed.value.stage === 'Queued' ? 'not_started' : 'running',
    step: parsed.value.stage || '',
    progress: parsed.value.percentage ? +parsed.value.percentage : 0,
    progressString: parsed.value.percentageLabel || ''
  };
});
</script>

<template>
  <PlAgCellProgress v-bind="{ params: { ...props.params, ...ProgressProps } }" />
</template>
