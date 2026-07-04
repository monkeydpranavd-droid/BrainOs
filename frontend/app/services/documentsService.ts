import { Entity, entities } from '../mockData';

export async function getDocuments(): Promise<Entity[]> {
  // Returns all document type entities from the mock DB
  return entities.filter(e => e.type === 'document');
}
