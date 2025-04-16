import type {
  PColumnIdAndSpec,
} from '@platforma-sdk/model';
import {
  BlockModel,
  type InferOutputsType,
  isPColumn,
  isPColumnSpec,
  parseResourceMap,
  type PlRef,
} from '@platforma-sdk/model';

import { type GraphMakerState } from '@milaboratories/graph-maker';

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
    species: 'homo-sapiens',
  })

  .withUiState<UiState>({
    graphState: {
      template: 'violin',
      title: 'Cell QC metrics',
      // layersSettings: {
      //   violin: {
      //     fillColor: '#99E099',
      //   },
      // },
    },
  })

  /**
   * Find possible options for the fastq input
   */
  .output('dataOptions', (ctx) => {
    return ctx.resultPool.getOptions((v) => {
      if (!isPColumnSpec(v)) return false;
      const domain = v.domain;
      return (
        v.name === 'pl7.app/sequencing/data'
        && (v.valueType as string) === 'File'
        && domain !== undefined
        && (domain['pl7.app/fileExtension'] === 'fastq'
          || domain['pl7.app/fileExtension'] === 'fastq.gz')
      );
    });
  })

  .output('labels', (ctx) => {
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
  .output('cellRangerProgress', (wf) => {
    return parseResourceMap(
      wf.outputs?.resolve('cellRangerProgress'),
      (acc) => acc.getLogHandle(),
      false,
    );
  })

  /**
   * Last line from cell ranger output
   */
  .output('cellRangerProgressLine', (ctx) => {
    return ctx.outputs !== undefined
      ? parseResourceMap(
          ctx.outputs?.resolve('cellRangerProgress'),
          (acc) => acc.getProgressLogWithInfo(''),
          false,
        )
      : undefined;
  })

  /**
   * P-frame with rawCounts
   */
  .output('rawCountsPf', (wf) => {
    const pCols = wf.outputs?.resolve('rawCountsPf')?.getPColumns();
    if (pCols === undefined) return undefined;

    return wf.createPFrame(pCols);
  })

  .output('rawCountsSpec', (wf) => {
    const pCols = wf.outputs?.resolve('rawCountsPf')?.getPColumns();
    if (pCols === undefined) return undefined;
    return pCols[0].spec;
  })

// .output('cellMetricsPf', (wf) => {
//   const pCols = wf.outputs?.resolve('cellMetricsPf')?.getPColumns();
//   if (pCols === undefined) return undefined;

//   const valueTypes = [
//     'Int',
//     'Long',
//     'Float',
//     'Double',
//     'String',
//     'Bytes',
//   ] as ValueType[];
//   const upstream = wf.resultPool
//     .getData()
//     .entries.map((v) => v.obj)
//     .filter(isPColumn)
//     .filter((column) =>
//       valueTypes.find((valueType) => (valueType === column.spec.valueType),
//       ),
//     );

//   return createPFrameForGraphs(wf, [...pCols, ...upstream]);
// })

  .output('cellMetricsPf', (wf) => {
    const pCols = wf.outputs?.resolve('cellMetricsPf')?.getPColumns();
    if (pCols === undefined) return undefined;

    return wf.createPFrame(pCols);
  })

  // Pcolumns for plot defaults
  .output('cellMetricsPfDefaults', (wf) => {
    let pCols = wf.outputs?.resolve('cellMetricsPf')?.getPColumns();
    if (pCols === undefined) return undefined;

    // Add sample labels
    const upstream = wf.resultPool
      .getData()
      .entries.map((v) => v.obj)
      .filter(isPColumn)
      .filter((col) => col.spec.name === 'pl7.app/label');

    pCols = [...pCols, ...upstream];
    return pCols.map(
      (c) =>
        ({
          columnId: c.id,
          spec: c.spec,
        } satisfies PColumnIdAndSpec),
    );
  })

  .output('cellMetricsSpec', (wf) => {
    const pCols = wf.outputs?.resolve('cellMetricsPf')?.getPColumns();
    if (pCols === undefined) return undefined;
    return pCols[0].spec;
  })

  .output('webSummary', (wf) => {
    return parseResourceMap(
      wf.outputs?.resolve('cellRangerReport'),
      (acc) => acc.getFileHandle(),
      false,
    );
  })

  /**
   * Returns true if the block is currently in "running" state
   */
  .output('isRunning', (ctx) => ctx.outputs?.getIsReadyOrError() === false)

  .sections([
    { type: 'link', href: '/', label: 'Settings' },
    { type: 'link', href: '/CellQC', label: 'Cell QC' },
  ])

  .title((ctx) =>
    ctx.args.title
      ? `Cell Ranger - ${ctx.args.title}`
      : 'Cell Ranger',
  )

  .done();

export type BlockOutputs = InferOutputsType<typeof model>;
