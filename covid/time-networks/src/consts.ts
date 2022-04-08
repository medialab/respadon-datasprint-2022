import Graph from 'graphology';

export const EDGE_TYPE_HYPERTEXT = 'HYPERTEXT';
export const EDGE_TYPE_CONTINUITY = 'CONTINUITY';

export const Z_OFFSET = 400;

export const COLOR_MODES = [
  { id: 'types', label: 'By actor types' },
  { id: 'lifecycle', label: 'By lifecycle (Appears / Disappears / Remains)' },
] as const;
export type ColorMode = typeof COLOR_MODES[number]['id'];

export const LAYERS: { path: string; year: string; graph: Graph | null }[] = [
  // 1. All data from yesterday:
  // { path: '/data/20220407/Covid_2020.gexf', year: '2020', graph: null },
  // { path: '/data/20220407/Covid_2021.gexf', year: '2021', graph: null },
  // { path: '/data/20220407/Covid_2022.gexf', year: '2022', graph: null },
  // 2. Without 2021:
  // { path: '/data/20220407/Covid_2020.gexf', year: '2020', graph: null },
  // { path: '/data/20220407/Covid_2022.gexf', year: '2022', graph: null },
  // 3. All data from today:
  // { path: '/data/20220408/covid_2020.gexf', year: '2020', graph: null },
  // { path: '/data/20220408/covid_2021.gexf', year: '2021', graph: null },
  // { path: '/data/20220408/covid_2022.gexf', year: '2022', graph: null },
  // 4. Today, 2 years, updated:
  { path: '/data/20220408/covid_2020_latest.gexf', year: '2020', graph: null },
  { path: '/data/20220408/covid_2021_latest.gexf', year: '2021', graph: null },
];

// 1, 2
// export const COLORS_FIELD = 'Type_Acteur';
// 3, 4
export const COLORS_FIELD = 'Acteur';
export const COLORS_VALUES = new Set<string>();
export const COLORS_MAPPING: Record<string, string> = {};

export const LIFECYCLE_COLORS_MAPPING = {
  appears: 'green',
  disappears: 'red',
  remains: 'grey',
};
