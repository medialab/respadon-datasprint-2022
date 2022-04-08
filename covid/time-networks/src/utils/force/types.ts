import { EdgePredicate, NodePredicate } from 'graphology-types';

export type NodeState = {
  x: number;
  y: number;
  z: number;
  dx: number;
  dy: number;
  dz: number;
  fixed?: boolean;
};

export type ForceLayoutSettings = {
  attraction?: number;
  repulsion?: number;
  gravity?: number;
  inertia?: number;
  maxMove?: number;
};

export type ForceLayoutParameters = {
  nodeXAttribute: string;
  nodeYAttribute: string;
  nodeZAttribute: string;
  isNodeFixed: string | NodePredicate;
  shouldSkipNode: NodePredicate | null;
  shouldSkipEdge: EdgePredicate | null;
  mutator: ((state: NodeState) => void) | null;
  maxIterations: number | null;
  settings: ForceLayoutSettings;
};

export type ForceLayoutSupervisorParameters = Omit<ForceLayoutParameters, 'maxIterations'> & {
  onConverged?: () => void;
};
