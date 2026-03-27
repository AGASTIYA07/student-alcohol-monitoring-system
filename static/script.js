const form = document.getElementById('submission-form');
let historyChart = null;

// Sensor reading logic
const readSensorBtn = document.getElementById('read-sensor-btn');
if (readSensorBtn) {
    readSensorBtn.addEventListener('click', async () => {
        readSensorBtn.disabled = true;
        readSensorBtn.innerText = "⏳ Reading...";
        
        try {
            const res = await fetch('/api/read_sensor');
            const data = await res.json();
            
            if(data.success) {
                document.getElementById('alcohol_level').value = data.level;
                if(data.mocked) {
                    console.info("Notice: " + data.message);
                }
                readSensorBtn.innerText = "✅ Captured";
            } else {
                alert("Failed to read from sensor.");
                readSensorBtn.innerText = "📡 Read Sensor";
            }
        } catch(error) {
            console.error(error);
            alert("Error connecting to hardware endpoint.");
            readSensorBtn.innerText = "📡 Read Sensor";
        } finally {
            setTimeout(() => {
                readSensorBtn.disabled = false;
                readSensorBtn.innerText = "📡 Read Sensor";
            }, 3000);
        }
    });
}

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('submit-btn');
        btn.disabled = true;
        btn.innerText = "Analyzing...";

        const studentId = document.getElementById('student_id').value.trim();
        const alcoholLevel = document.getElementById('alcohol_level').value;

        try {
            // Submit reading
            const res = await fetch('/api/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ student_id: studentId, alcohol_level: alcoholLevel })
            });

            const data = await res.json();
            
            // Show results panel
            document.getElementById('results-panel').style.display = 'block';
            
            // Apply data to DOM
            updateDashboard(studentId, data);
            
            // Speak suggestion
            speakFeedback(data.suggestion);
            
            // Fetch and update chart
            await fetchHistory(studentId);

        } catch (error) {
            console.error("Error submitting data", error);
            alert("Failed to analyze data.");
        } finally {
            btn.disabled = false;
            btn.innerText = "Submit Reading";
        }
    });
}

function updateDashboard(studentId, data) {
    // Classification Badge
    const badge = document.getElementById('classification-badge');
    badge.innerText = data.classification;
    badge.className = 'badge ' + data.classification.toLowerCase().replace(' ', '-');
    
    // Stats
    document.getElementById('risk-score').innerText = data.score;
    document.getElementById('clean-streak').innerText = data.clean_streak + ' days';
    document.getElementById('escalation-status').innerText = data.escalation;
    
    // AI Texts
    document.getElementById('ai-suggestion').innerText = data.suggestion;
    document.getElementById('behavior-prediction').innerText = data.prediction;
    
    // Avoidance Warning
    const warning = document.getElementById('avoidance-warning');
    if (data.avoidance) {
        warning.style.display = 'block';
    } else {
        warning.style.display = 'none';
    }
}

async function fetchHistory(studentId) {
    try {
        const res = await fetch(`/api/history/${studentId}`);
        const historyData = await res.json();
        
        document.getElementById('history-panel').style.display = 'block';
        updateChart(historyData.labels, historyData.data, historyData.analysis.classification);
    } catch(err) {
        console.error("Failed to load history", err);
    }
}

function updateChart(labels, dataPoints, currentClass) {
    const ctx = document.getElementById('history-chart').getContext('2d');
    
    let lineColor = '#3b82f6';
    if(currentClass === 'SAFE') lineColor = '#10b981';
    if(currentClass === 'OCCASIONAL') lineColor = '#f59e0b';
    if(currentClass === 'CONSISTENT') lineColor = '#f97316';
    if(currentClass === 'HIGH RISK') lineColor = '#ef4444';

    if (historyChart) {
        historyChart.destroy();
    }

    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Alcohol Level',
                data: dataPoints,
                borderColor: lineColor,
                backgroundColor: lineColor + '33', // 20% opacity
                borderWidth: 2,
                pointBackgroundColor: lineColor,
                pointRadius: 4,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function speakFeedback(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        
        // Optional: Selecting a preferred voice if available
        const voices = window.speechSynthesis.getVoices();
        const enVoice = voices.find(v => v.lang.startsWith('en'));
        if (enVoice) utterance.voice = enVoice;

        window.speechSynthesis.speak(utterance);
    } else {
        console.warn("Speech Synthesis not supported in this browser.");
    }
}

// Faculty specific code
async function fetchFacultyData() {
    const tbody = document.getElementById('student-table-body');
    if (!tbody) return; // Not on faculty page
    
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Loading data...</td></tr>';
    
    try {
        const res = await fetch('/api/all_students');
        const students = await res.json();
        
        if (students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No student data available.</td></tr>';
            return;
        }

        let html = '';
        students.forEach(s => {
            const rowClass = s.classification === 'HIGH RISK' ? 'style="background: rgba(239, 68, 68, 0.1);"' : '';
            const avoidanceHTML = s.avoidance ? '<span style="color: #ef4444; font-weight: bold;">Yes ⚠️</span>' : '<span style="color: #10b981;">No</span>';
            const badgeClass = 'badge ' + s.classification.toLowerCase().replace(' ', '-');
            
            html += `<tr ${rowClass}>
                <td style="font-weight: bold;">${s.student_id}</td>
                <td><span class="${badgeClass}">${s.classification}</span></td>
                <td><strong>${s.score}</strong></td>
                <td>${s.streak} days</td>
                <td>${avoidanceHTML}</td>
                <td>${s.escalation}</td>
            </tr>`;
        });
        
        tbody.innerHTML = html;
        
    } catch(err) {
        console.error(err);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Failed to load data.</td></tr>';
    }
}
