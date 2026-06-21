import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Activity, 
  Map, 
  History as HistoryIcon, 
  Bot,
  ShieldAlert
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Event Prediction', href: '/predict', icon: Activity },
  { name: 'Recommendations', href: '/recommendations', icon: Map },
  { name: 'Event History', href: '/history', icon: HistoryIcon },
  { name: 'AI Copilot', href: '/copilot', icon: Bot },
];

export function Sidebar() {
  return (
    <div className="flex h-full w-64 flex-col bg-slate-900 border-r border-slate-800 text-slate-300">
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-slate-800 bg-slate-950">
        <ShieldAlert className="h-8 w-8 text-indigo-500 mr-3" />
        <span className="text-xl font-bold text-white tracking-tight">ASTRA</span>
      </div>
      
      <div className="flex flex-1 flex-col overflow-y-auto pt-6 pb-4">
        <nav className="flex-1 space-y-1 px-4">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  isActive
                    ? 'bg-indigo-500/10 text-indigo-400 border-l-2 border-indigo-500'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-100 border-l-2 border-transparent',
                  'group flex items-center px-3 py-2.5 text-sm font-medium transition-all duration-200 ease-in-out rounded-r-lg'
                )
              }
            >
              <item.icon
                className="mr-3 h-5 w-5 flex-shrink-0"
                aria-hidden="true"
              />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}
