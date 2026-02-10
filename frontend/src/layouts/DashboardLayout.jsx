import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
    Bot,
    PhoneOutgoing,
    FileText,
    Mic,
    LayoutDashboard,
    PanelLeftClose,
    PanelLeftOpen,
    LogOut
} from 'lucide-react';
import clsx from 'clsx';

export default function DashboardLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();

    const navItems = [
        { name: 'Dashboard', path: '/console', icon: <LayoutDashboard size={20} /> },
        { name: 'Transcripts', path: '/console/transcripts', icon: <FileText size={20} /> },
        { name: 'Recordings', path: '/console/recordings', icon: <Mic size={20} /> },
    ];

    return (
        <div className="flex h-screen bg-slate-100 overflow-hidden font-sans">
            {/* Sidebar */}
            <aside
                className={clsx(
                    "bg-slate-900 text-slate-300 transition-all duration-300 ease-in-out flex flex-col fixed inset-y-0 left-0 z-20 md:relative",
                    sidebarOpen ? "w-64" : "w-20"
                )}
            >
                {/* Header */}
                <div className="h-16 flex items-center px-6 border-b border-slate-800">
                    <Bot className="text-brand-500 shrink-0" size={28} />
                    {sidebarOpen && (
                        <span className="ml-3 font-bold text-lg text-white tracking-wide truncate">
                            Mansa Console
                        </span>
                    )}
                </div>

                {/* Nav Items */}
                <nav className="flex-1 py-6 space-y-2 px-3">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <button
                                key={item.path}
                                onClick={() => navigate(item.path)}
                                className={clsx(
                                    "w-full flex items-center px-3 py-3 rounded-lg transition-colors group relative",
                                    isActive
                                        ? "bg-brand-600 text-white shadow-lg shadow-brand-900/20"
                                        : "hover:bg-slate-800 hover:text-white"
                                )}
                            >
                                <span className={clsx("shrink-0", isActive && "animate-pulse")}>
                                    {item.icon}
                                </span>

                                {sidebarOpen && (
                                    <span className="ml-3 font-medium text-sm">
                                        {item.name}
                                    </span>
                                )}

                                {!sidebarOpen && (
                                    <div className="absolute left-14 bg-slate-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                                        {item.name}
                                    </div>
                                )}
                            </button>
                        );
                    })}
                </nav>

                {/* Footer Actions */}
                <div className="p-4 border-t border-slate-800">
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="w-full flex items-center justify-center p-2 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                    >
                        {sidebarOpen ? <PanelLeftClose size={20} /> : <PanelLeftOpen size={20} />}
                    </button>
                    <button
                        onClick={() => navigate('/')}
                        className="mt-2 w-full flex items-center justify-center p-2 rounded hover:bg-slate-800 text-slate-400 hover:text-red-400 transition-colors"
                        title="Exit Console"
                    >
                        <LogOut size={20} />
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">

                {/* Content Area */}
                <div className="flex-1 overflow-y-auto p-4 md:p-8">
                    <Outlet />
                </div>

            </main>
        </div>
    );
}
