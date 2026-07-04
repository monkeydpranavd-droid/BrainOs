import { Entity, Relationship, entities, relationships } from '../mockData';

export interface GraphData {
  nodes: Entity[];
  edges: Relationship[];
}

export async function getGraphData(): Promise<GraphData> {
  return {
    nodes: entities,
    edges: relationships
  };
}
