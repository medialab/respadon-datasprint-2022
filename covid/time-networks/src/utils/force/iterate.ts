import Graph from 'graphology';
import { EdgePredicate, NodePredicate } from 'graphology-types';
import { createEdgeValueGetter, createNodeValueGetter } from 'graphology-utils/getters';

import { ForceLayoutParameters, NodeState } from './types';

export default function iterate(
  graph: Graph,
  nodeStates: Record<string, NodeState>,
  params: ForceLayoutParameters
) {
  const { nodeXAttribute: xKey, nodeYAttribute: yKey, nodeZAttribute: zKey, mutator } = params;
  const { attraction, repulsion, gravity, inertia = 0, maxMove = Infinity } = params.settings;

  const isNodeFixed = createNodeValueGetter(params.isNodeFixed);
  const shouldSkipNode = createNodeValueGetter(params.shouldSkipNode as NodePredicate, false);
  const shouldSkipEdge = createEdgeValueGetter(params.shouldSkipEdge as EdgePredicate, false);

  const nodes = graph.filterNodes((n, attr) => {
    return !shouldSkipNode.fromEntry(n, attr);
  });

  const adjustedOrder = nodes.length;

  // Check nodeStates and inertia
  for (let i = 0; i < adjustedOrder; i++) {
    const n = nodes[i];
    const attr = graph.getNodeAttributes(n);
    const nodeState = nodeStates[n];

    if (!nodeState)
      nodeStates[n] = {
        dx: 0,
        dy: 0,
        dz: 0,
        x: attr[xKey] || 0,
        y: attr[yKey] || 0,
        z: attr[zKey] || 0,
      };
    else
      nodeStates[n] = {
        dx: nodeState.dx * inertia,
        dy: nodeState.dy * inertia,
        dz: nodeState.dz * inertia,
        x: nodeState.x || attr[xKey] || 0,
        y: nodeState.y || attr[yKey] || 0,
        z: nodeState.z || attr[zKey] || 0,
      };
  }

  // Repulsion
  if (repulsion)
    for (let i = 0; i < adjustedOrder; i++) {
      const n1 = nodes[i];
      const n1State = nodeStates[n1];

      for (let j = i + 1; j < adjustedOrder; j++) {
        const n2 = nodes[j];
        const n2State = nodeStates[n2];

        if (n1State.z !== n2State.z) continue;

        // Compute distance:
        const dx = n2State.x - n1State.x;
        const dy = n2State.y - n1State.y;
        const dz = n2State.z - n1State.z;
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;

        // Repulse nodes relatively to 1 / distance:
        const repulsionX = (repulsion / distance) * dx;
        const repulsionY = (repulsion / distance) * dy;
        const repulsionZ = (repulsion / distance) * dz;
        n1State.dx -= repulsionX;
        n1State.dy -= repulsionY;
        n1State.dz -= repulsionZ;
        n2State.dx += repulsionX;
        n2State.dy += repulsionY;
        n2State.dz += repulsionZ;
      }
    }

  // Attraction
  if (attraction)
    graph.forEachEdge((edge, attr, source, target, sourceAttr, targetAttr, undirected) => {
      if (source === target) return;

      if (
        shouldSkipNode.fromEntry(source, sourceAttr) ||
        shouldSkipNode.fromEntry(target, targetAttr)
      )
        return;

      if (shouldSkipEdge.fromEntry(edge, attr, source, target, sourceAttr, targetAttr, undirected))
        return;

      const weight = attr.weight || 1;
      const n1State = nodeStates[source];
      const n2State = nodeStates[target];

      // Compute distance:
      const dx = n2State.x - n1State.x;
      const dy = n2State.y - n1State.y;
      const dz = n2State.z - n1State.z;

      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;

      // Attract nodes relatively to their distance:
      const attractionX = attraction * distance * dx;
      const attractionY = attraction * distance * dy;
      const attractionZ = attraction * distance * dz;
      n1State.dx += attractionX * weight;
      n1State.dy += attractionY * weight;
      n1State.dz += attractionZ * weight;
      n2State.dx -= attractionX * weight;
      n2State.dy -= attractionY * weight;
      n2State.dz -= attractionZ * weight;
    });

  // Gravity
  if (gravity)
    for (let i = 0; i < adjustedOrder; i++) {
      const n = nodes[i];
      const nodeState = nodeStates[n];

      // Attract nodes to [0, 0, 0] relatively to the distance:
      const { x, y, z } = nodeState;
      const distance = Math.sqrt(x * x + y * y + z * z) || 1;
      nodeStates[n].dx -= x * gravity * distance;
      nodeStates[n].dy -= y * gravity * distance;
      nodeStates[n].dz -= z * gravity * distance;
    }

  // Apply forces
  for (let i = 0; i < adjustedOrder; i++) {
    const n = nodes[i];
    let nodeState = nodeStates[n];

    const distance = Math.sqrt(
      nodeState.dx * nodeState.dx + nodeState.dy * nodeState.dy + nodeState.dz * nodeState.dz
    );

    if (distance > maxMove) {
      nodeState.dx *= maxMove / distance;
      nodeState.dy *= maxMove / distance;
      nodeState.dz *= maxMove / distance;
    }

    if (mutator) {
      mutator(nodeState);
    }

    if (!isNodeFixed.fromGraph(graph, n)) {
      nodeState.x += nodeState.dx;
      nodeState.y += nodeState.dy;
      nodeState.z += nodeState.dz;
      nodeState.fixed = false;
    } else {
      nodeState.fixed = true;
    }

    // NOTE: possibility to assign here to save one loop in the future
  }
}
