import React from 'react';
import { createRoot } from 'react-dom/client';

import './index.css';
import App from './views/App';
import getFullGraph from './utils/getFullGraph';
import { LAYERS } from './consts';
import getProjectedGraph from './utils/getProjectedGraph';

getFullGraph().then((fullGraph) => {
  const projections = LAYERS.map(({ year }) => ({
    year,
    graph: getProjectedGraph(fullGraph, year),
  }));

  const root = createRoot(document.getElementById('root') as HTMLDivElement);
  root.render(
    <React.StrictMode>
      <App fullGraph={fullGraph} projections={projections} />
    </React.StrictMode>
  );
});
