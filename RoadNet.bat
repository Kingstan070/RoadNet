@echo off
echo Setting up and running the Road Monitoring Project...

:: Step 1: Create Conda Environments and Install Dependencies

:: Check & Create Streamlit Environment
conda env list | findstr "streamlit_env" >nul
if errorlevel 1 (
    echo 📦 Creating Streamlit environment...
    call conda create --name streamlit_env python=3.10 -y
    call conda activate streamlit_env
    call pip install -r requirements_streamlit.txt
) else (
    echo 📦 Streamlit environment already exists. Activating...
    call conda activate streamlit_env
)

:: Check & Create TensorFlow Environment
conda env list | findstr "tf_env" >nul
if errorlevel 1 (
    echo 📦 Creating TensorFlow API environment...
    call conda create --name tf_env python=3.10 -y
    call conda activate tf_env
    call pip install -r requirements_tf.txt
) else (
    echo 📦 TensorFlow environment already exists. Activating...
    call conda activate tf_env
)

:: Check & Create PyTorch Environment
conda env list | findstr "torch_env" >nul
if errorlevel 1 (
    echo 📦 Creating PyTorch API environment...
    call conda create --name torch_env python=3.10 -y
    call conda activate torch_env
    call pip install -r requirements_torch.txt
) else (
    echo 📦 PyTorch environment already exists. Activating...
    call conda activate torch_env
)

:: Step 2: Start Services in Separate Windows

:: Start Streamlit App on Port 8501 with 5 GB upload limit
start "Streamlit UI" cmd /k "conda activate streamlit_env && streamlit run app.py --server.port=8501 --server.maxUploadSize=50000"

:: Start TensorFlow API on Port 8001
:: For testing: conda activate tf_env && python tf_predict_test.py
start "TensorFlow API" cmd /k "conda activate tf_env && uvicorn models.classification_tf.api:app --host 0.0.0.0 --port 8001 --reload"

:: Start PyTorch API on Port 8002
start "PyTorch API" cmd /k "conda activate torch_env && uvicorn models.detection_pytorch.api:app --host 0.0.0.0 --port 8002 --reload"

echo All services started! Open Streamlit at http://localhost:8501

:wait_for_q
set /p input="Type 'q' to close all services: "
if /i "%input%"=="q" (
    taskkill /FI "WINDOWTITLE eq Streamlit UI"
    taskkill /FI "WINDOWTITLE eq TensorFlow API"
    taskkill /FI "WINDOWTITLE eq PyTorch API"
    echo All services stopped.
    exit
) else (
    goto wait_for_q
)
