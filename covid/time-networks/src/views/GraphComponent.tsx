import React, { FC, useEffect } from 'react';
import Graph from 'graphology';
import { FullScreenControl, SigmaContainer, useSigma, ZoomControl } from '@react-sigma/core';
import { ColorMode, COLORS_FIELD, COLORS_MAPPING } from '../consts';

const Lifecycle: FC<{
  colorsMode: ColorMode;
  onEnterNode: (node: string) => void;
  onLeaveNode: (node: string) => void;
  highlightedNode: string | null;
  highlightedValue: string | null;
}> = ({ onEnterNode, onLeaveNode, highlightedNode, highlightedValue, colorsMode }) => {
  const sigma = useSigma();

  useEffect(() => {
    const graph = sigma.getGraph();
    graph.on('nodeAttributesUpdated', () => {
      sigma.refresh();
    });
    sigma.on('enterNode', ({ node }) => onEnterNode(graph.getNodeAttribute(node, 'label')));
    sigma.on('leaveNode', ({ node }) => onLeaveNode(graph.getNodeAttribute(node, 'label')));
  }, []);

  useEffect(() => {
    const graph = sigma.getGraph();
    sigma.setSetting('nodeReducer', (node, data) => {
      const res = { ...data };

      if (colorsMode === 'lifecycle') {
        res.color =
          data.lifecycle === 'appears' ? 'green' : data.lifecycle === 'disappears' ? 'red' : 'grey';
      } else {
        res.color = COLORS_MAPPING[graph.getNodeAttribute(node, COLORS_FIELD)];
      }

      if (highlightedValue && colorsMode === 'types') {
        const hasValue = (graph.getNodeAttribute(node, COLORS_FIELD) || []).includes(
          highlightedValue
        );
        res.color = hasValue ? COLORS_MAPPING[highlightedValue] : '#ccc';
        if (!hasValue) res.label = null;
      }

      if (!highlightedNode) return res;
      if (res.label === highlightedNode)
        return {
          ...res,
          highlighted: true,
        };

      return {
        ...res,
        label: null,
        color: '#ccc',
      };
    });
    sigma.setSetting('edgeReducer', (edge, data) => {
      const res = { ...data, size: 2 };

      if (!highlightedNode) return res;

      const source = graph.source(edge);
      const target = graph.target(edge);
      if (
        graph.getNodeAttribute(source, 'label') !== highlightedNode &&
        graph.getNodeAttribute(target, 'label') !== highlightedNode
      )
        return {
          ...res,
          hidden: true,
        };

      return {
        ...res,
        size: 5,
      };
    });
  }, [highlightedNode, colorsMode, highlightedValue]);

  return null;
};

const GraphComponent: FC<{
  year: string;
  graph: Graph;
  colorsMode: ColorMode;
  onEnterNode: (node: string) => void;
  onLeaveNode: (node: string) => void;
  highlightedNode: string | null;
  highlightedValue: string | null;
}> = ({ year, graph, onEnterNode, onLeaveNode, highlightedNode, colorsMode, highlightedValue }) => {
  return (
    <SigmaContainer
      graph={graph}
      initialSettings={{ allowInvalidContainer: true, defaultEdgeType: 'arrow' }}
    >
      <div className="year">{year}</div>
      <Lifecycle
        colorsMode={colorsMode}
        onEnterNode={onEnterNode}
        onLeaveNode={onLeaveNode}
        highlightedNode={highlightedNode}
        highlightedValue={highlightedValue}
      />
      <div className="controls">
        <ZoomControl />
        <FullScreenControl />
      </div>
    </SigmaContainer>
  );
};

export default GraphComponent;
