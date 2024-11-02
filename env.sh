
# Update and upgrade package lists
echo "Updating and upgrading packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.8
echo "Installing Python 3.8..."
sudo apt install -y python3.8 python3.8-venv python3.8-dev

sudo apt remove -y python3.6 python3.6-dev python3.6-venv

# Update alternatives to set python3 to python3.8
echo "Updating alternatives to set python3 to python3.8..."
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2

# Verify the default python version
echo "Verifying Python version..."
python3 --version

# Create a virtual environment named 'idenv'
echo "Creating virtual environment 'idenv'..."
python3 -m venv idenv

# Activate the virtual environment
echo "Activating the virtual environment 'idenv'..."
source idenv/bin/activate

echo "Setting RTSP stream URL..."
export RTSP_STREAM_URL="rtsp://admin:jetsonnano1@10.10.0.126:75/h265/ch1/main/av_stream"
echo "RTSP_STREAM_URL set to: $RTSP_STREAM_URL"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install specified modules
echo "Installing required modules..."
pip install coloredlogs==15.0.1 \
    Cython==3.0.11 \
    flatbuffers==24.3.25 \
    humanfriendly==10.0 \
    imageio==2.35.1 \
    lazy_loader==0.4 \
    mpmath==1.3.0 \
    networkx==3.1 \
    numpy==1.24.4 \
    onnx==1.17.0 \
    onnxruntime==1.19.2 \
    opencv-python==4.10.0.84 \
    packaging==24.1 \
    pillow==10.4.0 \
    pkg_resources==0.0.0 \
    protobuf==5.28.2 \
    PyWavelets==1.4.1 \
    scikit-image==0.21.0 \
    scipy==1.10.1 \
    sympy==1.13.3 \
    tifffile==2023.7.10


# Confirm installations
echo "Verifying installations..."
python -c "import coloredlogs, Cython, flatbuffers, humanfriendly, imageio, lazy_loader, mpmath, networkx, numpy, onnx, onnxruntime, cv2, packaging, pillow, pkg_resources, protobuf, PyWavelets, skimage, scipy, sympy, tifffile; print('All modules installed successfully.')"

echo "Script execution completed."
