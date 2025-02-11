<script setup lang="ts">
import { useApp } from "../app";
import { computed, ref } from 'vue';
const app = useApp();
const sampleId = defineModel<string | undefined>()

const report = computed(() => {
    const id = sampleId.value
    if (id === undefined) {
        console.warn("SampleId is undefined")
        return undefined
    }
    return app.model.outputs.webSummary?.data.find((it) => {
        return it.key.includes(id)
    })?.value

});
</script>

<template>
  <div title="Frame" width="1100" height="800" v-html="report" />
 {{report}} 
</template>
