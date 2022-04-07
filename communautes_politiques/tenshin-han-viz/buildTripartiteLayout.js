/**
 * This script takes as arguments two gexf files exported from the network visualization of hyphe
 * and returns a unified graphology graph
 * Nodes get a property "period_type" with enum{3}: ["past", "future", "bridge"]
 * Edges get a property "period_type" with enum{5}: ["past", "future", "bridge", "past_bridge", "future_bridge"]
 */
const Graph = require('graphology');
const forceAtlas2 = require('graphology-layout-forceatlas2');
const noverlap = require('graphology-layout-noverlap');

const extent = arr => {
  let max = -Infinity;
  let min = Infinity;
  arr.forEach(num => {
    if (num < min) {
      min = num;
    } else if (num > max) {
      max = num;
    }
  })
  return [min, max]
}

const buildTripartiteLayout = (graph, laterlMarginPortion = 0.7) => {
  /**
   * STEP 1 : build three layouts of the separate layouts
   */
  const pastGraph = new Graph();
  const bridgeGraph = new Graph();
  const futureGraph = new Graph();
  // add nodes
  graph.forEachNode((id, attrs) => {
    const { period_type } = attrs
    switch (period_type) {
      case 'past':
        pastGraph.addNode(id, attrs);
        break;
      case 'bridge':
        bridgeGraph.addNode(id, attrs);
        break;
      case 'future':
      default:
        futureGraph.addNode(id, attrs);
        break;
    }
  });
  // add edges
  graph.forEachEdge((id, attrs, source, target) => {
    const { period_type } = attrs;
    try {
      switch (period_type) {
        case 'past':
          // console.log('add past');
          // console.log('source', pastGraph.getNodeAttributes(source))
          // console.log('target', pastGraph.getNodeAttributes(target))
          pastGraph.addEdge(source, target, attrs);
          break;
        case 'bridge':
          // console.log('add bridge');
          bridgeGraph.addEdge(source, target, attrs);
          break;
        case 'future':
          // console.log('add future', period_type);
          futureGraph.addEdge(source, target, attrs);
          break;
        default:
          break;
      }
    }
    catch (e) {
      console.log(e)
    }

  });
  /**
   * STEP 2 : build layout
   */
  forceAtlas2.assign(pastGraph, { iterations: 50 });
  forceAtlas2.assign(bridgeGraph, { iterations: 50 });
  forceAtlas2.assign(futureGraph, { iterations: 50 });
  let positionsPast = noverlap(pastGraph, {maxIterations: 1000});
  let positionsBridge = noverlap(bridgeGraph, {maxIterations: 1000});
  let positionsFuture = noverlap(futureGraph, {maxIterations: 1000});
  const xExtent = extent([

    ...Object.values(positionsPast).map(({ x }) => x),
    ...Object.values(positionsBridge).map(({ x }) => x),
    ...Object.values(positionsFuture).map(({ x }) => x),

  ])
  const maxWidth = xExtent[1] - xExtent[0];
  const lateralMargin = maxWidth * laterlMarginPortion;
  positionsPast = Object.entries(positionsPast).reduce((res, [id, {x, y}]) => {
    return {
      ...res,
      [id]: {
        x: x - lateralMargin,
        y
      }
    }
  }, {});
  positionsFuture = Object.entries(positionsFuture).reduce((res, [id, {x, y}]) => {
    return {
      ...res,
      [id]: {
        x: x + lateralMargin,
        y
      }
    }
  }, {});
  /**
   * STEP 3 : apply new positions
   */
  graph.forEachNode((id, attr) => {
    if (positionsPast[id]) {
      graph.setNodeAttribute(id, 'x', positionsPast[id].x)
    } 
    else if (positionsBridge[id]) {
      graph.setNodeAttribute(id, 'x', positionsBridge[id].x)
    }
    else if (positionsFuture[id]) {
      graph.setNodeAttribute(id, 'x', positionsFuture[id].x)
    }
  })

  console.log('Starting to buildTripartiteLayout');

  return graph;
}
module.exports = buildTripartiteLayout;