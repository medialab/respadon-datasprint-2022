import Graph from 'graphology';
import gexf from 'graphology-gexf/browser';
import circular from 'graphology-layout/circular';

// @ts-ignore
import PALETTES from 'iwanthue/precomputed/k-means-pimp';

import {
  COLORS_FIELD,
  COLORS_MAPPING,
  COLORS_VALUES,
  EDGE_TYPE_CONTINUITY,
  EDGE_TYPE_HYPERTEXT,
  LAYERS,
  Z_OFFSET,
} from '../consts';
import { abstractSynchronousLayout } from './force';
import { NodeState } from './force/types';
import { cropToLargestConnectedComponent } from 'graphology-components';

export default async function getFullGraph() {
  // 1. Load each graph file:
  for (let i = 0; i < LAYERS.length; i++) {
    const layer = LAYERS[i];
    const data = await fetch(layer.path).then((r) => r.text());
    const graph = gexf.parse(Graph, data);
    circular.assign(graph);
    layer.graph = graph;
  }

  // 2. Build full graph:
  const fullGraph = new Graph();
  const urlsIndex: Record<string, Set<string>> = {};
  LAYERS.forEach((layer, i, a) => {
    const year = layer.year;
    const graph = layer.graph as Graph;

    // a. Add the layer for that graph:
    graph.forEachNode((_, attributes) => {
      const url = attributes.label;
      // 1, 2:
      // const colorValue = [(attributes[COLORS_FIELD] || []).join(', ').toLowerCase()];
      // 3, 4:
      const colorValue = ((attributes[COLORS_FIELD] || []).join(', ').split(', ') || []).map(
        (v: string) => v.toLowerCase()
      );
      urlsIndex[url] = urlsIndex[url] || new Set();
      urlsIndex[url].add(year);
      fullGraph.addNode(year + '-' + url, {
        year,
        url,
        label: url,
        x: attributes.x,
        y: attributes.y,
        z: i * Z_OFFSET,
        rawAttributes: attributes,
        [COLORS_FIELD]: colorValue,
      });

      colorValue.forEach((v: string) => !!v && COLORS_VALUES.add(v));
    });
    graph.forEachEdge((edge, attributes, _1, _2, { label: sourceUrl }, { label: targetUrl }) => {
      if (!fullGraph.hasNode(year + '-' + sourceUrl) || !fullGraph.hasNode(year + '-' + targetUrl))
        return;
      fullGraph.addEdgeWithKey(year + '-' + edge, year + '-' + sourceUrl, year + '-' + targetUrl, {
        edgeType: EDGE_TYPE_HYPERTEXT,
        year,
        attributes,
      });
    });

    // b. Link with previous layer:
    if (i > 0) {
      const previousYear = a[i - 1].year;
      graph.forEachNode((_, { label: url }) => {
        if (urlsIndex[url]?.has(previousYear)) {
          fullGraph.addEdgeWithKey(
            previousYear + '->' + year + '-' + url,
            previousYear + '-' + url,
            year + '-' + url,
            {
              weight: 0.3,
              edgeType: EDGE_TYPE_CONTINUITY,
              yearFrom: previousYear,
              yearTo: year,
            }
          );
        }
      });
    }
  });

  // 3. Fine tune node attributes:
  fullGraph.forEachNode((node, attributes) => {
    const yearIndex = LAYERS.findIndex((layer) => layer.year === attributes.year);
    const isFirstYear = yearIndex === 0;
    const isLastYear = yearIndex === LAYERS.length - 1;

    const nextYear = !isLastYear && LAYERS[yearIndex + 1].year;
    const previousYear = !isFirstYear && LAYERS[yearIndex - 1].year;

    const disappears = nextYear && !urlsIndex[attributes.url]?.has(nextYear);
    const appears = previousYear && !urlsIndex[attributes.url]?.has(previousYear);

    fullGraph.mergeNodeAttributes(node, {
      size: (urlsIndex[attributes.url]?.size || 0) * 3,
      lifecycle: disappears ? 'disappears' : appears ? 'appears' : 'remains',
    });
  });

  // 4. Only keep the largest component:
  cropToLargestConnectedComponent(fullGraph);

  // 5. Prerun the layered layout:
  abstractSynchronousLayout(fullGraph, {
    maxIterations: 1000,
    mutator: (state: NodeState) => {
      state.dz = 0;
    },
  });

  // 6. Choose colors:
  const palette = PALETTES[COLORS_VALUES.size];
  Array.from(COLORS_VALUES).forEach((v, i) => (COLORS_MAPPING[v] = palette[i] || 'grey'));

  // @ts-ignore
  window.GRAPH = fullGraph;

  return fullGraph;
}
