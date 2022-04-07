const fs = require ('fs');

const Graph = require('graphology')
    , gexf = require('graphology-gexf')
    , louvain = require('graphology-communities-louvain');

const graph = gexf.parse(
    Graph,
    fs.readFileSync('../gexf/Covid_web_archive.gexf', 'utf-8')
);

const toExport = [];

louvain.assign(graph);

graph.forEachNode((nodeId, { label, color, community, ...attrs }) => {
    toExport.push({
        name: `${community}.${nodeId}`,
        label: label,
        color: color,
        imports: [
            ...graph.neighbors(nodeId).map(nodeId => `${graph.getNodeAttribute(nodeId, 'community')}.${nodeId}`)
        ]
    })
})

fs.writeFile('data.json', JSON.stringify(toExport, undefined, 4), 'utf-8', (err) => {
    if (err) {
        return console.error(err);
    }
});