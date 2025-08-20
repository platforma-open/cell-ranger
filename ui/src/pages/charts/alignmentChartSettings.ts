import {
  Gradient,
} from '@platforma-sdk/ui-vue';

export function getMappingChartSettings(summary: Record<string, string> | undefined) {
  const parsePercent = (s: string | undefined): number => {
    if (!s) return 0;
    const v = parseFloat(s.replace('%', '').trim());
    return isNaN(v) ? 0 : v;
  };

  const mappedToGenome = parsePercent(summary?.['Reads Mapped to Genome']);
  const mappedConfident = parsePercent(summary?.['Reads Mapped Confidently to Genome']);
  const confIntergenic = parsePercent(summary?.['Reads Mapped Confidently to Intergenic Regions']);
  const confIntronic = parsePercent(summary?.['Reads Mapped Confidently to Intronic Regions']);
  const confExonic = parsePercent(summary?.['Reads Mapped Confidently to Exonic Regions']);

  const unmapped = Math.max(0, 100 - mappedToGenome);
  const mappedNotConfident = Math.max(0, mappedToGenome - mappedConfident);

  const magma = Gradient('magma');
  const segments = [
    { label: 'Confidently Intergenic', value: confIntergenic, color: '#42884E' },
    { label: 'Confidently Intronic', value: confIntronic, color: '#6BD67D' },
    { label: 'Confidently Exonic', value: confExonic, color: '#A6E6B1' },
    { label: 'Mapped (not confident)', value: mappedNotConfident, color: magma.getNthOf(3, 9) },
    { label: 'Unmapped', value: unmapped, color: magma.getNthOf(5, 9) },
  ];

  // const total = segments.reduce((s, x) => s + x.value, 0) || 1;
  const total = 100;

  return {
    title: 'Alignments',
    data: segments.map((s) => ({
      label: s.label,
      value: s.value,
      color: s.color,
      description: [s.label, 'Fraction:' + Math.round((s.value * 100) / total) + '%'].join('\n'),
    })),
  };
}
