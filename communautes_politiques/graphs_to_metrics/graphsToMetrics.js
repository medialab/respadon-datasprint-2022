const Graph = require('graphology');
const metrics = require('graphology-metrics')
const betweennessCentrality = require('graphology-metrics/centrality/betweenness');
const pagerankLib = require('graphology-metrics/centrality/pagerank');

const graphsToMetrics = (graphs) => {
  const labels = new Set();
  graphs.forEach(({graph}) => {
    graph.forEachNode((id, {label}) => {
      labels.add(label)
    })
  })
  const labelsMap = [...labels].reduce((res, label) => {
    return {
      ...res,
      [label]: graphs.reduce((res2, {year}) => {
        return {
          ...res2,
          [year]: {}
        }
      }, {})
    }
  }, {})
  graphs.forEach(({graph, year}) => {
    const centralities = betweennessCentrality(graph);
    const pageRanks = pagerankLib(graph);
    graph.forEachNode((id, {label}) => {
      const degree = graph.degree(id);
      const betweennessCentrality = centralities[id];
      const pageRank = pageRanks[id];
      labelsMap[label][year] = {
        degree,
        betweennessCentrality,
        pageRank
      }
    })
  })
  return Object.entries(labelsMap).reduce((res, [label, years]) => {
    return [
      ...res,
      ...Object.entries(years).reduce((res2, [year, metrics]) => {
        return [
          ...res2,
            {
            label,
            year,
            ...metrics
          }
        ];
      }, [])
    ]
  }, [])
}

module.exports = graphsToMetrics;