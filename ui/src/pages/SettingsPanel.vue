<script setup lang="ts">
import type { PlRef } from '@platforma-sdk/model';
import { plRefsEqual } from '@platforma-sdk/model';
import {
  PlAccordionSection,
  PlDropdown,
  PlDropdownRef,
  PlNumberField,
} from '@platforma-sdk/ui-vue';
import { useApp } from '../app';
import { speciesOptions } from '../species';

const app = useApp();

function setInput(inputRef?: PlRef) {
  app.model.args.ref = inputRef;
  if (inputRef) {
    app.model.ui.title = app.model.outputs.dataOptions?.find((o) =>
      plRefsEqual(o.ref, inputRef),
    )?.label;
  } else {
    app.model.ui.title = undefined;
  }
}
</script>

<template>
  <PlDropdownRef
    v-model="app.model.args.ref"
    :options="app.model.outputs.dataOptions"
    label="Select dataset"
    clearable
    @update:model-value="setInput"
  />
  <PlDropdown
    v-model="app.model.args.species"
    :options="speciesOptions"
    label="Select species"
  />
  <PlAccordionSection label="Advanced Settings">
    <PlNumberField
      v-model="app.model.args.mem"
      label="Memory (GiB)"
      :min-value="1"
      :step="1"
      :max-value="1012"
      placeholder="64"
    >
      <template #tooltip>
        Sets the amount of memory to use for the clustering.
      </template>
    </PlNumberField>

    <PlNumberField
      v-model="app.model.args.cpu"
      label="CPU (cores)"
      :min-value="1"
      :step="1"
      :max-value="128"
      placeholder="16"
    >
      <template #tooltip>
        Sets the number of CPU cores to use for the clustering.
      </template>
    </PlNumberField>
  </PlAccordionSection>
</template>
