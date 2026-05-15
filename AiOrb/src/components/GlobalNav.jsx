import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, ShieldAlert, Activity, Database,
  Brain, Settings, Zap, Home, ShoppingCart, Users, Mail, LogOut
} from 'lucide-react';

const navItems = [
  { category: 'Insights' },
  { path: '/dashboard/heatmaps',   label: 'User Friction',  icon: Activity },
  { path: '/dashboard/complexity', label: 'App Complexity', icon: Settings },
  { category: 'Enterprise' },
  { path: '/dashboard/b2b',        label: 'B2B Licensing',  icon: Brain },
  { path: '/dashboard/knowledge',  label: 'RAG Ingestion',  icon: Database },
];

function NavLink({ item }) {
  const location = useLocation();
  const active = item.path === '/dashboard'
    ? location.pathname === '/dashboard'
    : location.pathname.startsWith(item.path);
  const Icon = item.icon;

  if (item.category) {
    return <div className="mt-6 mb-2 px-6 text-[11px] font-semibold tracking-wider text-[#6b7a8a] uppercase">{item.category}</div>;
  }

  return (
    <Link
      to={item.path}
      className={`
        relative flex items-center gap-4 px-6 py-3 text-[14px] font-light transition-colors
        ${active
          ? 'text-white bg-[rgba(255,255,255,0.05)] border-l-2 border-[#f6a821]'
          : 'text-[#c9d5e0] hover:text-white hover:bg-[rgba(255,255,255,0.02)] border-l-2 border-transparent'
        }
      `}
    >
      <Icon className={`w-[18px] h-[18px] ${active ? 'text-[#f6a821]' : 'text-[#8fa5b8]'}`} />
      <span className={active ? 'font-medium' : ''}>{item.label}</span>
    </Link>
  );
}

export default function GlobalNav() {
  return (
    <aside className="w-[260px] h-full bg-[#202b38] flex flex-col border-r border-[#314256]">
      {/* Sidebar Header Logo */}
      <div className="h-20 flex items-center px-6 border-b border-[#314256]">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-[#314256] flex items-center justify-center">
             <Zap className="w-5 h-5 text-[#f6a821]" />
          </div>
          <span className="text-[18px] font-medium text-white tracking-wide">Light Blue</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 custom-scrollbar">
        {navItems.map((item, idx) => (
          <NavLink key={idx} item={item} />
        ))}
      </nav>

      {/* User / Logout */}
      <div className="p-6 border-t border-[#314256]">
        <Link to="/login" className="flex items-center gap-3 text-[#c9d5e0] hover:text-[#f6a821] trans">
          <LogOut className="w-5 h-5" />
          <span className="text-[14px]">Sign Out</span>
        </Link>
      </div>
    </aside>
  );
}
