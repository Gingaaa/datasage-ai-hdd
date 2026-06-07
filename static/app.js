document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('upload-section');
    const reportSection = document.getElementById('report-section');
    const fileInput = document.getElementById('file-input');
    const statusMsg = document.getElementById('upload-status');
    const resetBtn = document.getElementById('reset-btn');
    const exportBtn = document.getElementById('export-btn');
    const reportContent = document.getElementById('report-content');
    
    const rawTextInput = document.getElementById('raw-text-input');
    const submitTextBtn = document.getElementById('submit-text-btn');
    
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    let currentReportMarkdown = '';

    // Drag and Drop Handlers
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileUpload(e.target.files[0]);
        }
    });

    resetBtn.addEventListener('click', () => {
        uploadZone.style.display = 'flex';
        reportSection.classList.add('hidden');
        
        fileInput.value = '';
        statusMsg.textContent = '';
        statusMsg.className = 'status-message';
        rawTextInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;
        currentReportMarkdown = '';
        reportContent.innerHTML = '';
        chatMessages.innerHTML = `<div class="message system-msg"><p>Upload any data file to start exploring!</p></div>`;
    });

    const exportDropdownBtn = document.getElementById('export-dropdown-btn');
    const exportDropdownMenu = document.getElementById('export-options');
    const exportPdf = document.getElementById('export-pdf');
    const exportDocx = document.getElementById('export-docx');
    const exportPptx = document.getElementById('export-pptx');
    const exportMd = document.getElementById('export-md');

    // Dropdown toggle
    if (exportDropdownBtn) {
        exportDropdownBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            exportDropdownMenu.parentElement.classList.toggle('show');
        });
    }

    // Close dropdown when clicking outside
    window.addEventListener('click', () => {
        if (exportDropdownMenu && exportDropdownMenu.parentElement.classList.contains('show')) {
            exportDropdownMenu.parentElement.classList.remove('show');
        }
    });

    // Export PDF (Native printing for perfect vector/text PDF)
    if (exportPdf) {
        exportPdf.addEventListener('click', (e) => {
            e.preventDefault();
            if (!currentReportMarkdown) return;
            window.print();
        });
    }

    // Export DOCX (Backend generation)
    if (exportDocx) {
        exportDocx.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!currentReportMarkdown) return;
            await downloadFromBackend('/api/export/docx', 'Data_Analytics_Report.docx');
        });
    }

    // Export PPTX (Backend generation)
    if (exportPptx) {
        exportPptx.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!currentReportMarkdown) return;
            await downloadFromBackend('/api/export/pptx', 'Data_Analytics_Report.pptx');
        });
    }

    // Export Markdown (Frontend generation)
    if (exportMd) {
        exportMd.addEventListener('click', (e) => {
            e.preventDefault();
            if (!currentReportMarkdown) return;
            const blob = new Blob([currentReportMarkdown], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Data_Analytics_Report.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }

    async function downloadFromBackend(endpoint, filename) {
        showStatus('Generating file...', 'loading');
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ markdown: currentReportMarkdown })
            });
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                showStatus('Export successful!', 'success');
            } else {
                showStatus('Export failed on server.', 'error');
            }
        } catch (error) {
            showStatus('Error downloading file.', 'error');
        }
    }

    async function handleFileUpload(file) {
        showStatus('Analyzing file and generating comprehensive report... This may take a moment.', 'loading');
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload/unified', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showStatus('Success!', 'success');
                setTimeout(() => {
                    renderReport(data.report_markdown, data.report_charts);
                    enableChat();
                }, 500);
            } else {
                showStatus(`Error: ${data.detail}`, 'error');
            }
        } catch (error) {
            showStatus('Failed to upload file. Make sure the backend is running.', 'error');
        }
    }

    submitTextBtn.addEventListener('click', async () => {
        const text = rawTextInput.value.trim();
        if (!text) {
            showStatus('Please enter some text first.', 'error');
            return;
        }

        showStatus('Processing text and generating report...', 'loading');
        submitTextBtn.disabled = true;

        try {
            const response = await fetch('/api/upload/unified/text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showStatus('Success!', 'success');
                setTimeout(() => {
                    renderReport(data.report_markdown, data.report_charts);
                    enableChat();
                }, 500);
            } else {
                showStatus(`Error: ${data.detail}`, 'error');
            }
        } catch (error) {
            showStatus('Failed to process text.', 'error');
        } finally {
            submitTextBtn.disabled = false;
        }
    });

    function showStatus(text, type) {
        statusMsg.textContent = text;
        statusMsg.className = `status-message ${type}`;
    }

    function renderReport(markdown, reportCharts) {
        currentReportMarkdown = markdown;
        uploadZone.style.display = 'none';
        reportSection.classList.remove('hidden');
        
        // Use marked.js to render markdown
        if (typeof marked !== 'undefined') {
            reportContent.innerHTML = marked.parse(markdown);
        } else {
            // Fallback basic rendering
            reportContent.innerHTML = `<pre style="white-space: pre-wrap;">${markdown}</pre>`;
        }
        
        // Render proactive charts if any
        if (reportCharts && reportCharts.length > 0) {
            // Fallback container for charts that don't match any inline text
            const fallbackContainer = document.createElement('div');
            fallbackContainer.className = 'report-charts-container';
            fallbackContainer.style.marginTop = '2rem';
            fallbackContainer.style.display = 'flex';
            fallbackContainer.style.flexDirection = 'column';
            fallbackContainer.style.gap = '2rem';
            
            reportCharts.forEach((chartData, index) => {
                const chartWrapper = document.createElement('div');
                chartWrapper.className = 'inline-chart-wrapper';
                
                const canvas = document.createElement('canvas');
                const chartId = 'report-chart-' + index + '-' + Date.now();
                canvas.id = chartId;
                chartWrapper.appendChild(canvas);
                
                // Try to insert inline
                let insertedInline = false;
                if (chartData.col) {
                    // Look for headers or bold text mentioning the column name
                    const searchEls = reportContent.querySelectorAll('h2, h3, h4, strong');
                    for (let el of searchEls) {
                        if (el.textContent.includes(chartData.col)) {
                            let blockEl = el;
                            // If it's a strong tag, get the parent paragraph
                            if (el.tagName === 'STRONG') {
                                blockEl = el.closest('p, li') || el.parentElement;
                            }
                            
                            // Insert chart after this block element
                            if (blockEl && blockEl.parentNode) {
                                if (blockEl.nextSibling) {
                                    blockEl.parentNode.insertBefore(chartWrapper, blockEl.nextSibling);
                                } else {
                                    blockEl.parentNode.appendChild(chartWrapper);
                                }
                                insertedInline = true;
                                break;
                            }
                        }
                    }
                }
                
                if (!insertedInline) {
                    fallbackContainer.appendChild(chartWrapper);
                }
                
                // Initialize chart asynchronously so it's in the DOM
                setTimeout(() => {
                    new Chart(document.getElementById(chartId), {
                        type: chartData.type,
                        data: {
                            labels: chartData.labels,
                            datasets: [{
                                label: chartData.title,
                                data: chartData.values,
                                backgroundColor: [
                                    'rgba(59, 130, 246, 0.6)',
                                    'rgba(16, 185, 129, 0.6)',
                                    'rgba(245, 158, 11, 0.6)',
                                    'rgba(239, 68, 68, 0.6)',
                                    'rgba(139, 92, 246, 0.6)',
                                    'rgba(236, 72, 153, 0.6)',
                                    'rgba(14, 165, 233, 0.6)'
                                ],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                title: {
                                    display: true,
                                    text: chartData.title
                                }
                            }
                        }
                    });
                }, 10);
            });
            
            // Only append fallback if it has children
            if (fallbackContainer.children.length > 0) {
                reportContent.appendChild(fallbackContainer);
            }
        }
        
        addMessage('Analysis complete! I have generated a comprehensive report for you. You can now ask me questions about it.', 'system-msg');
    }

    // Chat Functionality
    function enableChat() {
        chatInput.disabled = false;
        sendBtn.disabled = false;
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, 'user-msg');
        chatInput.value = '';
        
        // Show loading indicator
        const typingId = addTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            removeElement(typingId);
            
            if (response.ok) {
                // If it's a markdown response from the agent
                addMessage(data.reply, 'agent-msg');
                if (data.chart_data) {
                    renderChart(data.chart_data);
                }
            } else {
                addMessage(`Error: ${data.detail}`, 'system-msg');
            }
        } catch (error) {
            removeElement(typingId);
            addMessage('Error communicating with the agent.', 'system-msg');
        }
    }

    function addMessage(text, className) {
        const div = document.createElement('div');
        div.className = `message ${className}`;
        
        // Render markdown in chat using marked if available
        if (typeof marked !== 'undefined' && className === 'agent-msg') {
            div.innerHTML = marked.parse(text);
        } else {
            // Basic fallback for user messages
            const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
            div.innerHTML = formattedText;
        }
        
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function renderChart(chartData) {
        const div = document.createElement('div');
        div.className = 'message agent-msg chart-message';
        div.style.width = '100%';
        div.style.maxWidth = '100%';
        div.style.backgroundColor = 'rgba(255, 255, 255, 0.9)'; // white bg for chart
        div.style.color = '#000';
        
        const canvas = document.createElement('canvas');
        const chartId = 'chart-' + Date.now();
        canvas.id = chartId;
        div.appendChild(canvas);
        
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        new Chart(document.getElementById(chartId), {
            type: chartData.type,
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: chartData.title,
                    data: chartData.values,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.6)',
                        'rgba(16, 185, 129, 0.6)',
                        'rgba(245, 158, 11, 0.6)',
                        'rgba(239, 68, 68, 0.6)',
                        'rgba(139, 92, 246, 0.6)',
                        'rgba(236, 72, 153, 0.6)',
                        'rgba(14, 165, 233, 0.6)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: chartData.title
                    }
                }
            }
        });
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'typing-indicator';
        div.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeElement(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
