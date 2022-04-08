const fs = require('fs')
const Graph = require('graphology');
const gexf = require('graphology-gexf');
const graphsToMetrics = require('./graphsToMetrics.js');

const graph2012 = gexf.parse(Graph, fs.readFileSync('../data/melenchon_2012.gexf', 'utf8'));
const graph2017 = gexf.parse(Graph, fs.readFileSync('../data/melenchon_2017.gexf', 'utf8'));
const graph2022 = gexf.parse(Graph, fs.readFileSync('../data/melenchon_2022.gexf', 'utf8'));

const buildNodesAttributesMap = arr => {
  return arr.reduce((res, item) => {
    return {
      ...res,
      [item.NAME]: {
        forme_editoriale: item['forme éditoriale (TAGS)'],
        acteur: item['acteur (TAGS)']
      }
    }
  }, {})
}

import('d3-dsv')
.then(({csvFormat, csvParse}) => {

const metrics = graphsToMetrics([
  {
    year: 2012,
    graph: graph2012,
    nodesAttributesMap: buildNodesAttributesMap(csvParse(fs.readFileSync('../data/melenchon_2012.csv', 'utf8')))
  },
  {
    year: 2017,
    graph: graph2017,
    nodesAttributesMap: buildNodesAttributesMap(csvParse(fs.readFileSync('../data/melenchon_2017.csv', 'utf8')))
  },
  {
    year: 2022,
    graph: graph2022,
    nodesAttributesMap: buildNodesAttributesMap(csvParse(fs.readFileSync('../data/melenchon_2022.csv', 'utf8')))
  },
]);

  fs.writeFileSync('../data/metrics.csv', csvFormat(metrics), 'utf8')
})
