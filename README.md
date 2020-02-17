# Webcam-Emotion-Detection
This is based entirely on [atulapra's](https://github.com/atulapra) [Emotion-detection-repo](https://github.com/atulapra/Emotion-detection). Forked to this repo since for easier dependency management for use in FabLab projects.
## Setup
Start off by cloning the repo:
```
git clone https://github.com/faaip/Emotion-detection
cd Emotion-detection
```
We need to have openCV installed, which has quite a few dependencies for the Raspberry Pi. You can install these using the supplied script:
```
sh install_opencv_dependencies.sh

```
If you later run into problems with the openCV installation, you can follow this [guide](https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/) instead.

Initialize the virtual environment:
```
virtualenv venv -p python3
```
Activate the virtual environment:
```
source venv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Download [atulapra's](https://github.com/atulapra) pre-trained model. Using the download script:
```
sh download-model.sh
```

Run program:
```
python run.py
```
## Options
To run in full screen:
```
python run.py --fullscreen
```
To show debug info:
```
python run.py --debug
```
## References
* [atulapra's](https://github.com/atulapra) [Emotion-detection-repo](https://github.com/atulapra/Emotion-detection).
* "Challenges in Representation Learning: A report on three machine learning contests." I Goodfellow, D Erhan, PL Carrier, A Courville, M Mirza, B
   Hamner, W Cukierski, Y Tang, DH Lee, Y Zhou, C Ramaiah, F Feng, R Li,  
   X Wang, D Athanasakis, J Shawe-Taylor, M Milakov, J Park, R Ionescu,
   M Popescu, C Grozea, J Bergstra, J Xie, L Romaszko, B Xu, Z Chuang, and
   Y. Bengio. arXiv 2013.