/**
 * Skeleton Agent — 최소 프론트엔드 컴포넌트. [CUSTOMIZE] 도메인 UI 로 교체하세요.
 * 마운트: /addon/skeleton (동적 로드)
 */
import { useEffect, useState } from "react";
import axios from "axios";

interface Item {
  id: number;
  name: string;
  note: string;
  created_at: string;
}

export default function SkeletonPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [name, setName] = useState("");

  const load = async () => {
    const res = await axios.get("/api/addon/skeleton/items");
    setItems(res.data.items ?? []);
  };

  useEffect(() => {
    load();
  }, []);

  const add = async () => {
    if (!name.trim()) return;
    await axios.post("/api/addon/skeleton/items", { name });
    setName("");
    load();
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-xl font-bold mb-4 dark:text-white">Skeleton Agent</h1>
      <div className="flex gap-2 mb-4">
        <input
          className="flex-1 border rounded px-3 py-2 dark:bg-gray-800 dark:text-white"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="항목 이름"
        />
        <button className="px-4 py-2 rounded bg-blue-600 text-white" onClick={add}>
          추가
        </button>
      </div>
      <ul className="space-y-2">
        {items.map((it) => (
          <li key={it.id} className="border rounded px-3 py-2 dark:text-gray-200">
            {it.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
