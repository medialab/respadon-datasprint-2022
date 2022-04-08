const fs = require('fs')
const Graph = require('graphology');
const gexf = require('graphology-gexf');
const mergeGraphs = require('./buildBridgingNetwork.js');
const layout = require('./buildTripartiteLayout.js');

const graph2012 = gexf.parse(Graph, fs.readFileSync('../data/melenchon_2012.gexf', 'utf8'));
const graph2017 = gexf.parse(Graph, fs.readFileSync('../data/melenchon_2017.gexf', 'utf8'));
const graph2022 = gexf.parse(Graph, fs.readFileSync('../data/melenchon_2022.gexf', 'utf8'));

fs.writeFileSync('../data/triptyque_2012_to_2017.gexf', gexf.write(layout(mergeGraphs(graph2012, graph2017))), 'utf8')
fs.writeFileSync('../data/triptyque_2017_to_2022.gexf', gexf.write(layout(mergeGraphs(graph2017, graph2022))), 'utf8')
