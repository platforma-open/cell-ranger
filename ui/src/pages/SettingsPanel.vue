<script setup lang="ts">
import type { PlRef } from '@platforma-sdk/model';
import { plRefsEqual } from '@platforma-sdk/model';
import { PlDropdown, PlDropdownRef } from '@platforma-sdk/ui-vue';
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
</template>
