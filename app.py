import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import traceback
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurar Pandas para evitar la advertencia de FutureWarning
pd.set_option('future.no_silent_downcasting', True)

# Cargar los modelos entrenados
try:
    logger.info("Iniciando carga de modelos...")
    ordinal_encoder = joblib.load('models/ordinal_encoder.pkl')
    robust_scaler = joblib.load('models/robust_scaler.pkl')
    pca_model = joblib.load('models/pca_model.pkl')
    random_forest_model = joblib.load('models/random_forest_model.pkl')
    
    # Log categorías aprendidas por el OrdinalEncoder
    logger.debug("Categorías de OrdinalEncoder:")
    for col, categories in zip(['Sex', 'Embarked', 'Cabin', 'Title', 'Ticket'], ordinal_encoder.categories_):
        logger.debug(f"{col}: {categories.tolist()}")
    logger.info("Modelos cargados exitosamente")
except Exception as e:
    logger.error(f"Error al cargar los modelos: {str(e)}")
    logger.error(traceback.format_exc())
    raise

@app.route('/')
def home():
    request_id = str(uuid.uuid4())
    logger.info(f"Request ID: {request_id} - Accediendo a la página principal")
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    request_id = str(uuid.uuid4())
    logger.debug(f"Request ID: {request_id} - Solicitando favicon")
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/predict', methods=['POST'])
def predict():
    request_id = str(uuid.uuid4())
    logger.info(f"Request ID: {request_id} - Iniciando predicción")
    
    try:
        # Obtener datos del formulario
        data = {
            'Pclass': request.form.get('pclass', ''),
            'Sex': request.form.get('sex', ''),
            'Age': request.form.get('age', ''),
            'SibSp': request.form.get('sibsp', '0'),
            'Parch': request.form.get('parch', '0'),
            'Fare': request.form.get('fare', '0.0'),
            'Embarked': request.form.get('embarked', 'S'),
            'Cabin': request.form.get('cabin', 'Unknown'),
            'Ticket': request.form.get('ticket', 'Unknown'),
            'Name': request.form.get('name', '')
        }
        
        logger.debug(f"Request ID: {request_id} - Datos recibidos: {data}")

        # Validar campos obligatorios
        logger.debug(f"Request ID: {request_id} - Validando campos obligatorios")
        try:
            data['Pclass'] = int(data['Pclass'])
            if data['Pclass'] not in [1, 2, 3]:
                logger.warning(f"Request ID: {request_id} - Clase inválida: {data['Pclass']}")
                return jsonify({'error': 'Clase inválida. Debe ser 1, 2 o 3.'}), 400
        except (ValueError, TypeError):
            logger.warning(f"Request ID: {request_id} - Error en validación de Pclass")
            return jsonify({'error': 'Clase debe ser un número entero (1, 2 o 3).'}), 400

        if data['Sex'] not in ['male', 'female']:
            logger.warning(f"Request ID: {request_id} - Sexo inválido: {data['Sex']}")
            return jsonify({'error': 'Sexo inválido. Debe ser "male" o "female".'}), 400

        try:
            data['Age'] = float(data['Age'])
            if data['Age'] <= 0 or data['Age'] > 120:
                logger.warning(f"Request ID: {request_id} - Edad inválida: {data['Age']}")
                return jsonify({'error': 'Edad inválida. Debe estar entre 0 y 120.'}), 400
        except (ValueError, TypeError):
            logger.warning(f"Request ID: {request_id} - Error en validación de Age")
            return jsonify({'error': 'Edad debe ser un número válido.'}), 400

        if not data['Name']:
            logger.warning(f"Request ID: {request_id} - Nombre vacío")
            return jsonify({'error': 'Nombre es obligatorio.'}), 400

        try:
            data['SibSp'] = int(data['SibSp'])
            if data['SibSp'] < 0 or data['SibSp'] > 10:
                logger.warning(f"Request ID: {request_id} - SibSp inválido: {data['SibSp']}")
                return jsonify({'error': 'Número de hermanos/cónyuges debe estar entre 0 y 10.'}), 400
        except (ValueError, TypeError):
            logger.warning(f"Request ID: {request_id} - Error en validación de SibSp")
            return jsonify({'error': 'Número de hermanos/cónyuges debe ser un número entero.'}), 400

        try:
            data['Parch'] = int(data['Parch'])
            if data['Parch'] < 0 or data['Parch'] > 10:
                logger.warning(f"Request ID: {request_id} - Parch inválido: {data['Parch']}")
                return jsonify({'error': 'Número de padres/hijos debe estar entre 0 y 10.'}), 400
        except (ValueError, TypeError):
            logger.warning(f"Request ID: {request_id} - Error en validación de Parch")
            return jsonify({'error': 'Número de padres/hijos debe ser un número entero.'}), 400

        try:
            data['Fare'] = float(data['Fare'])
            if data['Fare'] < 0:
                logger.warning(f"Request ID: {request_id} - Fare inválido: {data['Fare']}")
                return jsonify({'error': 'Tarifa debe ser un número no negativo.'}), 400
        except (ValueError, TypeError):
            logger.warning(f"Request ID: {request_id} - Error en validación de Fare")
            return jsonify({'error': 'Tarifa debe ser un número válido.'}), 400

        # Crear DataFrame
        logger.debug(f"Request ID: {request_id} - Creando DataFrame")
        df = pd.DataFrame([data])
        logger.debug(f"Request ID: {request_id} - DataFrame creado: {df.to_dict()}")

        # Ingeniería de características
        logger.debug(f"Request ID: {request_id} - Realizando ingeniería de características")
        df['FamilySize'] = df['SibSp'] + df['Parch'] + 1

        # Extraer título con una regex más robusta
        df['Title'] = df['Name'].str.extract(r'(?:^|\s)([A-Za-z]+)\.?\s', expand=False)
        if df['Title'].isna().any():
            logger.warning(f"Request ID: {request_id} - No se pudo extraer título del nombre: {data['Name']}")
            df['Title'] = 'Mr'  # Asignar título por defecto
            logger.debug(f"Request ID: {request_id} - Título asignado por defecto: {df['Title'].iloc[0]}")
        else:
            logger.debug(f"Request ID: {request_id} - Título extraído: {df['Title'].iloc[0]}")

        # Reemplazar títulos
        df['Title'] = df['Title'].replace(['Lady', 'Countess', 'Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
        df['Title'] = df['Title'].replace(['Mlle', 'Ms'], 'Miss')
        df['Title'] = df['Title'].replace('Mme', 'Mrs')
        logger.debug(f"Request ID: {request_id} - Título procesado: {df['Title'].iloc[0]}")

        # Validar que el título sea conocido por el encoder
        known_titles = ['Mr', 'Mrs', 'Miss', 'Master', 'Rare']
        if df['Title'].iloc[0] not in known_titles:
            logger.warning(f"Request ID: {request_id} - Título no reconocido: {df['Title'].iloc[0]}")
            return jsonify({'error': f'Título "{df["Title"].iloc[0]}" no reconocido por el modelo. Use títulos como Mr, Mrs, Miss, Master.'}), 400

        # Validar variables categóricas contra las categorías del OrdinalEncoder
        categorical_cols = ['Sex', 'Embarked', 'Cabin', 'Title', 'Ticket']
        for col, categories in zip(categorical_cols, ordinal_encoder.categories_):
            if df[col].iloc[0] not in categories:
                if col == 'Ticket':
                    df.loc[0, col] = 'Unknown'  # Reemplazar tickets desconocidos
                    logger.debug(f"Request ID: {request_id} - Ticket desconocido reemplazado por 'Unknown'")
                else:
                    logger.warning(f"Request ID: {request_id} - Valor inválido para {col}: {df[col].iloc[0]}")
                    return jsonify({'error': f'Valor "{df[col].iloc[0]}" no válido para {col}. Valores permitidos: {categories.tolist()}'}), 400

        # Codificar variables categóricas
        logger.debug(f"Request ID: {request_id} - Codificando variables categóricas")
        try:
            df[categorical_cols] = ordinal_encoder.transform(df[categorical_cols])
            logger.debug(f"Request ID: {request_id} - Variables categóricas codificadas: {df[categorical_cols].to_dict()}")
        except ValueError as e:
            logger.error(f"Request ID: {request_id} - Error en OrdinalEncoder: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Error en codificación de variables categóricas: {str(e)}'}), 400

        # Seleccionar características para RobustScaler (en el mismo orden que en entrenamiento)
        scaler_features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'FamilySize', 'Title']
        X = df[scaler_features]
        logger.debug(f"Request ID: {request_id} - Características seleccionadas para escalado: {X.to_dict()}")

        # Escalar características
        logger.debug(f"Request ID: {request_id} - Escalando características")
        try:
            X_scaled = robust_scaler.transform(X)
            X_scaled_df = pd.DataFrame(X_scaled, columns=scaler_features)
            logger.debug(f"Request ID: {request_id} - Características escaladas: {X_scaled_df.to_dict()}")
        except Exception as e:
            logger.error(f"Request ID: {request_id} - Error en RobustScaler: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Error en escalado de características: {str(e)}'}), 400

        # Seleccionar características para PCA y predicción (en el mismo orden que en entrenamiento)
        pca_features = ['Sex', 'Ticket', 'Age', 'Fare', 'Pclass', 'SibSp', 'Title', 'FamilySize']
        X_pca_input = X_scaled_df[pca_features]
        logger.debug(f"Request ID: {request_id} - Características seleccionadas para PCA: {X_pca_input.to_dict()}")

        # Aplicar PCA
        logger.debug(f"Request ID: {request_id} - Aplicando PCA")
        try:
            X_pca = pca_model.transform(X_pca_input)
            logger.debug(f"Request ID: {request_id} - PCA aplicado")
        except Exception as e:
            logger.error(f"Request ID: {request_id} - Error en PCA: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Error en transformación PCA: {str(e)}'}), 400

        # Hacer predicción
        logger.debug(f"Request ID: {request_id} - Realizando predicción")
        try:
            prediction = random_forest_model.predict(X_pca)[0]
            prediction_proba = random_forest_model.predict_proba(X_pca)[0][1]
            logger.debug(f"Request ID: {request_id} - Predicción: {prediction}, Probabilidad: {prediction_proba}")
        except Exception as e:
            logger.error(f"Request ID: {request_id} - Error en predicción: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Error en predicción: {str(e)}'}), 400

        # Preparar respuesta
        result = {
            'survived': bool(prediction),
            'probability': round(prediction_proba * 100, 1),
            'passenger_name': data['Name']
        }
        
        logger.info(f"Request ID: {request_id} - Predicción exitosa: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Request ID: {request_id} - Error en /predict: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 400

if __name__ == '__main__':
    logger.info("Iniciando la aplicación Flask")
    app.run(debug=True)