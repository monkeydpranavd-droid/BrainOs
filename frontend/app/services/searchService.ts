import { Entity, searchBrain } from '../mockData';

export async function querySearch(query: string): Promise<Entity[]> {
  // Leverage searchBrain in mockData
  return searchBrain(query);
}
