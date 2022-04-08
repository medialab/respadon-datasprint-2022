import Graph from 'graphology';

import { ForceLayoutSupervisorParameters, NodeState } from './types';

export function assignLayoutChanges(
  graph: Graph,
  nodeStates: Record<string, NodeState>,
  params: ForceLayoutSupervisorParameters
) {
  const { nodeXAttribute: x, nodeYAttribute: y, nodeZAttribute: z } = params;

  graph.updateEachNodeAttributes(
    (n, attr) => {
      const state = nodeStates[n];

      if (!state || state.fixed) return attr;

      attr[x] = state.x;
      attr[y] = state.y;
      attr[z] = state.z;

      return attr;
    },
    { attributes: ['x', 'y', 'z'] }
  );
}
