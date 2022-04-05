# Ten Shin Han viz (three eyes viz !!)

This little script merges two graphs from different periods of time and creates a unified graph merging them into one single graph with three types of nodes: "past" only, "bridge" (nodes which are in two graphs), "future" only.

Nodes get a property "period_type" with enum{3}: `["past", "future", "bridge"]`

Edges get a property "period_type" with enum{5}: `["past", "future", "bridge", "past_bridge", "future_bridge"]`

It returns a `graphology` graph to be used for visualizing  the transition between two graphs.

# Installation

```
npm install
```

# Example usage

See `example.js`. Or do something like this:

```js
const fs = require('fs')
const gexf = require('graphology-gexf');
const mergeGraphs = require('./buildBridgingNetwork.js');

const graphFrom20x1 = gexf.parse(Graph, fs.readFileSync('my_graph_from_20x1.gexf', 'utf8'));
const graphFrom20x2 = gexf.parse(Graph, fs.readFileSync('my_graph_from_20x2.gexf', 'utf8'));

const mergedGraph = mergeGraphs(graphFrom20x1, graphFrom20x2);
// write graph
const gexfString = gexf.write(mergedGraph);
fs.writeFileSync('mergedGraph.gexf', gexfString, 'utf8')
```

