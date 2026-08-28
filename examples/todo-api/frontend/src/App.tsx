import { useEffect, useState } from 'react';
import { Item, listItems } from './api';

export default function App() {
  const [items, setItems] = useState<Item[]>([]);
  useEffect(() => { listItems().then(setItems); }, []);
  return <ul>{items.map(i => <li key={i.id}>{i.title}</li>)}</ul>;
}