export interface Item { id: number; title: string }

export async function listItems(): Promise<Item[]> {
  const res = await fetch('/api/tasks');
  return res.json();
}
