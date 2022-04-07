/**
 * This script takes as arguments two gexf files exported from the network visualization of hyphe
 * and returns a unified graphology graph
 * Nodes get a property "period_type" with enum{3}: ["past", "future", "bridge"]
 * Edges get a property "period_type" with enum{5}: ["past", "future", "bridge", "past_bridge", "future_bridge"]
 */
const Graph = require('graphology');
const forceAtlas2 = require('graphology-layout-forceatlas2');

const pastEdgeColor = 'rgb(211, 121, 101)',
      pastNodeColor = 'rgb(201, 43, 8)',

      bridgeEdgeColor = 'rgb(151, 162, 222)',
      bridgeNodeColor = 'rgb(79, 99, 203)',

      futureEdgeColor = 'rgb(166, 214, 117)',
      futureNodeColor = 'rgb(38, 139, 60)';


const buildBridgingNetwork = (graph1, graph2) => {

  console.log('Starting to bridge the two graphs');

  const nodesFromGraphPast = new Set();
  const nodesFromGraphFuture = new Set();

  graph1.forEachNode((node) => {
    // console.log(graph.getNodeAttributes(node));
    nodesFromGraphPast.add(graph1.getNodeAttribute(node, 'label'));
  });
  graph2.forEachNode((node) => {
    nodesFromGraphFuture.add(graph2.getNodeAttribute(node, 'label'));
  });

  const nodesLabelsFromBothYears = new Set(
    [...nodesFromGraphPast].filter(label => nodesFromGraphFuture.has(label))
  )
  const nodesLabelsFromPastOnly = new Set(
    [...nodesFromGraphPast].filter(label => !nodesFromGraphFuture.has(label))
  )
  const nodesLabelsFromFutureOnly = new Set(
    [...nodesFromGraphFuture].filter(label => !nodesFromGraphPast.has(label))
  )
  console.log('Past : %s nodes', [...nodesLabelsFromPastOnly].length);
  console.log('Future : %s nodes', [...nodesLabelsFromFutureOnly].length);
  console.log('Both years : %s nodes', [...nodesLabelsFromBothYears].length);
  // create new graph
  const resultGraph = new Graph();
  // store ids of nodes from past graph
  const nodesIdsFromPastOnly = new Set();
  // store ids of nodes from future graph
  const nodesIdsFromFutureOnly = new Set();
  // store ids of nodes from future graph concerning the bridge
  const nodesIdsFromBothYears = new Set();
  // iterate within past nodes to fill nodesIdsFromPastOnly
  graph1.forEachNode((nodeId, attributes) => {
    if (nodesLabelsFromPastOnly.has(attributes['label'])) {
      nodesIdsFromPastOnly.add(nodeId)
    }
  });
  // iterate within future nodes to fill nodesIdsFromFutureOnly and nodesIdsFromBothYears
  graph2.forEachNode((nodeId, attributes) => {
    if (nodesLabelsFromBothYears.has(attributes['label'])) {
      nodesIdsFromBothYears.add(nodeId)
    } else if (nodesLabelsFromFutureOnly.has(attributes['label'])) {
      nodesIdsFromFutureOnly.add(nodeId)
    }
  });
  // record past-to-future id links
  const pastIdToFutureIdForBridgeNodesMap = {};
  const bridgeLabelsProcessed = new Set();
  // @todo this is expensive, could be improved by setting label-to-id maps previously
  let numberOfLabelDuplicates = 0;
  [...nodesLabelsFromBothYears].forEach(label => {
    graph1.forEachNode((id1, attr1) => {
      if (attr1.label === label) {
        graph2.forEachNode((id2, attr2) => {
          if (attr2['label'] === label) {
            if (!bridgeLabelsProcessed.has(label)) {
              pastIdToFutureIdForBridgeNodesMap[id1] = id2;
              // console.log('label', label);
              bridgeLabelsProcessed.add(label);
            } else {
              numberOfLabelDuplicates++;
            }
            return;
          }
        })
        return;
      }
    })
  });
  // control we are doing no crap
  console.log('%s duplicates', numberOfLabelDuplicates)

  const pastIdsToNewIdsMap = {};
  const futureIdsToNewIdsMap = {};
  let indexCounter = 0;
  // add past nodes to new graph
  [...nodesIdsFromPastOnly].forEach(nodeId => {
    const attributes = graph1.getNodeAttributes(nodeId);
    pastIdsToNewIdsMap[nodeId] = indexCounter;
    resultGraph.addNode(indexCounter, {
      ...attributes,
      period_type: 'past'
    });
    indexCounter++;
  });
  // add bridge nodes to new graph
  [...nodesIdsFromBothYears].forEach(nodeId => {
    const attributes = graph2.getNodeAttributes(nodeId);
    futureIdsToNewIdsMap[nodeId] = indexCounter;
    // console.log('node id', nodeId);
    resultGraph.addNode(indexCounter, {
      ...attributes,
      period_type: 'bridge'
    });
    indexCounter++;
  });
  // add future nodes to new graph
  [...nodesIdsFromFutureOnly].forEach(nodeId => {
    const attributes = graph2.getNodeAttributes(nodeId);
    futureIdsToNewIdsMap[nodeId] = indexCounter;
    resultGraph.addNode(indexCounter, {
      ...attributes,
      period_type: 'future'
    });
    indexCounter++;
  });
  // for logging purpose
  let numberOfPastEdges = 0,
    numberOfPastToBridgeEdges = 0,
    numberOfBridgeEdges = 0,
    numberOfBridgeToFutureEdges = 0,
    numberOfFutureEdges = 0;
  // iterate within past edges
  graph1.forEachEdge((edge, attr, source, target) => {
    // console.log(edge, attr, source, target)
    let newSourceId;
    let newTargetId;
    let edgeType;
    const sourceLabel = graph1.getNodeAttribute(source, 'label');
    const targetLabel = graph1.getNodeAttribute(target, 'label');
    // both are past
    if (nodesLabelsFromPastOnly.has(sourceLabel) && nodesLabelsFromPastOnly.has(targetLabel)) {
      edgeType = 'past';
      newSourceId = pastIdsToNewIdsMap[source];
      newTargetId = pastIdsToNewIdsMap[target];
      numberOfPastEdges++;
    }
    // both are bridge
    else if (nodesLabelsFromBothYears.has(sourceLabel) && nodesLabelsFromBothYears.has(targetLabel)) {
      edgeType = 'bridge';
      newSourceId = futureIdsToNewIdsMap[pastIdToFutureIdForBridgeNodesMap[source]];
      newTargetId = futureIdsToNewIdsMap[pastIdToFutureIdForBridgeNodesMap[target]];
      numberOfBridgeEdges++;
    }
    // source is bridge
    else if (nodesLabelsFromBothYears.has(sourceLabel)) {
      edgeType = 'past_bridge';
      newSourceId = futureIdsToNewIdsMap[pastIdToFutureIdForBridgeNodesMap[source]];
      newTargetId = pastIdsToNewIdsMap[target];
      numberOfPastToBridgeEdges++;
    }
    // target is bridge
    else {
      edgeType = 'past_bridge';
      newSourceId = pastIdsToNewIdsMap[source];
      newTargetId = futureIdsToNewIdsMap[pastIdToFutureIdForBridgeNodesMap[target]];
      numberOfPastToBridgeEdges++;
    }
    if (newSourceId !== undefined && newTargetId !== undefined) {
      resultGraph.addEdge(newSourceId, newTargetId, {
        ...attr,
        period_type: edgeType
      })
    } else {
      console.log('problem in graph1', attr, { source, target, newSourceId, newTargetId});
    }
  })
  // iterate within future edges
  graph2.forEachEdge((edge, attr, source, target) => {
    let newSourceId;
    let newTargetId;
    let edgeType;
    const sourceLabel = graph2.getNodeAttribute(source, 'label');
    const targetLabel = graph2.getNodeAttribute(target, 'label');
    // both are future
    if (nodesLabelsFromFutureOnly.has(sourceLabel) && nodesLabelsFromFutureOnly.has(targetLabel)) {
      edgeType = 'future';
      newSourceId = futureIdsToNewIdsMap[source];
      newTargetId = futureIdsToNewIdsMap[target];
      numberOfFutureEdges++;
    }
    // both are bridge
    else if (nodesLabelsFromBothYears.has(sourceLabel) && nodesLabelsFromBothYears.has(targetLabel)) {
      // @todo handle bridge issues
      edgeType = 'bridge';
      newSourceId = futureIdsToNewIdsMap[source];
      newTargetId = futureIdsToNewIdsMap[target];
      numberOfBridgeEdges++;
      // console.log('both are bridge', newSourceId, newTargetId);
    }
    // source is bridge
    else if (nodesLabelsFromBothYears.has(sourceLabel)) {
      edgeType = 'future_bridge';
      newSourceId = futureIdsToNewIdsMap[source];
      newTargetId = futureIdsToNewIdsMap[target];
      numberOfBridgeToFutureEdges++;
      // console.log('source is bridge', newSourceId, newTargetId);

    }
    // target is bridge
    else {
      edgeType = 'future_bridge';
      newSourceId = futureIdsToNewIdsMap[source];
      newTargetId = futureIdsToNewIdsMap[target];
      numberOfBridgeToFutureEdges++;
      // console.log('target is bridge', newSourceId, newTargetId);
    }
    if (newSourceId !== undefined && newTargetId !== undefined) {
      // adding edge if it is new
      if (!resultGraph.hasEdge(newSourceId, newTargetId)) {
        resultGraph.addEdge(newSourceId, newTargetId, {
          ...attr,
          period_type: edgeType
        })
      }
      // @todo weighten existing edge in the bridge ?

    } else {
      console.log('problem in graph2', attr, { source, target, newSourceId, newTargetId});
    }
  })
  // set nodes color
  resultGraph.forEachNode((id, attr) => {
    let color;
    switch (attr.period_type) {
      case 'past':
        color = pastNodeColor;
        break;
      case 'bridge':
        color = bridgeNodeColor;
        break;
      case 'future':
      default:
        color = futureNodeColor;
        break;
    }
    resultGraph.setNodeAttribute(id, 'color', color);
  });
  // set edges color
  resultGraph.forEachEdge((id, attr) => {
    let color;
    switch (attr.period_type) {
      case 'past':
      case 'past_bridge':
        color = pastEdgeColor;
        break;
      case 'bridge':
        color = bridgeEdgeColor;
        break;
      case 'future':
      case 'future_bridge':
      default:
        color = futureEdgeColor;
        break;
    }
    resultGraph.setEdgeAttribute(id, 'color', color);
  });
  console.log('Number of past edges : ', numberOfPastEdges);
  console.log('Number of past to bridge edges : ', numberOfPastToBridgeEdges);
  console.log('Number of bridge edges : ', numberOfBridgeEdges);
  console.log('Number of bridge to future edges : ', numberOfBridgeToFutureEdges);
  console.log('Number of future edges : ', numberOfFutureEdges)

  // Run force atlas spatialization
  forceAtlas2.assign(resultGraph, {iterations: 50});
  return resultGraph;
}
module.exports = buildBridgingNetwork;