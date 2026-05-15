import { NavLink, Outlet, useNavigate } from "react-router";
import { useEffect } from "react";
import { LogOut } from "lucide-react";

const navItems = [
  { path: '/', label: 'Inicio' },
  { path: '/stock', label: 'Stock' },
  { path: '/clientes', label: 'Clientes' },
  { path: '/ventas', label: 'Ventas' },
  { path: '/cobros', label: 'Cobros' },
  { path: '/cheques', label: 'Cheques' },
];

export default function Layout() {
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="overflow-x-auto">
          <div className="flex items-center gap-1 px-4 min-w-max">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `px-4 py-4 text-sm font-medium transition-colors whitespace-nowrap ${
                    isActive
                      ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]'
                      : 'text-gray-600 hover:text-gray-900 border-b-2 border-transparent'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
            <button
              onClick={handleLogout}
              className="ml-auto px-4 py-4 text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors flex items-center gap-1"
            >
              <LogOut className="w-4 h-4" />
              Salir
            </button>
          </div>
        </div>
      </nav>
      <main className="p-4 md:p-6 lg:p-8">
        <Outlet />
      </main>
    </div>
  );
}
