const fs = require('fs')
const Graph = require('graphology');
const gexf = require('graphology-gexf');
const mergeGraphs = require('./buildBridgingNetwork.js');
const layout = require('./buildTripartiteLayout.js');

const graph2017 = gexf.parse(Graph, fs.readFileSync('../data/melenchon_2017.gexf', 'utf8'));
const graph2022 = gexf.parse(Graph, fs.readFileSync('../data/melenchon_2022.gexf', 'utf8'));

const mergedGraph = mergeGraphs(graph2017, graph2022);
// write graph
const gexfString1 = gexf.write(mergedGraph);
fs.writeFileSync('../data/mergedGraph.gexf', gexfString1, 'utf8')

const tripartiteGraph = layout(mergedGraph);

// write graph
const gexfString2 = gexf.write(tripartiteGraph);
fs.writeFileSync('../data/mergedGraphSpatialized.gexf', gexfString2, 'utf8')
