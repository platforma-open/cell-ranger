import {
  BlockModel,
  createPFrameForGraphs,
  type InferOutputsType,
  isPColumn,
  isPColumnSpec,
  parseResourceMap,
  type PlRef,
  type ValueType,
} from "@platforma-sdk/model";

import { type GraphMakerState } from "@milaboratories/graph-maker";

export type UiState = {
  graphState: GraphMakerState;
};
/**
 * Block arguments coming from the user interface
 */
export type BlockArgs = {
  /**
   * Reference to the fastq data
   */
  ref?: PlRef;

  /**
   * Species settings
   */
  species?: string;

  /**
   * Block title
   */
  title?: string;
};

export const model = BlockModel.create()

  .withArgs<BlockArgs>({
    species: "homo-sapiens"
  })

  .withUiState<UiState>({
    graphState: {
      template: 'violin',
      title: 'Cell QC metrics',
      layersSettings: {
        violin: {
          fillColor: '#99E099'
        }
      }
    }
  })

  /**
   * Find possible options for the fastq input
   */
  .output("dataOptions", (ctx) => {
    return ctx.resultPool.getOptions((v) => {
      if (!isPColumnSpec(v)) return false;
      const domain = v.domain;
      return (
        v.name === "pl7.app/sequencing/data" &&
        (v.valueType as string) === "File" &&
        domain !== undefined &&
        (domain["pl7.app/fileExtension"] === "fastq" ||
          domain["pl7.app/fileExtension"] === "fastq.gz")
      );
    });
  })

  .output("labels", (ctx) => {
    const inputRef = ctx.args.ref;
    if (inputRef === undefined) return undefined;

    const inputSpec = ctx.resultPool.getSpecByRef(inputRef); // @TODO use resultPool.getPColumnSpecByRef after updating SDK
    if (inputSpec === undefined || !isPColumnSpec(inputSpec)) return undefined;

    const labels = ctx.findLabels(inputSpec.axesSpec[0]);
    if (!labels) return undefined;

    return labels;
  })

  /**
   * Preprocessing progress
   */
  .output("cellRangerProgress", (wf) => {
    return parseResourceMap(
      wf.outputs?.resolve("cellRangerProgress"),
      (acc) => acc.getLogHandle(),
      false
    );
  })

  /**
   * Last line from cell ranger output
   */
  .output("cellRangerProgressLine", (wf) => {
    return parseResourceMap(
      wf.outputs?.resolve("cellRangerProgress"),
      (acc) => acc.getLastLogs(1),
      false
    );
  })

  /**
   * P-frame with rawCounts
   */
  .output("rawCountsPf", (wf) => {
    const pCols = wf.outputs?.resolve("rawCountsPf")?.getPColumns();
    if (pCols === undefined) return undefined;

    return wf.createPFrame(pCols);
  })

  .output("rawCountsSpec", (wf) => {
    const pCols = wf.outputs?.resolve("rawCountsPf")?.getPColumns();
    if (pCols === undefined) return undefined;
    return pCols[0].spec;

  })

  .output("cellMetricsPf", (wf) => {
    const pCols = wf.outputs?.resolve("cellMetricsPf")?.getPColumns();
    if (pCols === undefined) return undefined;

    return wf.createPFrame(pCols);
  })

  .output("cellMetricsSpec", (wf) => {
    const pCols = wf.outputs?.resolve("cellMetricsPf")?.getPColumns();
    if (pCols === undefined) return undefined;
    return pCols[0].spec;

  })

  .output("webSummary", (wf) => {
    return parseResourceMap(
      wf.outputs?.resolve("cellRangerReport"),
      (acc) => acc.getFileHandle(),
      false
    );
  })

  /**
   * Returns true if the block is currently in "running" state
   */
  .output("isRunning", (ctx) => ctx.outputs?.getIsReadyOrError() === false)

  .sections((ctx) => {
    return [
      { type: "link", href: "/", label: "Settings" },
      { type: "link", href: "/CellQC", label: "Cell QC" }
    ];
  })

  .title((ctx) =>
    ctx.args.title
      ? `Cell Ranger - ${ctx.args.title}`
      : "Cell Ranger"
  )

  .done();

export type BlockOutputs = InferOutputsType<typeof model>;
