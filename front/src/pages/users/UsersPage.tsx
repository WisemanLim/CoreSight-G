import { useEffect, useState } from "react";
import { getUsers, createUser, deleteUser, User } from "../../api/users";
import { getAuth } from "../../store/auth";
import { useLocale } from "../../hooks/useLocale";

const ROLE_COLORS: Record<string, string> = {
  supervisor: "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400",
  admin:      "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400",
  user:       "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400",
  viewer:     "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400",
};

export default function UsersPage() {
  const { t } = useLocale();
  const me = getAuth();
  const isSupervisor = me?.role === "supervisor";

  const [users, setUsers] = useState<User[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ user_id: "", username: "", password: "", role: "user", email: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getUsers().then(setUsers).catch(console.error);
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await createUser(form);
      const updated = await getUsers();
      setUsers(updated);
      setShowForm(false);
      setForm({ user_id: "", username: "", password: "", role: "user", email: "" });
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(detail ?? t("users.createFailed"));
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(userId: string) {
    if (!confirm(`'${userId}' ${t("users.confirmDelete")}`)) return;
    try {
      await deleteUser(userId);
      setUsers((prev) => prev.filter((u) => u.user_id !== userId));
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      alert(detail ?? t("users.deleteFailed"));
    }
  }

  const FORM_FIELDS = [
    { key: "user_id",   label: t("users.userId"),       type: "text" },
    { key: "username",  label: t("users.username"),      type: "text" },
    { key: "password",  label: t("users.password"),      type: "password" },
    { key: "email",     label: t("users.emailOptional"), type: "text" },
  ];

  return (
    <div className="p-6 space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">{t("users.title")}</h1>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          {showForm ? t("common.cancel") : t("users.addUser")}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 space-y-4">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-200">{t("users.newUser")}</h2>
          {error && <p className="text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded px-3 py-2">{error}</p>}
          <div className="grid grid-cols-2 gap-4">
            {FORM_FIELDS.map(({ key, label, type }) => (
              <div key={key}>
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">{label}</label>
                <input
                  type={type}
                  value={form[key as keyof typeof form]}
                  onChange={(e) => setForm((p) => ({ ...p, [key]: e.target.value }))}
                  required={key !== "email"}
                  className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">{t("users.role")}</label>
            <select
              value={form.role}
              onChange={(e) => setForm((p) => ({ ...p, role: e.target.value }))}
              className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {(isSupervisor ? ["supervisor", "admin", "user", "viewer"] : ["admin", "user", "viewer"]).map(
                (r) => <option key={r} value={r}>{t(`users.roles.${r}`)}</option>
              )}
            </select>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
          >
            {loading ? t("common.creating") : t("common.create")}
          </button>
        </form>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-900 text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              <th className="text-left px-4 py-3">{t("users.userId")}</th>
              <th className="text-left px-4 py-3">{t("users.username")}</th>
              <th className="text-left px-4 py-3">{t("users.role")}</th>
              <th className="text-left px-4 py-3">{t("users.status")}</th>
              <th className="text-left px-4 py-3">{t("users.joinDate")}</th>
              {isSupervisor && <th className="px-4 py-3" />}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {users.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center text-gray-400 dark:text-gray-500 py-8">{t("users.noUsers")}</td>
              </tr>
            )}
            {users.map((u) => (
              <tr key={u.user_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td className="px-4 py-3 font-medium text-gray-800 dark:text-gray-200">{u.user_id}</td>
                <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{u.username}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ROLE_COLORS[u.role] ?? "bg-gray-100 dark:bg-gray-700 text-gray-500"}`}>
                    {t(`users.roles.${u.role}`) ?? u.role}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    u.status === "active"
                      ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500"
                  }`}>
                    {u.status === "active" ? t("common.active") : t("common.inactive")}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-400 dark:text-gray-500 text-xs">
                  {u.created_at ? new Date(u.created_at).toLocaleDateString() : "-"}
                </td>
                {isSupervisor && (
                  <td className="px-4 py-3 text-right">
                    {u.user_id !== me?.username && u.role !== "supervisor" && (
                      <button
                        onClick={() => handleDelete(u.user_id)}
                        className="text-xs text-red-400 hover:text-red-600 dark:hover:text-red-300 transition-colors"
                      >
                        {t("common.delete")}
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
