@echo off
echo 🚀 Setting up and running the Road Monitoring Project...

:: Step 1: Create Conda Environments and Install Dependencies

:: Check & Create Streamlit Environment
conda env list | findstr "streamlit_env" >nul || (
    echo 📦 Creating Streamlit environment...
    conda create --name streamlit_env python=3.10 -y && conda activate streamlit_env && pip install -r requirements_streamlit.txt
)

:: Check & Create TensorFlow Environment
conda env list | findstr "tf_env" >nul || (
    echo 📦 Creating TensorFlow API environment...
    conda create --name tf_env python=3.10 -y && conda activate tf_env && pip install -r requirements_tf.txt
)

:: Check & Create PyTorch Environment
conda env list | findstr "torch_env" >nul || (
    echo 📦 Creating PyTorch API environment...
    conda create --name torch_env python=3.10 -y && conda activate torch_env && pip install -r requirements_torch.txt
)

:: Step 2: Start Services in Separate Windows

:: Start Streamlit App on Port 8501 with 5 GB upload limit
start "Streamlit UI" cmd /k "conda activate streamlit_env && streamlit run app.py --server.port=8501 --server.maxUploadSize=50000"

:: Start TensorFlow API on Port 8001
start "TensorFlow API" cmd /k "conda activate tf_env && uvicorn models.classification_tf.api:app --host 0.0.0.0 --port 8001 --reload"

:: Start PyTorch API on Port 8002
start "PyTorch API" cmd /k "conda activate torch_env && uvicorn models.detection_pytorch.api:app --host 0.0.0.0 --port 8002 --reload"

echo ✅ All services started! Open Streamlit at http://localhost:8501
pause
