// Datos de prueba
const testData = [
    { Pclass: 3, Name: "Davies, Mr. Alfred J", Sex: "male", Age: 24, SibSp: 2, Parch: 0, Ticket: "519", Fare: 24.15 },
    { Pclass: 3, Name: "Cribb, Mr. John Hatfield", Sex: "male", Age: 44, SibSp: 0, Parch: 1, Ticket: "470", Fare: 16.1 },
    { Pclass: 3, Name: 'Leeni, Mr. Fahim ("Philip Zenni")', Sex: "male", Age: 22, SibSp: 0, Parch: 0, Ticket: "171", Fare: 7.225 },
    { Pclass: 3, Name: "Hansen, Mr. Claus Peter", Sex: "male", Age: 41, SibSp: 2, Parch: 0, Ticket: "399", Fare: 14.1083 },
    { Pclass: 3, Name: 'Murphy, Miss. Katherine "Kate"', Sex: "female", Age: 18.42, SibSp: 1, Parch: 0, Ticket: "444", Fare: 15.5 },
    { Pclass: 3, Name: "de Messemaeker, Mrs. Guillaume Joseph (Emma)", Sex: "female", Age: 36, SibSp: 1, Parch: 0, Ticket: "300", Fare: 17.4 },
    { Pclass: 2, Name: "Buss, Miss. Kate", Sex: "female", Age: 36, SibSp: 0, Parch: 0, Ticket: "220", Fare: 13 },
    { Pclass: 1, Name: "Butt, Major. Archibald Willingham", Sex: "male", Age: 45, SibSp: 0, Parch: 0, Ticket: "21", Fare: 26.55 },
    { Pclass: 1, Name: "Thayer, Mr. John Borland", Sex: "male", Age: 49, SibSp: 1, Parch: 1, Ticket: "83", Fare: 110.8833 },
    { Pclass: 2, Name: "Kantor, Mr. Sinai", Sex: "male", Age: 34, SibSp: 1, Parch: 0, Ticket: "150", Fare: 26 },
    { Pclass: 3, Name: "McMahon, Mr. Martin", Sex: "male", Age: 28.46, SibSp: 0, Parch: 0, Ticket: "463", Fare: 7.75 },
    { Pclass: 3, Name: "Vander Planke, Mr. Leo Edmondus", Sex: "male", Age: 16, SibSp: 2, Parch: 0, Ticket: "302", Fare: 18 },
    { Pclass: 3, Name: "Honkanen, Miss. Eliina", Sex: "female", Age: 27, SibSp: 0, Parch: 0, Ticket: "670", Fare: 7.925 }
];

// Función para rellenar el formulario con datos de prueba aleatorios
document.getElementById('fillTestData').addEventListener('click', function() {
    console.log('Botón de datos de prueba clicado');
    
    // Seleccionar un registro aleatorio
    const randomIndex = Math.floor(Math.random() * testData.length);
    const testRecord = testData[randomIndex];
    console.log('Registro de prueba seleccionado:', testRecord);

    // Rellenar los campos del formulario
    document.getElementById('pclass').value = testRecord.Pclass;
    document.getElementById('name').value = testRecord.Name;
    document.getElementById('male').checked = testRecord.Sex === 'male';
    document.getElementById('female').checked = testRecord.Sex === 'female';
    document.getElementById('age').value = testRecord.Age.toFixed(2);
    document.getElementById('sibsp').value = testRecord.SibSp;
    document.getElementById('parch').value = testRecord.Parch;
    document.getElementById('ticket').value = testRecord.Ticket;
    document.getElementById('fare').value = testRecord.Fare.toFixed(2);

    // Actualizar estilos de los radio buttons
    document.querySelectorAll('.radio-item').forEach(item => {
        item.classList.remove('selected');
    });
    if (testRecord.Sex === 'male') {
        document.getElementById('male').closest('.radio-item').classList.add('selected');
    } else if (testRecord.Sex === 'female') {
        document.getElementById('female').closest('.radio-item').classList.add('selected');
    }

    // Disparar el envío del formulario
    console.log('Enviando formulario automáticamente...');
    document.getElementById('titanicForm').dispatchEvent(new Event('submit'));
});

// Manejo de estilos para radio buttons
document.querySelectorAll('input[name="sex"]').forEach(radio => {
    radio.addEventListener('change', function() {
        console.log('Radio button changed:', this.value);
        document.querySelectorAll('.radio-item').forEach(item => {
            item.classList.remove('selected');
        });
        this.closest('.radio-item').classList.add('selected');
    });
});

// Manejo del formulario
document.getElementById('titanicForm').addEventListener('submit', function(e) {
    e.preventDefault();
    console.log('Formulario enviado, interceptando submit...');
    
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
        console.log('Respuesta recibida:', response);
        if (!response.ok) {
            throw new Error(`Error en la predicción: ${response.statusText}`);
        }
        return response.json();
    })
    .then(result => {
        console.log('Resultado de la predicción:', result);
        showResult(result);
    })
    .catch(error => {
        console.error('Error en fetch:', error);
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
            <p>Basado en las características del pasajero, el modelo predice que habría sobrevivido al hundimiento del Titanic.</p>
        `;
    } else {
        resultDiv.className = 'result danger';
        resultDiv.innerHTML = `
            <h3>❌ ${result.passenger_name} NO habría sobrevivido</h3>
            <p>Basado en las características del pasajero, el modelo predice que no habría sobrevivido al hundimiento del Titanic.</p>
        `;
    }
    
    resultDiv.style.display = 'block';
}

// Validación en tiempo real
document.getElementById('age').addEventListener('input', function() {
    console.log('Validando edad:', this.value);
    if (this.value < 0) this.value = 0;
    if (this.value > 120) this.value = 120;
});

document.getElementById('sibsp').addEventListener('input', function() {
    console.log('Validando sibsp:', this.value);
    if (this.value < 0) this.value = 0;
    if (this.value > 10) this.value = 10;
});

document.getElementById('parch').addEventListener('input', function() {
    console.log('Validando parch:', this.value);
    if (this.value < 0) this.value = 0;
    if (this.value > 10) this.value = 10;
});

document.getElementById('fare').addEventListener('input', function() {
    console.log('Validando fare:', this.value);
    if (this.value < 0) this.value = 0;
});