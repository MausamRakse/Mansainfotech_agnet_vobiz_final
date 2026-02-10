import { useNavigate } from 'react-router-dom';
import {
    Bot,
    PhoneOutgoing,
    Activity,
    FileText,
    ArrowRight,
    ShieldCheck,
    Zap,
    Globe
} from 'lucide-react';

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col">
            {/* Navbar */}
            <nav className="border-b bg-white/50 backdrop-blur-sm fixed w-full z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-2">
                            <div className="bg-brand-600 p-2 rounded-lg text-white">
                                <Bot size={24} />
                            </div>
                            <span className="text-xl font-bold bg-gradient-to-r from-brand-700 to-brand-500 bg-clip-text text-transparent">
                                Mansa AI
                            </span>
                        </div>

                        <button
                            onClick={() => navigate('/console')}
                            className="px-5 py-2 rounded-full bg-slate-900 text-white font-medium text-sm hover:bg-slate-800 transition-all flex items-center gap-2"
                        >
                            Open Console <ArrowRight size={16} />
                        </button>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="flex-grow pt-32 pb-16 px-4">
                <div className="max-w-5xl mx-auto text-center space-y-8">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 text-brand-700 text-sm font-semibold border border-brand-100 mb-4">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
                        </span>
                        Now Live: Outbound Agent V1
                    </div>

                    <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 leading-tight">
                        Intelligent Outbound <br />
                        <span className="text-brand-600">AI Calling Agent</span>
                    </h1>

                    <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
                        Deploy autonomous voice agents that can handle lead qualification, appointment booking, and customer support with human-like fluency.
                    </p>

                    <div className="flex justify-center gap-4 pt-4">
                        <button
                            onClick={() => navigate('/console')}
                            className="px-8 py-4 rounded-xl bg-brand-600 text-white font-semibold text-lg hover:bg-brand-700 shadow-lg shadow-brand-500/30 transition-all hover:scale-105"
                        >
                            Launch Console
                        </button>
                        <button className="px-8 py-4 rounded-xl bg-white border border-slate-200 text-slate-700 font-semibold text-lg hover:bg-slate-50 shadow-sm transition-all">
                            View Documentation
                        </button>
                    </div>
                </div>

                {/* Features Grid */}
                <div className="max-w-6xl mx-auto mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
                    <FeatureCard
                        icon={<PhoneOutgoing className="text-blue-600" size={32} />}
                        title="Bulk & Single Calling"
                        desc="Upload Excel sheets for high-volume campaigns or dial single numbers instantly for testing."
                    />
                    <FeatureCard
                        icon={<FileText className="text-emerald-600" size={32} />}
                        title="Smart Transcripts"
                        desc="Automatically generated transcripts stored in JSON format for easy analysis and integration."
                    />
                    <FeatureCard
                        icon={<Activity className="text-violet-600" size={32} />}
                        title="Real-time Monitoring"
                        desc="Watch live agent status, call duration, and connection health from a central dashboard."
                    />
                </div>
            </main>

            {/* Footer */}
            <footer className="border-t bg-white py-12">
                <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-slate-500 text-sm">
                    <p>© 2024 Mansa Infotech. All rights reserved.</p>
                    <div className="flex gap-6 mt-4 md:mt-0">
                        <span className="flex items-center gap-1"><ShieldCheck size={14} /> Enterprise Grade</span>
                        <span className="flex items-center gap-1"><Zap size={14} /> Low Latency</span>
                        <span className="flex items-center gap-1"><Globe size={14} /> Global Reach</span>
                    </div>
                </div>
            </footer>
        </div>
    );
}

function FeatureCard({ icon, title, desc }) {
    return (
        <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-xl shadow-slate-200/40 hover:shadow-2xl hover:shadow-slate-200/60 transition-all group">
            <div className="mb-6 p-3 bg-slate-50 rounded-xl inline-block group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">{title}</h3>
            <p className="text-slate-600 leading-relaxed">
                {desc}
            </p>
        </div>
    )
}
