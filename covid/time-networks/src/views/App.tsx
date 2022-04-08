import React, { FC, useState } from 'react';
import Graph from 'graphology';
import { map } from 'lodash';

import './App.css';

import GraphComponent from './GraphComponent';
import { COLOR_MODES, ColorMode, COLORS_MAPPING, LIFECYCLE_COLORS_MAPPING } from '../consts';

const App: FC<{
  fullGraph: Graph;
  projections: { graph: Graph; year: string }[];
}> = ({ projections }) => {
  const [highlightedNode, setHighlightedNode] = useState<string | null>(null);
  const [highlightedValue, setHighlightedValue] = useState<string | null>(null);
  const [colorsMode, setColorsMode] = useState<ColorMode>('types');

  return (
    <div className="app">
      <div className="buttons">
        <div>
          {COLOR_MODES.map(({ id, label }) => (
            <span key={id} className="input-wrapper">
              <input
                id={`checkbox-colors-${id}`}
                type="radio"
                checked={id === colorsMode}
                onChange={(e) => {
                  if (e.target.checked) setColorsMode(id);
                }}
              />
              <label htmlFor={`checkbox-colors-${id}`}>{label}</label>
            </span>
          ))}
        </div>
        <div>
          {map(
            colorsMode === 'lifecycle' ? LIFECYCLE_COLORS_MAPPING : COLORS_MAPPING,
            (color, key) => (
              <span
                key={key}
                className="caption-wrapper"
                onMouseEnter={() => setHighlightedValue(key)}
                onMouseLeave={() => setHighlightedValue(null)}
              >
                <span className="color" style={{ background: color }} />{' '}
                <span className="color-label">{key}</span>
              </span>
            )
          )}
        </div>
      </div>
      <div className="graphs">
        {projections.map(({ year, graph }) => (
          <GraphComponent
            key={year}
            year={year}
            graph={graph}
            colorsMode={colorsMode}
            highlightedNode={highlightedNode}
            highlightedValue={highlightedValue}
            onEnterNode={(url) => setHighlightedNode(url)}
            onLeaveNode={() => setHighlightedNode(null)}
          />
        ))}
      </div>
    </div>
  );
};

export default App;
