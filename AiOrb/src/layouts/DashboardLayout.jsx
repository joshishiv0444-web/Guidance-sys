import { Outlet } from 'react-router-dom';
import GlobalNav from '../components/GlobalNav';
import { Search, Bell, Settings } from 'lucide-react';

export default function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-[#253342]">
      {/* Sidebar Area */}
      <GlobalNav />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        
        {/* Top Header */}
        <header className="h-20 flex-shrink-0 flex items-center justify-between px-8 bg-[#253342]">
          <div className="flex-1 flex items-center">
             <div className="relative w-full max-w-md">
               <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                 <Search className="h-5 w-5 text-[#6b7a8a]" />
               </div>
               <input 
                 type="text" 
                 placeholder="Search Dashboard" 
                 className="w-full bg-[#1e2835] border border-transparent rounded pl-10 pr-4 py-2.5 text-[14px] text-white placeholder-[#6b7a8a] focus:outline-none focus:border-[#314256] focus:bg-[#1c2631] trans"
               />
             </div>
          </div>

          <div className="flex flex-shrink-0 items-center gap-6">
            <div className="flex items-center gap-4 text-[#8fa5b8]">
               <button className="hover:text-white trans relative">
                 <Bell className="w-5 h-5" />
                 <span className="absolute top-0 right-0 w-2 h-2 bg-[#f6a821] rounded-full" />
               </button>
               <button className="hover:text-white trans">
                 <Settings className="w-5 h-5" />
               </button>
            </div>
            
            <div className="flex items-center gap-3 pl-6 border-l border-[#314256]">
               <div className="flex flex-col items-end">
                 <span className="text-[13px] font-medium text-white">admin@aiorb.com</span>
                 <span className="text-[11px] text-[#8fa5b8]">Administrator</span>
               </div>
               <div className="w-9 h-9 rounded bg-[#314256] flex items-center justify-center text-white text-[12px] font-semibold">
                 AD
               </div>
            </div>
          </div>
        </header>

        {/* Scrollable Main Content */}
        <main className="flex-1 overflow-auto p-8">
          <div className="max-w-[1400px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
