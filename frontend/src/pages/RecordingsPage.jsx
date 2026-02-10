import { useState, useEffect } from 'react';
import { AgentService } from '../services/AgentService';
import {
    Mic,
    Loader2,
    Play,
    Pause,
    Clock,
    Download,
    Phone,
    Search,
    Filter
} from 'lucide-react';
import clsx from 'clsx';

export default function RecordingsPage() {
    const [recordings, setRecordings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [playing, setPlaying] = useState(null); // job_id
    const [audioRef, setAudioRef] = useState(null);
    const [filter, setFilter] = useState('');

    // Fetch data
    useEffect(() => {
        async function loadData() {
            setLoading(true);
            const data = await AgentService.fetchRecordings();
            setRecordings(data);
            setLoading(false);
        }
        loadData();
    }, []);

    // Audio Controls
    const togglePlay = (jobId, filename) => {
        if (playing === jobId) {
            audioRef.pause();
            setPlaying(null);
        } else {
            const url = `http://localhost:8000/api/recordings/${filename}`;
            const audio = new Audio(url);
            audio.play();
            setAudioRef(audio);
            setPlaying(jobId);

            audio.onended = () => {
                setPlaying(null);
                setAudioRef(null);
            };
        }
    };

    const filteredRecordings = recordings.filter(r =>
        r.job_id?.includes(filter) || r.timestamp?.includes(filter)
    );

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Call Recordings</h1>
                    <p className="text-slate-500 text-sm">Review audio from completed calls.</p>
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
                        placeholder="Search logs..."
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
                    Fetching recordings...
                </div>
            ) : filteredRecordings.length === 0 ? (
                <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
                    <Mic className="text-slate-300 mx-auto mb-4" size={48} />
                    <p className="text-slate-500">No recordings available yet.</p>
                </div>
            ) : (
                <div className="grid gap-4">
                    {filteredRecordings.map((rec) => (
                        <div key={rec.job_id} className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                {/* Play Button */}
                                <button
                                    onClick={() => togglePlay(rec.job_id, rec.filename)}
                                    className={`p-3 rounded-full transition-all duration-300 ${playing === rec.job_id
                                            ? 'bg-red-500 text-white shadow-lg shadow-red-500/40'
                                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                        }`}
                                >
                                    {playing === rec.job_id ? <Pause size={20} className="ml-0.5" /> : <Play size={20} className="ml-1" />}
                                </button>

                                {/* Info */}
                                <div>
                                    <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                                        Call Recording #{rec.job_id?.substring(0, 6)}
                                        <span className="text-xs font-normal text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                                            {rec.size_bytes ? `${(rec.size_bytes / 1024).toFixed(0)} KB` : "N/A"}
                                        </span>
                                    </h3>
                                    <div className="flex items-center gap-4 text-xs text-slate-400 mt-1">
                                        <span className="flex items-center gap-1"><Clock size={12} /> {rec.timestamp}</span>
                                        <span className="flex items-center gap-1"><Phone size={12} /> User Audio</span>
                                    </div>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex items-center gap-2">
                                <a
                                    href={`http://localhost:8000/api/recordings/${rec.filename}`}
                                    download
                                    className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors tooltip"
                                    title="Download Recording"
                                >
                                    <Download size={18} />
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
