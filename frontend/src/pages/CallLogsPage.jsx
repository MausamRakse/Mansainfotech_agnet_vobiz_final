import { useState, useEffect } from 'react';
import { AgentService } from '../services/AgentService';
import {
    FileText,
    Loader2,
    Clock,
    Phone,
    Search,
    Filter
} from 'lucide-react';

export default function CallLogsPage() {
    const [transcripts, setTranscripts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');

    useEffect(() => {
        async function loadData() {
            setLoading(true);
            const data = await AgentService.fetchTranscripts();
            setTranscripts(data);
            setLoading(false);
        }
        loadData();
    }, []);

    const filteredTranscripts = transcripts.filter(t =>
        t.phone_number?.includes(filter) || t.job_id?.includes(filter)
    );

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Call Transcripts</h1>
                    <p className="text-slate-500 text-sm">Review conversations and agent performance.</p>
                </div>
                <button
                    onClick={() => window.location.reload()}
                    className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                >
                    <Loader2 size={14} className={loading && "animate-spin"} /> Refresh
                </button>
            </header>

            {/* Filters */}
            <div className="flex gap-4 mb-6">
                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                        type="text"
                        placeholder="Search by phone or Job ID..."
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                    />
                </div>
                <button className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500">
                    <Filter size={18} />
                </button>
            </div>

            {loading ? (
                <div className="text-center py-20 text-slate-400">
                    <Loader2 className="animate-spin mx-auto mb-2" size={32} />
                    Loading logs...
                </div>
            ) : filteredTranscripts.length === 0 ? (
                <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
                    <FileText className="text-slate-300 mx-auto mb-4" size={48} />
                    <p className="text-slate-500">No transcripts found.</p>
                </div>
            ) : (
                <div className="grid gap-4">
                    {filteredTranscripts.map((t) => (
                        <div key={t.job_id} className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="font-semibold text-slate-900 flex items-center gap-1">
                                            <Phone size={14} className="text-emerald-500" /> {t.phone_number || "Unknown"}
                                        </span>
                                        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 text-xs font-mono">
                                            ID: {t.job_id?.substring(0, 8)}...
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-4 text-xs text-slate-400">
                                        <span className="flex items-center gap-1"><Clock size={12} /> {t.timestamp || "Just now"}</span>
                                        <span>{t.messages?.length || 0} messages</span>
                                    </div>
                                </div>

                                {/* Status Badge (Mock) */}
                                <span className={`px-2 py-1 rounded text-xs font-medium ${t.messages?.length > 5 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                                    }`}>
                                    {t.messages?.length > 5 ? 'Completed' : 'Short Call'}
                                </span>
                            </div>

                            {/* Transcript Preview */}
                            <div className="bg-slate-50 rounded-lg p-3 text-sm space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                                {t.messages?.map((msg, idx) => (
                                    <div key={idx} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[85%] px-3 py-2 rounded-lg text-xs leading-relaxed ${msg.role === 'user'
                                                ? 'bg-blue-100 text-blue-900 rounded-tr-none'
                                                : 'bg-white border border-slate-200 text-slate-700 rounded-tl-none'
                                            }`}>
                                            <span className="block font-bold mb-0.5 text-[10px] opacity-70 uppercase tracking-wide">
                                                {msg.display_role}
                                            </span>
                                            {msg.content}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
