import { useState, useEffect } from 'react';
import { AgentService } from '../services/AgentService';
import {
    PhoneCall,
    UploadCloud,
    Loader2,
    CheckCircle,
    AlertCircle
} from 'lucide-react';
import clsx from 'clsx';

export default function ConsolePage() {
    const [singlePhone, setSinglePhone] = useState('');
    const [callStatus, setCallStatus] = useState(null); // { loading, success, error, data }

    const [bulkFile, setBulkFile] = useState(null);
    const [bulkNumbers, setBulkNumbers] = useState([]);
    const [bulkStatus, setBulkStatus] = useState(null); // { loading, success, error, count }

    // --- Single Call ---
    const handleSingleCall = async () => {
        if (!singlePhone) return;

        setCallStatus({ loading: true });
        try {
            const res = await AgentService.callSingle(singlePhone);
            setCallStatus({ loading: false, success: true, data: res });
        } catch (err) {
            setCallStatus({ loading: false, error: err.message || "Failed to initiate call" });
        }
    };

    // --- Bulk Call ---
    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setBulkFile(file);
        setBulkStatus({ loading: true, message: "Parsing file..." });

        try {
            const res = await AgentService.uploadExcel(file);
            setBulkNumbers(res.phone_numbers || []);
            setBulkStatus({ loading: false, success: true, count: res.total_count });
        } catch (err) {
            setBulkStatus({ loading: false, error: "Failed to parse file. Ensure it has a phone column." });
            setBulkFile(null);
        }
    };

    const handleStartBulk = async () => {
        if (bulkNumbers.length === 0) return;

        setBulkStatus({ ...bulkStatus, loading: true, message: `Dialing ${bulkNumbers.length} numbers...` });

        try {
            const res = await AgentService.startBulkCall(bulkNumbers);
            setBulkStatus({
                loading: false,
                success: true,
                message: `Successfully dispatched ${res.total_processed} calls!`
            });
            setBulkNumbers([]); // Reset
            setBulkFile(null);
        } catch (err) {
            setBulkStatus({ loading: false, error: "Bulk dispatch failed." });
        }
    };

    return (
        <div className="space-y-8">
            <header>
                <h1 className="text-3xl font-bold text-slate-900">Agent Console</h1>
                <p className="text-slate-500 mt-1">Manage outbound campaigns and monitor agent performance.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Single Call Card */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col h-full">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
                            <PhoneCall size={24} />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-slate-900">Single Call</h2>
                            <p className="text-sm text-slate-500">Test the agent with a direct call</p>
                        </div>
                    </div>

                    <div className="space-y-4 flex-1">
                        <label className="block text-sm font-medium text-slate-700">
                            Phone Number (with Country Code)
                        </label>
                        <input
                            type="text"
                            placeholder="+919999999999"
                            value={singlePhone}
                            onChange={(e) => setSinglePhone(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                        />

                        {callStatus?.error && (
                            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-center gap-2">
                                <AlertCircle size={16} /> {callStatus.error}
                            </div>
                        )}

                        {callStatus?.success && (
                            <div className="p-3 bg-green-50 text-green-700 text-sm rounded-lg flex items-center gap-2">
                                <CheckCircle size={16} />
                                Call dispatched! Room: {callStatus.data.room_name}
                            </div>
                        )}
                    </div>

                    <button
                        onClick={handleSingleCall}
                        disabled={callStatus?.loading || !singlePhone}
                        className="mt-6 w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 transition-all"
                    >
                        {callStatus?.loading ? <Loader2 className="animate-spin" size={20} /> : "Call Now"}
                    </button>
                </div>

                {/* Bulk Upload Card */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col h-full">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-3 bg-emerald-100 text-emerald-600 rounded-lg">
                            <UploadCloud size={24} />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-slate-900">Bulk Campaign</h2>
                            <p className="text-sm text-slate-500">Upload Excel/CSV to dial multiple leads</p>
                        </div>
                    </div>

                    <div className="space-y-6 flex-1">
                        <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 hover:bg-slate-50 transition-colors text-center cursor-pointer relative">
                            <input
                                type="file"
                                accept=".csv, .xlsx"
                                onChange={handleFileChange}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            />
                            <div className="flex flex-col items-center">
                                <UploadCloud className="text-slate-400 mb-3" size={40} />
                                <span className="text-slate-600 font-medium">
                                    {bulkFile ? bulkFile.name : "Click to upload Excel/CSV"}
                                </span>
                                <span className="text-slate-400 text-sm mt-1">
                                    {bulkFile ? `${(bulkFile.size / 1024).toFixed(1)} KB` : "Drag and drop or browse"}
                                </span>
                            </div>
                        </div>

                        {bulkStatus?.loading && (
                            <div className="text-center text-slate-500 text-sm flex justify-center gap-2">
                                <Loader2 className="animate-spin" size={16} /> {bulkStatus.message || "Processing..."}
                            </div>
                        )}

                        {bulkStatus?.error && (
                            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-center gap-2">
                                <AlertCircle size={16} /> {bulkStatus.error}
                            </div>
                        )}

                        {bulkNumbers.length > 0 && (
                            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-semibold text-slate-700">Preview Numbers</span>
                                    <span className="text-xs bg-slate-200 px-2 py-1 rounded text-slate-600">
                                        Total: {bulkNumbers.length}
                                    </span>
                                </div>
                                <div className="max-h-32 overflow-y-auto space-y-1 pr-1">
                                    {bulkNumbers.slice(0, 10).map((num, i) => (
                                        <div key={i} className="text-sm text-slate-600 bg-white px-2 py-1 rounded border border-slate-100">
                                            {num}
                                        </div>
                                    ))}
                                    {bulkNumbers.length > 10 && (
                                        <div className="text-xs text-slate-400 text-center italic">
                                            +{bulkNumbers.length - 10} more...
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    <button
                        onClick={handleStartBulk}
                        disabled={bulkStatus?.loading || bulkNumbers.length === 0}
                        className="mt-6 w-full py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 transition-all"
                    >
                        {bulkStatus?.loading ? <Loader2 className="animate-spin" size={20} /> : "Start Campaign"}
                    </button>
                </div>
            </div>

        </div>
    );
}
