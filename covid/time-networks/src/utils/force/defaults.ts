import { ForceLayoutParameters } from './types';

const DEFAULTS: ForceLayoutParameters = {
  nodeXAttribute: 'x',
  nodeYAttribute: 'y',
  nodeZAttribute: 'z',
  isNodeFixed: 'fixed',
  shouldSkipNode: null,
  shouldSkipEdge: null,
  maxIterations: null,
  mutator: null,
  settings: {
    attraction: 0.0005,
    repulsion: 0.1,
    gravity: 0.0001,
    inertia: 0.6,
    maxMove: 200,
  },
};

export default DEFAULTS;
