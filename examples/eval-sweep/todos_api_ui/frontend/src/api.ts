export interface Item { id: number; title: string }

export async function listItems(): Promise<Item[]> {
  const res = await fetch('/api/todos');
  return res.json();
}
