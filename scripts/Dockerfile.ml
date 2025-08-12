FROM freqtradeorg/freqtrade:stable

# Instalar dependências ML
USER root
RUN pip install --no-cache-dir \
    scikit-learn==1.3.0 \
    pandas==1.5.3 \
    numpy==1.24.3 \
    joblib==1.3.2

# Voltar para usuário freqtrade
USER freqtrade

# Criar diretório para modelos ML
RUN mkdir -p /freqtrade/user_data/ml_models

WORKDIR /freqtrade
