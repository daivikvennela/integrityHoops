/**
 * ML Notebook Editor
 * Interactive notebook interface with code execution and output display
 */

class MLNotebook {
    constructor(options = {}) {
        this.kernelSessionId = options.kernelSessionId;
        this.apiBaseUrl = options.apiBaseUrl || '/api/notebook';
        this.cells = [];
        this.cellIdCounter = 0;
        this.executionCounter = 0;
        
        // DOM elements
        this.cellsContainer = document.getElementById('cellsContainer');
        this.outputContainer = document.getElementById('outputContainer');
        this.outputInfo = document.getElementById('outputInfo');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('Initializing ML Notebook...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Add initial cell
        this.addCell('# Welcome to ML Notebook\n# Start coding here...\nprint("Hello, World!")');
        
        // Load from localStorage if available
        this.loadFromLocalStorage();
        
        // Auto-save every 30 seconds
        setInterval(() => this.saveToLocalStorage(), 30000);
        
        console.log('ML Notebook initialized successfully');
    }
    
    setupEventListeners() {
        // Add cell button
        document.getElementById('addCellBtn').addEventListener('click', () => {
            this.addCell('');
        });
        
        // Run all button
        document.getElementById('runAllBtn').addEventListener('click', () => {
            this.runAllCells();
        });
        
        // Clear output button
        document.getElementById('clearOutputBtn').addEventListener('click', () => {
            this.clearOutput();
        });
        
        // Restart kernel button
        document.getElementById('restartKernelBtn').addEventListener('click', () => {
            this.restartKernel();
        });
        
        // Save notebook button
        document.getElementById('saveNotebookBtn').addEventListener('click', () => {
            this.saveNotebook();
        });
        
        // Template select
        document.getElementById('templateSelect').addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadTemplate(e.target.value);
            }
        });
        
        // CSV select and load
        document.getElementById('loadCsvBtn').addEventListener('click', () => {
            const csvSelect = document.getElementById('csvSelect');
            if (csvSelect.value) {
                this.loadCSV(csvSelect.value);
            } else {
                this.showNotification('Please select a CSV file', 'warning');
            }
        });
        
        // CSV upload
        document.getElementById('csvUpload').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadCSV(e.target.files[0]);
            }
        });
        
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(btn.dataset.tab);
            });
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+S / Cmd+S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveNotebook();
            }
        });
    }
    
    addCell(code = '', cellType = 'code') {
        const cellId = `cell-${this.cellIdCounter++}`;
        
        // Clone cell template
        const template = document.getElementById('cellTemplate');
        const cellElement = template.content.cloneNode(true);
        const cell = cellElement.querySelector('.notebook-cell');
        
        cell.dataset.cellId = cellId;
        
        // Get textarea for CodeMirror
        const textarea = cell.querySelector('.cell-code');
        
        // Append to container
        this.cellsContainer.appendChild(cellElement);
        
        // Initialize CodeMirror
        const editor = CodeMirror.fromTextArea(textarea, {
            mode: 'python',
            theme: 'monokai',
            lineNumbers: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            indentUnit: 4,
            indentWithTabs: false,
            extraKeys: {
                'Shift-Enter': () => {
                    this.runCell(cellId);
                },
                'Tab': (cm) => {
                    cm.replaceSelection('    ');
                }
            }
        });
        
        editor.setValue(code);
        
        // Store cell data
        this.cells.push({
            id: cellId,
            type: cellType,
            editor: editor,
            element: cell
        });
        
        // Set up cell controls
        const runBtn = cell.querySelector('.run-cell');
        const deleteBtn = cell.querySelector('.delete-cell');
        
        runBtn.addEventListener('click', () => this.runCell(cellId));
        deleteBtn.addEventListener('click', () => this.deleteCell(cellId));
        
        return cellId;
    }
    
    deleteCell(cellId) {
        const index = this.cells.findIndex(c => c.id === cellId);
        if (index !== -1) {
            const cell = this.cells[index];
            cell.element.remove();
            this.cells.splice(index, 1);
            this.saveToLocalStorage();
        }
    }
    
    async runCell(cellId) {
        const cell = this.cells.find(c => c.id === cellId);
        if (!cell) return;
        
        const code = cell.editor.getValue();
        if (!code.trim()) {
            this.showNotification('Cell is empty', 'warning');
            return;
        }
        
        // Update cell UI
        const cellElement = cell.element;
        const statusElement = cellElement.querySelector('.cell-status');
        const execCountElement = cellElement.querySelector('.exec-count');
        
        cellElement.classList.add('executing');
        statusElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
        
        try {
            // Execute code
            const result = await this.executeCode(code);
            
            // Update execution count
            this.executionCounter++;
            execCountElement.textContent = this.executionCounter;
            
            // Display output
            this.addOutput(result, cellId);
            
            // Update cell status
            if (result.success) {
                statusElement.innerHTML = '<i class="fas fa-check" style="color: var(--success-green);"></i> Done';
                cellElement.classList.remove('error');
            } else {
                statusElement.innerHTML = '<i class="fas fa-times" style="color: var(--error-red);"></i> Error';
                cellElement.classList.add('error');
            }
            
        } catch (error) {
            console.error('Error running cell:', error);
            statusElement.innerHTML = '<i class="fas fa-times" style="color: var(--error-red);"></i> Error';
            cellElement.classList.add('error');
            this.showNotification('Error executing cell: ' + error.message, 'error');
        } finally {
            cellElement.classList.remove('executing');
            setTimeout(() => {
                statusElement.textContent = '';
            }, 3000);
        }
    }
    
    async runAllCells() {
        this.showLoading(true);
        
        for (const cell of this.cells) {
            await this.runCell(cell.id);
            // Small delay between cells
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        this.showLoading(false);
        this.showNotification('All cells executed successfully', 'success');
    }
    
    async executeCode(code) {
        const response = await fetch(`${this.apiBaseUrl}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                timeout: 60
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    addOutput(result, cellId) {
        // Switch to output tab
        this.switchTab('output');
        
        // Create output item
        const outputItem = document.createElement('div');
        outputItem.className = 'output-item';
        outputItem.dataset.cellId = cellId;
        
        const timestamp = new Date().toLocaleTimeString();
        
        let html = `
            <div class="output-header">
                <div class="output-label">
                    <i class="fas fa-terminal"></i>
                    Cell Output
                </div>
                <div class="output-timestamp">${timestamp}</div>
            </div>
        `;
        
        // Add text output
        if (result.text_output) {
            html += `
                <div class="output-text">${this.escapeHtml(result.text_output)}</div>
            `;
        }
        
        // Add error output
        if (result.error_output) {
            html += `
                <div class="output-error">
                    <strong><i class="fas fa-exclamation-triangle"></i> Error:</strong><br>
                    ${this.escapeHtml(result.error_output)}
                </div>
            `;
        }
        
        // Add HTML outputs (tables, etc.)
        if (result.html_outputs && result.html_outputs.length > 0) {
            result.html_outputs.forEach(output => {
                html += `<div class="output-html">${output.content}</div>`;
            });
        }
        
        // Add image outputs (plots)
        if (result.image_outputs && result.image_outputs.length > 0) {
            result.image_outputs.forEach(output => {
                html += `
                    <div class="output-image-container">
                        <img src="data:image/${output.format};base64,${output.data}" 
                             alt="Plot" class="output-image">
                    </div>
                `;
            });
        }
        
        outputItem.innerHTML = html;
        this.outputContainer.appendChild(outputItem);
        
        // Update output info
        this.outputInfo.textContent = `${this.outputContainer.children.length} output(s)`;
        
        // Scroll to bottom
        outputItem.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
    
    clearOutput() {
        this.outputContainer.innerHTML = '';
        this.outputInfo.textContent = 'No output yet. Run some cells to see results here.';
        this.showNotification('Output cleared', 'info');
    }
    
    async loadTemplate(templateName) {
        if (!confirm(`Load ${templateName} template? This will replace current cells.`)) {
            document.getElementById('templateSelect').value = '';
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/load-template`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ template: templateName })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Clear existing cells
                this.cells.forEach(cell => cell.element.remove());
                this.cells = [];
                this.cellIdCounter = 0;
                
                // Add new cells from template
                data.cells.forEach(cell => {
                    this.addCell(cell.content, cell.type);
                });
                
                this.showNotification(`Template "${templateName}" loaded successfully`, 'success');
            } else {
                throw new Error(data.error || 'Failed to load template');
            }
            
        } catch (error) {
            console.error('Error loading template:', error);
            this.showNotification('Error loading template: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
            document.getElementById('templateSelect').value = '';
        }
    }
    
    async loadCSV(filename) {
        this.showLoading(true);
        
        try {
            // Get CSV info
            const response = await fetch(`${this.apiBaseUrl}/csv-info/${filename}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to get CSV info');
            }
            
            const info = data.info;
            
            // Generate load code
            const loadCode = `# CSV File: ${filename}
# Shape: ${info.shape[0]} rows × ${info.shape[1]} columns
# Columns: ${info.columns.join(', ')}

import pandas as pd
df = pd.read_csv('${this.getUploadPath()}/${filename}')

print(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
print(f"\\nColumns: {df.columns.tolist()}")
print(f"\\nMemory usage: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
print("\\nFirst 5 rows:")
df.head()`;
            
            // Add cell with load code and run it
            const cellId = this.addCell(loadCode);
            await this.runCell(cellId);
            
            this.showNotification(`CSV "${filename}" loaded successfully`, 'success');
            
        } catch (error) {
            console.error('Error loading CSV:', error);
            this.showNotification('Error loading CSV: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async uploadCSV(file) {
        this.showLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.apiBaseUrl}/upload-csv`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Add cell with the load code
                const cellId = this.addCell(data.load_code);
                
                // Update CSV select dropdown
                const csvSelect = document.getElementById('csvSelect');
                const option = document.createElement('option');
                option.value = data.filename;
                option.textContent = data.filename;
                csvSelect.appendChild(option);
                csvSelect.value = data.filename;
                
                this.showNotification(`File "${data.filename}" uploaded successfully`, 'success');
                
                // Show output in output tab
                this.addOutput({
                    success: true,
                    text_output: data.execution_output,
                    error_output: '',
                    html_outputs: [],
                    image_outputs: []
                }, cellId);
            } else {
                throw new Error(data.error || 'Failed to upload CSV');
            }
            
        } catch (error) {
            console.error('Error uploading CSV:', error);
            this.showNotification('Error uploading CSV: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
            // Reset file input
            document.getElementById('csvUpload').value = '';
        }
    }
    
    async restartKernel() {
        if (!confirm('Restart kernel? All variables will be lost.')) {
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/kernel/restart`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.kernelSessionId = data.kernel_session_id;
                this.executionCounter = 0;
                
                // Reset execution counts
                document.querySelectorAll('.exec-count').forEach(el => {
                    el.textContent = '-';
                });
                
                // Clear output
                this.clearOutput();
                
                this.showNotification('Kernel restarted successfully', 'success');
            } else {
                throw new Error(data.error || 'Failed to restart kernel');
            }
            
        } catch (error) {
            console.error('Error restarting kernel:', error);
            this.showNotification('Error restarting kernel: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async saveNotebook() {
        const filename = prompt('Enter notebook name:', 'my_notebook.ipynb');
        if (!filename) return;
        
        this.showLoading(true);
        
        try {
            // Collect all cells
            const cells = this.cells.map(cell => ({
                type: cell.type,
                content: cell.editor.getValue()
            }));
            
            const response = await fetch(`${this.apiBaseUrl}/save-notebook`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cells: cells,
                    filename: filename
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`Notebook saved as "${data.filename}"`, 'success');
            } else {
                throw new Error(data.error || 'Failed to save notebook');
            }
            
        } catch (error) {
            console.error('Error saving notebook:', error);
            this.showNotification('Error saving notebook: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // Update tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane.id === `${tabName}Tab`);
        });
    }
    
    saveToLocalStorage() {
        try {
            const notebookData = {
                cells: this.cells.map(cell => ({
                    type: cell.type,
                    content: cell.editor.getValue()
                })),
                timestamp: Date.now()
            };
            
            localStorage.setItem('ml_notebook_state', JSON.stringify(notebookData));
            console.log('Notebook saved to localStorage');
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }
    
    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('ml_notebook_state');
            if (saved) {
                const data = JSON.parse(saved);
                
                // Check if data is recent (within 24 hours)
                const age = Date.now() - data.timestamp;
                if (age < 24 * 60 * 60 * 1000) {
                    // Clear default cell
                    this.cells.forEach(cell => cell.element.remove());
                    this.cells = [];
                    this.cellIdCounter = 0;
                    
                    // Load saved cells
                    data.cells.forEach(cell => {
                        this.addCell(cell.content, cell.type);
                    });
                    
                    console.log('Notebook loaded from localStorage');
                }
            }
        } catch (error) {
            console.error('Error loading from localStorage:', error);
        }
    }
    
    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }
    
    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'error' ? 'var(--error-red)' : type === 'success' ? 'var(--success-green)' : 'var(--neon-cyan)'};
            color: ${type === 'success' ? 'var(--dark-bg)' : 'white'};
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease;
            font-weight: 600;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getUploadPath() {
        // This should match the actual upload folder path
        return '/Users/daivikvennela/workspace/testApp/IntegrityHoops/testApp1/data/uploads';
    }
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

