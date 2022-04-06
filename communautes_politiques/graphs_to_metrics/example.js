const fs = require('fs')
const Graph = require('graphology');
const gexf = require('graphology-gexf');
const graphsToMetrics = require('./graphsToMetrics.js');

const graph2017 = gexf.parse(Graph, fs.readFileSync('melenchon_2017.gexf', 'utf8'));
const graph2022 = gexf.parse(Graph, fs.readFileSync('melenchon_2022.gexf', 'utf8'));

const metrics = graphsToMetrics([
  {
    year: 2017,
    graph: graph2017
  },
  {
    year: 2022,
    graph: graph2022
  },
]);

import('d3-dsv')
.then(({csvFormat}) => {
  fs.writeFileSync('metrics.csv', csvFormat(metrics), 'utf8')
})
