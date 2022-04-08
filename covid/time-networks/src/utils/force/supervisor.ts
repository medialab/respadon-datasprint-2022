import Graph from 'graphology';
import isGraph from 'graphology-utils/is-graph';
import resolveDefaults from 'graphology-utils/defaults';

import DEFAULTS from './defaults';
import iterate from './iterate';
import { assignLayoutChanges } from './helpers';
import { ForceLayoutParameters, ForceLayoutSupervisorParameters, NodeState } from './types';

class ForceSupervisor {
  callbacks: Record<string, () => void>;

  graph: Graph;
  params: ForceLayoutParameters;
  nodeStates: Record<string, NodeState>;
  frameID: number | null;
  running = false;
  killed = false;

  constructor(graph: Graph, params: Partial<ForceLayoutSupervisorParameters>) {
    // Validation
    if (!isGraph(graph)) throw new Error('the given graph is not a valid graphology instance.');

    params = resolveDefaults(params, DEFAULTS);

    this.callbacks = {};

    if (params.onConverged) this.callbacks.onConverged = params.onConverged;

    this.graph = graph;
    this.params = params as ForceLayoutParameters;
    this.nodeStates = {};
    this.frameID = null;
  }

  isRunning() {
    return this.running;
  }

  runFrame() {
    iterate(this.graph, this.nodeStates, this.params);

    assignLayoutChanges(this.graph, this.nodeStates, this.params);

    this.frameID = window.requestAnimationFrame(() => this.runFrame());
  }

  stop() {
    this.running = false;

    if (this.frameID !== null) {
      window.cancelAnimationFrame(this.frameID);
      this.frameID = null;
    }

    return this;
  }

  start() {
    if (this.killed) throw new Error('layout was killed.');

    if (this.running) return;

    this.running = true;
    this.runFrame();
  }

  kill() {
    this.stop();
    this.nodeStates = {};
    this.killed = true;

    // TODO: cleanup events
  }
}

export default ForceSupervisor;
