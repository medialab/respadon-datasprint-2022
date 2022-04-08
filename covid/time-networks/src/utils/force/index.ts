import Graph from 'graphology';
import isGraph from 'graphology-utils/is-graph';
import resolveDefaults from 'graphology-utils/defaults';

import iterate from './iterate';
import DEFAULTS from './defaults';
import { ForceLayoutParameters } from './types';
import { assignLayoutChanges } from './helpers';

export function abstractSynchronousLayout(
  graph: Graph,
  params: Partial<ForceLayoutParameters> = {}
) {
  if (!isGraph(graph)) throw new Error('the given graph is not a valid graphology instance.');

  const maxIterations = params.maxIterations;

  const allParams = resolveDefaults(params, DEFAULTS) as ForceLayoutParameters;

  if (typeof maxIterations !== 'number' || maxIterations <= 0)
    throw new Error('you should provide a positive number of maximum iterations.');

  // Iteration state
  const nodeStates = {};
  let i;

  // Iterating
  for (i = 0; i < maxIterations; i++) {
    iterate(graph, nodeStates, allParams);
  }

  assignLayoutChanges(graph, nodeStates, allParams);
}
