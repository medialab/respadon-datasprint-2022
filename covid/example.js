const fs = require('fs')
const Graph = require('graphology');
const gexf = require('graphology-gexf');
const mergeGraphs = require('../communautes_politiques/tenshin-han-viz/buildBridgingNetwork.js');
const layout = require('../communautes_politiques/tenshin-han-viz/buildTripartiteLayout.js');

const graph2017 = gexf.parse(Graph, fs.readFileSync('gexf/Covid_web_archive.gexf', 'utf8'));
const graph2022 = gexf.parse(Graph, fs.readFileSync('gexf/Covid_web_vivant.gexf', 'utf8'));

const mergedGraph = mergeGraphs(graph2017, graph2022);
// write graph
const gexfString1 = gexf.write(mergedGraph);
fs.writeFileSync('dist/mergedGraph.gexf', gexfString1, 'utf8')

const tripartiteGraph = layout(mergedGraph);
// write graph
const gexfString2 = gexf.write(tripartiteGraph);
fs.writeFileSync('dist/mergedGraphSpatialized.gexf', gexfString2, 'utf8')