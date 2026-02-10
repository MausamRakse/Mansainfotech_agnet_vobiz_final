import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api', // Should be dynamic in prod
    headers: {
        'Content-Type': 'application/json',
    }
});

export const AgentService = {
    // Single Call
    callSingle: async (phoneNumber) => {
        try {
            const res = await api.post('/call-single', { phone_number: phoneNumber });
            return res.data;
        } catch (err) {
            console.error("Call failed:", err);
            throw err;
        }
    },

    // Bulk Call
    uploadExcel: async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await api.post('/upload-excel', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            return res.data; // { phone_numbers: [...], total_count: N }
        } catch (err) {
            console.error("Upload failed:", err);
            throw err;
        }
    },

    startBulkCall: async (phoneNumbers) => {
        try {
            const res = await api.post('/bulk-call', { phone_numbers: phoneNumbers });
            return res.data;
        } catch (err) {
            console.error("Bulk start failed:", err);
            throw err;
        }
    },

    // Logs & Recordings
    fetchTranscripts: async () => {
        try {
            const res = await api.get('/transcripts');
            return res.data;
        } catch (err) {
            console.error("Fetch transcripts failed:", err);
            return [];
        }
    },

    fetchRecordings: async () => {
        try {
            const res = await api.get('/recordings');
            return res.data;
        } catch (err) {
            console.error("Fetch recordings failed:", err);
            return [];
        }
    }
};
