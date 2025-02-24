import { ColDefProgress } from "@platforma-sdk/ui-vue";
import { ProgressLogWithInfo } from "@platforma-sdk/model";

const logLineRegex = /^(?<date>\d{4}-\d{2}-\d{2})\s+(?<time>\d{2}:\d{2}:\d{2})\s+\[(?<tag>[^\]]+)\]\s+\((?<status>[^)]+)\)\s+(?<identifier>.*)$/;

type Group ={
  date: string,
  time: string,
  tag: string,
  status: string,
  identifier: string
}

function match(raw: string) {
  return raw.match(logLineRegex)?.groups as Group | undefined;
}

export const parseProgress  = (progressLine: ProgressLogWithInfo | undefined): ColDefProgress => {
  const res: ColDefProgress = {
    status: 'not_started',
    percent: undefined, 
    text: '', // this text is in the left part of cell (main text)
    suffix: ''
  };

  if (!progressLine) {
    return res;
  }

  if (!progressLine.live) {
    res.status = 'done';
    res.text = 'Complete';
    return res;
  }

  const raw = progressLine.progressLine?.trim();

  if (!raw) {
    return res;
  }

  res.text = raw;

  res.status = 'running'; // Shows "infinite" progress if percent is not known

  const groups = match(raw);

  if (!groups) {
    return res;
  }

  res.text = groups.time + ' ' + groups.status + ' ' + groups.identifier;
  res.text = `[${groups.time}] (${groups.status}) ${groups.identifier}`;

  // Could we simply show "infinite" progress if the percentage is unknown?
  // switch (groups.identifier) {
  //   case 'SC_MULTI_CORE.MULTI_GEM_WELL_PROCESSOR.COUNT_GEM_WELL_PROCESSOR._BASIC_SC_RNA_COUNTER._MATRIX_COMPUTER.WRITE_BARCODE_INDEX':
  //     res.percent = '20';
  //     break;
  //   case 'SC_MULTI_CORE.MULTI_GEM_WELL_PROCESSOR.COUNT_GEM_WELL_PROCESSOR._BASIC_SC_RNA_COUNTER._MATRIX_COMPUTER.ALIGN_AND_COUNT':
  //     res.percent = '50';
  //     break;
  //   case 'SC_MULTI_CORE.MULTI_GEM_WELL_PROCESSOR.COUNT_GEM_WELL_PROCESSOR._BASIC_SC_RNA_COUNTER.WRITE_POS_BAM':
  //     res.percent = '75';
  //     break;
  //   case 'SC_MULTI_CORE.MULTI_REPORTER.CHOOSE_CLOUPE':
  //     res.percent = '100';
  //     break;
  // }

  return res;
};