import { useEffect, useState, Suspense } from "react";
import { useParams } from "react-router";
import GenericAddonPage from "./GenericAddonPage";

// Vite resolves this glob at build time — any .tsx in deployed/ is automatically included.
// After uploading an addon with a -front.tsx file, rebuild the frontend to activate it.
const addonModules = import.meta.glob("./deployed/*.tsx");

export default function AddonAgentPage() {
  const { agentKey } = useParams<{ agentKey: string }>();
  const [Component, setComponent] = useState<React.ComponentType | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (!agentKey) { setChecked(true); return; }
    const moduleKey = `./deployed/${agentKey}.tsx`;
    if (addonModules[moduleKey]) {
      addonModules[moduleKey]()
        .then((mod: any) => { setComponent(() => mod.default); setChecked(true); })
        .catch(() => setChecked(true));
    } else {
      setChecked(true);
    }
  }, [agentKey]);

  if (!checked) return null;

  if (Component) {
    return (
      <Suspense fallback={<div className="p-6 text-sm text-gray-400">Loading...</div>}>
        <Component />
      </Suspense>
    );
  }

  return <GenericAddonPage />;
}
