// Modal elements
const modal = document.getElementById('logModal');
const modalTitle = document.getElementById('modalTitle');
const closeModal = document.getElementById('closeModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const logContainer = document.getElementById('logContainer');

// Button elements
const predictBtn = document.getElementById('predictBtn');
const trainBtn = document.getElementById('trainBtn');

// Output element
const outputContent = document.getElementById('outputContent');

// Close modal handlers
closeModal.addEventListener('click', () => {
    modal.style.display = 'none';
});

closeModalBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Helper function to validate and get form data
function getFormData() {
    const form = document.getElementById('predictionForm');
    
    // Get all required fields
    const Gender = parseInt(document.querySelector('input[name="Gender"]:checked')?.value);
    const Age = parseInt(document.getElementById('Age').value);
    const Driving_License = parseInt(document.getElementById('Driving_License').value);
    const Region_Code = parseFloat(document.getElementById('Region_Code').value);
    const Previously_Insured = parseInt(document.getElementById('Previously_Insured').value);
    const Annual_Premium = parseFloat(document.getElementById('Annual_Premium').value);
    const Policy_Sales_Channel = parseFloat(document.getElementById('Policy_Sales_Channel').value);
    const Vintage = parseInt(document.getElementById('Vintage').value);
    const Vehicle_Age = document.getElementById('Vehicle_Age').value;
    const Vehicle_Damage_Yes = parseInt(document.getElementById('Vehicle_Damage_Yes').value);
    
    // Validate all fields
    if (isNaN(Gender) || isNaN(Age) || isNaN(Driving_License) || isNaN(Region_Code) || 
        isNaN(Previously_Insured) || isNaN(Annual_Premium) || isNaN(Policy_Sales_Channel) || 
        isNaN(Vintage) || !Vehicle_Age || isNaN(Vehicle_Damage_Yes)) {
        return null;
    }
    
    // Convert Vehicle_Age to binary fields
    let Vehicle_Age_lt_1_Year = 0;
    let Vehicle_Age_gt_2_Years = 0;
    
    if (Vehicle_Age === 'lt_1') {
        Vehicle_Age_lt_1_Year = 1;
    } else if (Vehicle_Age === 'gt_2') {
        Vehicle_Age_gt_2_Years = 1;
    }
    
    return {
        Gender,
        Age,
        Driving_License,
        Region_Code,
        Previously_Insured,
        Annual_Premium,
        Policy_Sales_Channel,
        Vintage,
        Vehicle_Age_lt_1_Year,
        Vehicle_Age_gt_2_Years,
        Vehicle_Damage_Yes
    };
}

// Predict with logs
predictBtn.addEventListener('click', async () => {
    const data = getFormData();
    
    // Validate form
    if (!data) {
        alert('⚠️ Please fill in all required fields correctly');
        return;
    }
    
    // Open modal
    modalTitle.textContent = 'Prediction Process Logs';
    modal.style.display = 'flex';
    logContainer.innerHTML = '<div class="log-message info">🔍 Connecting to prediction service...</div>';
    
    // Build query string
    const queryParams = new URLSearchParams(data).toString();
    const eventSource = new EventSource(`/predict-stream?${queryParams}`);
    
    predictBtn.disabled = true;
    predictBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> PROCESSING...';
    
    eventSource.onmessage = (event) => {
        const message = event.data;
        
        if (message === 'DONE') {
            eventSource.close();
            predictBtn.disabled = false;
            predictBtn.innerHTML = '<i class="fas fa-chart-line"></i> PREDICT RESPONSE';
            return;
        }
        
        if (message.startsWith('RESULT:')) {
            const result = JSON.parse(message.substring(7));
            
            if (result.status) {
                const willGetInsurance = result.prediction === 1;
                
                // Only show the response badge - nothing else
                outputContent.innerHTML = `
                    <div class="response-badge ${willGetInsurance ? 'positive' : 'negative'}">
                        ${willGetInsurance ? '✓ Customer will likely get insurance' : '✗ Customer unlikely to get insurance'}
                    </div>
                `;
            }
            return;
        }
        
        const logMsg = document.createElement('div');
        logMsg.className = 'log-message';
        
        if (message.includes('ERROR') || message.includes('❌')) {
            logMsg.classList.add('error');
        } else if (message.includes('success') || message.includes('✓')) {
            logMsg.classList.add('success');
        } else if (message.includes('🔍') || message.includes('INFO')) {
            logMsg.classList.add('info');
        }
        
        logMsg.textContent = message;
        logContainer.appendChild(logMsg);
        logContainer.scrollTop = logContainer.scrollHeight;
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
        predictBtn.disabled = false;
        predictBtn.innerHTML = '<i class="fas fa-chart-line"></i> PREDICT RESPONSE';
        
        const errorMsg = document.createElement('div');
        errorMsg.className = 'log-message error';
        errorMsg.textContent = '✗ Connection error. Please try again.';
        logContainer.appendChild(errorMsg);
    };
});

// Train with logs
trainBtn.addEventListener('click', async () => {
    modalTitle.textContent = 'Training Process Logs';
    modal.style.display = 'flex';
    logContainer.innerHTML = '<div class="log-message info">🚀 Connecting to training service...</div>';
    
    const eventSource = new EventSource('/train-stream');
    
    trainBtn.disabled = true;
    trainBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> TRAINING...';
    
    eventSource.onmessage = (event) => {
        const message = event.data;
        
        if (message === 'DONE') {
            eventSource.close();
            trainBtn.disabled = false;
            trainBtn.innerHTML = '<i class="fas fa-brain"></i> TRAIN MODEL';
            return;
        }
        
        const logMsg = document.createElement('div');
        logMsg.className = 'log-message';
        
        if (message.includes('ERROR') || message.includes('❌')) {
            logMsg.classList.add('error');
        } else if (message.includes('success') || message.includes('✓')) {
            logMsg.classList.add('success');
        } else if (message.includes('🚀') || message.includes('INFO')) {
            logMsg.classList.add('info');
        }
        
        logMsg.textContent = message;
        logContainer.appendChild(logMsg);
        logContainer.scrollTop = logContainer.scrollHeight;
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
        trainBtn.disabled = false;
        trainBtn.innerHTML = '<i class="fas fa-brain"></i> TRAIN MODEL';
        
        const errorMsg = document.createElement('div');
        errorMsg.className = 'log-message error';
        errorMsg.textContent = '✗ Connection error. Please try again.';
        logContainer.appendChild(errorMsg);
    };
});
