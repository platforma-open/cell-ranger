import { model } from "@platforma-open/milaboratories.cell-ranger.model";
import { defineApp } from "@platforma-sdk/ui-vue";
import Settings from "./pages/MainPage.vue";

export const sdkPlugin = defineApp(model, (app) => {
  return {
    progress: () => {
      return app.model.outputs.isRunning
    },
    showErrorsNotification: true,
    routes: {
      "/": () => Settings,
      "/Report": () => Settings
    },
  };
});

export const useApp = sdkPlugin.useApp;
