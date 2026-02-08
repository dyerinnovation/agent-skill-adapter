import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/skills", label: "Skills" },
  { to: "/training", label: "Training" },
  { to: "/evaluation", label: "Evaluation" },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-56 bg-blue-700 text-white flex flex-col">
        <div className="px-6 py-5 text-xl font-bold border-b border-blue-600">
          Skill Adapter
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === "/"}
              className={({ isActive }) =>
                `block px-3 py-2 rounded text-sm font-medium ${
                  isActive ? "bg-blue-800 text-white" : "text-blue-100 hover:bg-blue-600"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
