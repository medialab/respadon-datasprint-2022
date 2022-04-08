import Graph from 'graphology';
import noverlap from 'graphology-layout-noverlap';
import pagerank from 'graphology-metrics/centrality/pagerank';

import { EDGE_TYPE_HYPERTEXT } from '../consts';

export default function getProjectedGraph(fullGraph: Graph, year: string): Graph {
  const graph = fullGraph.nullCopy();

  // Initialize graph:
  fullGraph.forEachNode((node, attributes) => {
    if (attributes.year === year) graph.addNode(node, attributes);
  });
  fullGraph.forEachEdge((edge, attributes, source, target) => {
    if (attributes.edgeType === EDGE_TYPE_HYPERTEXT && attributes.year === year)
      graph.addEdgeWithKey(edge, source, target, attributes);
  });

  // Keep the graph updated:
  fullGraph.on('eachNodeAttributesUpdated', () => {
    graph.forEachNode((node) => {
      const { x, y } = fullGraph.getNodeAttributes(node);
      graph.setNodeAttribute(node, 'x', x);
      graph.setNodeAttribute(node, 'y', y);
    });
  });

  // Choose node sizes:
  pagerank.assign(graph);
  graph.forEachNode((node, attributes) => {
    graph.setNodeAttribute(node, 'size', attributes.pagerank * 200 + 4);
  });

  // Run some noverlap for readability:
  noverlap.assign(graph, {
    maxIterations: 100,
    settings: {
      ratio: 0.1,
    },
  });

  return graph;
}
