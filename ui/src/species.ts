export const speciesOptions = [
  { text: 'Homo sapiens (GRCh38)', value: 'homo-sapiens' },
  { text: 'Mus musculus (GRCm39)', value: 'mus-musculus' },
  { text: 'Saccharomyces cerevisiae (R64-1-1)', value: 'saccharomyces-cerevisiae' },
  { text: 'Rattus norvegicus (mRatBN7.2)', value: 'rattus-norvegicus' },
  { text: 'Danio rerio (GRCz11)', value: 'danio-rerio' },
  { text: 'Drosophila Melanogaster (BDGP6.46)', value: 'drosophila-melanogaster' },
  { text: 'Arabidopsis Thaliana (TAIR10)', value: 'arabidopsis-thaliana' },
  { text: 'Caenorhabditis Elegans (WBcel235)', value: 'caenorhabditis-elegans' },
  { text: 'Gallus Gallus (GRCg7b)', value: 'gallus-gallus' },
  { text: 'Bos Taurus (ARS-UCD1.3)', value: 'bos-taurus' },
  { text: 'Sus Scrofa (Sscrofa11.1)', value: 'sus-scrofa' },
  { text: 'Test genome (v1)', value: 'test-species' },
] as const;

export type SpeciesName = (typeof speciesOptions)[number]['value'];
