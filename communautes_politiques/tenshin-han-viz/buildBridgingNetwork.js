const fs = require('fs')
const Graph = require('graphology');
const gexf = require('graphology-gexf');



const graph1 = gexf.parse(Graph, fs.readFileSync('melenchon_2017.gexf', 'utf8'));
const graph2 = gexf.parse(Graph, fs.readFileSync('melenchon_2022.gexf', 'utf8'));

const buildBridgingNetwork = (graph1, graph2) => {

  const nodesFromGraphPast = new Set();
  const nodesFromGraphFuture = new Set();

  graph1.forEachNode((node) => {
    // console.log(graph.getNodeAttributes(node));
    nodesFromGraphPast.add(graph1.getNodeAttribute(node, 'label'));
  });
  graph2.forEachNode((node) => {
    nodesFromGraphFuture.add(graph2.getNodeAttribute(node, 'label'));
  });


  const nodesFromBothYears = new Set(
    [...nodesFromGraphPast].filter(label => nodesFromGraphFuture.has(label))
  )
  const nodesFromPastOnly = new Set(
    [...nodesFromGraphPast].filter(label => !nodesFromGraphFuture.has(label))
  )
  const nodesFromFutureOnly = new Set(
    [...nodesFromGraphFuture].filter(label => !nodesFromGraphPast.has(label))
  )

  console.log('Both years : %s nodes', [...nodesFromBothYears].length);
  console.log('2017 : %s nodes', [...nodesFrom2017Only].length);
  console.log('2022 : %s nodes', [...nodesFrom2022Only].length);
  // create new graph
  const resultGraph = new Graph();
  // store ids of nodes from past graph
  // store ids of nodes from future graph
  // store ids of nodes from future graph concerning the bridge
  // store 
}