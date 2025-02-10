import { model } from "@platforma-open/milaboratories.cell-ranger.model";
import { defineApp } from "@platforma-sdk/ui-vue";
import Settings from "./pages/MainPage.vue";
import Report from "./pages/Report.vue";
import CellQC from "./pages/CellQC.vue";

export const sdkPlugin = defineApp(model, (app) => {
  return {
    progress: () => {
      return app.model.outputs.isRunning
    },
    showErrorsNotification: true,
    routes: {
      "/": () => Settings,
      "/Report": () => Report,
      "/CellQC": () => CellQC
    },
  };
});

export const useApp = sdkPlugin.useApp;
