// Manejo de estilos para radio buttons
document.querySelectorAll('input[name="sex"]').forEach(radio => {
    radio.addEventListener('change', function() {
        document.querySelectorAll('.radio-item').forEach(item => {
            item.classList.remove('selected');
        });
        this.closest('.radio-item').classList.add('selected');
    });
});

// Manejo del formulario
document.getElementById('titanicForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Mostrar loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
    
    // Recopilar datos del formulario
    const formData = new FormData(this);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // Imprimir datos en la consola para depuración
    console.log('Datos enviados:', data);
    
    // Llamada a la API de Flask
    fetch('/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la predicción');
        }
        return response.json();
    })
    .then(result => {
        showResult(result);
    })
    .catch(error => {
        document.getElementById('loading').style.display = 'none';
        const resultDiv = document.getElementById('result');
        resultDiv.className = 'result danger';
        resultDiv.innerHTML = `
            <h3>❌ Error</h3>
            <p>${error.message}</p>
        `;
        resultDiv.style.display = 'block';
    });
});

function showResult(result) {
    document.getElementById('loading').style.display = 'none';
    const resultDiv = document.getElementById('result');
    
    if (result.error) {
        resultDiv.className = 'result danger';
        resultDiv.innerHTML = `
            <h3>❌ Error</h3>
            <p>${result.error}</p>
        `;
    } else if (result.survived) {
        resultDiv.className = 'result success';
        resultDiv.innerHTML = `
            <h3>✅ ${result.passenger_name} habría SOBREVIVIDO</h3>
            <p>Probabilidad de supervivencia: ${result.probability}%</p>
            <p>Basado en las características del pasajero, el modelo predice que habría sobrevivido al hundimiento del Titanic.</p>
        `;
    } else {
        resultDiv.className = 'result danger';
        resultDiv.innerHTML = `
            <h3>❌ ${result.passenger_name} NO habría sobrevivido</h3>
            <p>Probabilidad de supervivencia: ${result.probability}%</p>
            <p>Basado en las características del pasajero, el modelo predice que no habría sobrevivido al hundimiento del Titanic.</p>
        `;
    }
    
    resultDiv.style.display = 'block';
}

// Validación en tiempo real
document.getElementById('age').addEventListener('input', function() {
    if (this.value < 0) this.value = 0;
    if (this.value > 120) this.value = 120;
});

document.getElementById('sibsp').addEventListener('input', function() {
    if (this.value < 0) this.value = 0;
    if (this.value > 10) this.value = 10;
});

document.getElementById('parch').addEventListener('input', function() {
    if (this.value < 0) this.value = 0;
    if (this.value > 10) this.value = 10;
});

document.getElementById('fare').addEventListener('input', function() {
    if (this.value < 0) this.value = 0;
});