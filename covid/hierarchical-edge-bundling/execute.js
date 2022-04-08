const fs = require ('fs');

const Graph = require('graphology')
    , gexf = require('graphology-gexf')
    , louvain = require('graphology-communities-louvain');

[
    'covid_2020.gexf',
    'covid_2021.gexf',
    'covid_2022.gexf'
].forEach(file => {
    const graph = gexf.parse(
        Graph,
        fs.readFileSync('../gexf/' + file, 'utf-8')
    );
    
    const toExport = [];
    
    louvain.assign(graph);
    
    graph.forEachNode((nodeId, { label, color, community, pages_total, ...attrs }) => {
        if (graph.neighbors(nodeId).length !== 0) {
            toExport.push({
                name: `${community}.${nodeId}`,
                label,
                color,
                pages_total,
                imports: [
                    ...graph.neighbors(nodeId).map(nodeId => `${graph.getNodeAttribute(nodeId, 'community')}.${nodeId}`)
                ]
            })
        }
    })
    
    fs.writeFile(`data-${file}.json`, JSON.stringify(toExport, undefined, 4), 'utf-8', (err) => {
        if (err) {
            return console.error(err);
        }
    });
})
