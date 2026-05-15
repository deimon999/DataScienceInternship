// API Base URL - Change this to your deployment URL
const API_BASE_URL = 'http://localhost:8000';

// Store for analytics
let predictionHistory = [];
let recentPredictions = [];

// ============== Initialization ==============
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    checkAPIStatus();
    loadModelInfo();
    setInterval(checkAPIStatus, 10000); // Check every 10 seconds
});

// Conversion rate USD -> INR (approx). Adjust if needed.
const USD_TO_INR = 82.0;

// ============== Tab Navigation ==============
function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Form submission
    document.getElementById('predictionForm').addEventListener('submit', handlePrediction);

    // Upload area
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('click', () => document.getElementById('csvFile').click());
    uploadArea.addEventListener('dragover', e => {
        e.preventDefault();
        uploadArea.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color');
    });
    uploadArea.addEventListener('dragleave', e => {
        uploadArea.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color');
    });
    uploadArea.addEventListener('drop', e => {
        e.preventDefault();
        uploadArea.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color');
        handleFileUpload(e.dataTransfer.files[0]);
    });

    document.getElementById('csvFile').addEventListener('change', e => {
        handleFileUpload(e.target.files[0]);
    });
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Load data for specific tabs
    if (tabName === 'model-info') {
        loadModelInfo();
    } else if (tabName === 'analytics') {
        loadAnalytics();
    }
}

// ============== API Status Check ==============
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        
        if (data.status === 'healthy') {
            statusIndicator.classList.add('online');
            statusText.textContent = 'API Online';
            statusText.style.color = 'var(--success-color)';
        } else {
            statusIndicator.classList.remove('online');
            statusText.textContent = 'Models Not Loaded';
            statusText.style.color = 'var(--warning-color)';
        }
    } catch (error) {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        statusIndicator.classList.remove('online');
        statusText.textContent = 'API Offline';
        statusText.style.color = 'var(--danger-color)';
    }
}

// ============== Prediction Handling ==============
async function handlePrediction(e) {
    e.preventDefault();
    
    const formData = new FormData(document.getElementById('predictionForm'));
    const data = {
        square_feet: parseFloat(formData.get('square_feet')),
        bedrooms: parseInt(formData.get('bedrooms')),
        bathrooms: parseFloat(formData.get('bathrooms')),
        age: parseInt(formData.get('age')),
        garage: parseInt(formData.get('garage')),
        location_score: parseFloat(formData.get('location_score')),
        condition: formData.get('condition')
    };

    // Validate
    if (!validateInputData(data)) {
        showToast('Please fill all fields with valid values', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || 'Prediction failed', 'error');
            showLoading(false);
            return;
        }

        const result = await response.json();
        displayPredictionResult(result);
        
        // Add to history
        predictionHistory.push({
            ...data,
            predicted_price: result.predicted_price,
            timestamp: new Date().toLocaleString()
        });
        
        showToast('Prediction successful!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error connecting to API: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function displayPredictionResult(result) {
    const inr = document.getElementById('inrToggle') && document.getElementById('inrToggle').checked;
    const predicted = inr ? result.predicted_price * USD_TO_INR : result.predicted_price;
    const lower = inr ? result.prediction_range.lower_bound * USD_TO_INR : result.prediction_range.lower_bound;
    const upper = inr ? result.prediction_range.upper_bound * USD_TO_INR : result.prediction_range.upper_bound;

    document.getElementById('predictedPrice').textContent = formatCurrency(predicted, inr);

    document.getElementById('confidenceFill').style.width = (result.confidence * 100) + '%';
    document.getElementById('confidencePercent').textContent = (result.confidence * 100).toFixed(1) + '%';

    document.getElementById('lowerBound').textContent = formatCurrency(lower, inr);
    document.getElementById('upperBound').textContent = formatCurrency(upper, inr);
    
    document.getElementById('resultSection').style.display = 'block';
    
    // Scroll to result
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    document.getElementById('predictionForm').reset();
    document.getElementById('resultSection').style.display = 'none';
}

// ============== Batch Prediction ==============
async function handleFileUpload(file) {
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
        showToast('Please upload a CSV file', 'error');
        return;
    }

    showLoading(true);

    try {
        const text = await file.text();
        const lines = text.split('\n').filter(line => line.trim());
        
        if (lines.length < 2) {
            showToast('CSV must have at least one data row', 'error');
            showLoading(false);
            return;
        }

        const headers = lines[0].split(',').map(h => h.trim());
        const predictions = [];

        for (let i = 1; i < lines.length && i <= 1000; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const record = {};
            
            headers.forEach((header, index) => {
                if (index < values.length) {
                    record[header] = isNaN(values[index]) ? values[index] : parseFloat(values[index]);
                }
            });

            if (Object.keys(record).length === headers.length) {
                predictions.push(record);
            }
        }

        if (predictions.length === 0) {
            showToast('No valid records found', 'error');
            showLoading(false);
            return;
        }

        // Send batch prediction
        const response = await fetch(`${API_BASE_URL}/batch-predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ data: predictions })
        });

        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || 'Batch prediction failed', 'error');
            showLoading(false);
            return;
        }

        const result = await response.json();
        displayBatchResults(result);
        showToast('Batch prediction completed successfully!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error processing file: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function displayBatchResults(result) {
    const inr = document.getElementById('inrToggle') && document.getElementById('inrToggle').checked;
    document.getElementById('totalPredictions').textContent = result.total_predictions;
    document.getElementById('avgPrice').textContent = formatCurrency(inr ? result.average_price * USD_TO_INR : result.average_price, inr);
    document.getElementById('minPrice').textContent = formatCurrency(inr ? result.price_range.min * USD_TO_INR : result.price_range.min, inr);
    document.getElementById('maxPrice').textContent = formatCurrency(inr ? result.price_range.max * USD_TO_INR : result.price_range.max, inr);

    // Create results table
    let tableHTML = '<table style="width: 100%; border-collapse: collapse;">';
    tableHTML += '<tr style="background: var(--light-bg); border-bottom: 2px solid var(--border-color);">' +
        '<th style="padding: 10px; text-align: left;">House ID</th>' +
        '<th style="padding: 10px; text-align: right;">Predicted Price</th>' +
        '<th style="padding: 10px; text-align: center;">Confidence</th>' +
        '</tr>';

    result.predictions.forEach((pred, index) => {
        const inr = document.getElementById('inrToggle') && document.getElementById('inrToggle').checked;
        const price = inr ? pred.predicted_price * USD_TO_INR : pred.predicted_price;
        tableHTML += '<tr style="border-bottom: 1px solid var(--border-color);">' +
            `<td style="padding: 10px;">#${pred.house_id}</td>` +
            `<td style="padding: 10px; text-align: right; font-weight: 600;">${formatCurrency(price, inr)}</td>` +
            `<td style="padding: 10px; text-align: center;">${(pred.confidence * 100).toFixed(0)}%</td>` +
            '</tr>';
    });

    tableHTML += '</table>';
    document.getElementById('predictionsTable').innerHTML = tableHTML;
    document.getElementById('batchResults').style.display = 'block';
}

// ============== Model Information ==============
async function loadModelInfo() {
    showLoading(true);

    try {
        const [modelResponse, featureResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/model-info`),
            fetch(`${API_BASE_URL}/feature-importance?top_n=10`)
        ]);

        if (!modelResponse.ok || !featureResponse.ok) {
            showToast('Could not load model information', 'warning');
            showLoading(false);
            return;
        }

        const modelData = await modelResponse.json();
        const featureData = await featureResponse.json();

        // Display model details
        let detailsHTML = '<li><span class="label">Model Type</span><span class="value">' + 
            (modelData.model_type || 'Unknown') + '</span></li>';
        detailsHTML += '<li><span class="label">Min Price</span><span class="value">$' + 
            modelData.parameters.min_price.toLocaleString() + '</span></li>';
        detailsHTML += '<li><span class="label">Max Price</span><span class="value">$' + 
            modelData.parameters.max_price.toLocaleString() + '</span></li>';

        document.getElementById('modelDetails').innerHTML = detailsHTML;

        // Display feature importance
        let featureHTML = '';
        Object.entries(featureData.top_features).forEach(([feature, importance]) => {
            featureHTML += `<div style="margin-bottom: 15px;">` +
                `<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">` +
                `<span style="font-weight: 600;">${feature}</span>` +
                `<span style="color: var(--text-light);">${(importance * 100).toFixed(2)}%</span>` +
                `</div>` +
                `<div style="background: var(--border-color); height: 8px; border-radius: 4px; overflow: hidden;">` +
                `<div style="background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); ` +
                `height: 100%; width: ${importance * 100}%; border-radius: 4px;"></div>` +
                `</div></div>`;
        });

        document.getElementById('featureImportance').innerHTML = featureHTML || '<p>No feature data available</p>';
    } catch (error) {
        console.error('Error loading model info:', error);
        showToast('Error loading model information', 'error');
    } finally {
        showLoading(false);
    }
}

// ============== Analytics ==============
function loadAnalytics() {
    updateRecentPredictions();
    updatePriceChart();
}

function updateRecentPredictions() {
    const container = document.getElementById('recentPredictions');
    
    if (predictionHistory.length === 0) {
        container.innerHTML = '<p>No predictions yet</p>';
        return;
    }

    let html = '<ul style="list-style: none; padding: 0;">';
    predictionHistory.slice(-5).reverse().forEach(pred => {
        html += `<li style="padding: 10px; border-bottom: 1px solid var(--border-color);">` +
            `<div style="font-weight: 600;">$${pred.predicted_price.toLocaleString('en-US', {maximumFractionDigits: 0})}</div>` +
            `<div style="font-size: 12px; color: var(--text-light);">${pred.square_feet} sq ft | ${pred.timestamp}</div>` +
            `</li>`;
    });
    html += '</ul>';
    
    container.innerHTML = html;
}

function updatePriceChart() {
    const container = document.getElementById('priceChart');
    
    if (predictionHistory.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-light);">Make predictions to see chart</p>';
        return;
    }

    const prices = predictionHistory.map(p => p.predicted_price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;

    let chartHTML = `
        <div style="padding: 20px;">
            <p style="text-align: center; font-size: 14px; color: var(--text-light);">
                Min: $${minPrice.toLocaleString('en-US', {maximumFractionDigits: 0})} | 
                Avg: $${avgPrice.toLocaleString('en-US', {maximumFractionDigits: 0})} | 
                Max: $${maxPrice.toLocaleString('en-US', {maximumFractionDigits: 0})}
            </p>
            <p style="text-align: center; font-size: 12px; color: var(--text-light); margin-top: 10px;">
                Total predictions: ${prices.length}
            </p>
        </div>
    `;

    container.innerHTML = chartHTML;
}

// ============== Utility Functions ==============
function validateInputData(data) {
    return data.square_feet > 0 &&
        data.bedrooms > 0 &&
        data.bathrooms > 0 &&
        data.age >= 0 &&
        data.garage >= 0 &&
        data.location_score >= 1 && data.location_score <= 10 &&
        data.condition !== '';
}

function formatCurrency(value, inr=false) {
    if (inr) {
        return formatINR(value);
    } else {
        return '$' + Number(value).toLocaleString('en-US', {maximumFractionDigits: 0});
    }
}

function formatINR(x) {
    // Ensure number
    if (isNaN(x) || x === null) return '₹0';
    const num = Math.round(x);
    const str = num.toString();
    let lastThree = str.slice(-3);
    let otherNumbers = str.slice(0, -3);
    if (otherNumbers !== '') lastThree = ',' + lastThree;
    const res = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + lastThree;
    return '₹' + res;
}

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    spinner.style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('errorToast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.style.display = 'block';

    setTimeout(() => {
        toast.style.display = 'none';
    }, 4000);
}
