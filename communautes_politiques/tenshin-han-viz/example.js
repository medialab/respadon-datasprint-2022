const fs = require('fs')
const Graph = require('graphology');
const gexf = require('graphology-gexf');
const mergeGraphs = require('./buildBridgingNetwork.js');

const graph2017 = gexf.parse(Graph, fs.readFileSync('melenchon_2017.gexf', 'utf8'));
const graph2022 = gexf.parse(Graph, fs.readFileSync('melenchon_2022.gexf', 'utf8'));

const mergedGraph = mergeGraphs(graph2017, graph2022);
// write graph
const gexfString = gexf.write(mergedGraph);
fs.writeFileSync('mergedGraph.gexf', gexfString, 'utf8')