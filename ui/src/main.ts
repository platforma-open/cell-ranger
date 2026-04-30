import { BlockLayout } from '@platforma-sdk/ui-vue';
import type { ObjectPlugin } from 'vue';
import { createApp } from 'vue';
import { sdkPlugin } from './app';

createApp(BlockLayout).use(sdkPlugin as ObjectPlugin<[]>).mount('#app');
