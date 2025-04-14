# Quantum String Matching Demo

## Introduction

This demo showcases a **quantum string matching algorithm**, designed to identify whether a given substring exists within a larger string using principles from quantum computing. It serves as a basic illustration of how quantum parallelism and interference can be leveraged to accelerate string search problems compared to classical approaches.

The algorithm is implemented using **Qiskit**, a Python-based framework for quantum computing. While this version is simulated on a classical backend, it lays the groundwork for future deployment on real quantum hardware.

## Qiskit 

Qiskit is an open source software development kit for quantum computing. It allows users to create and run quantum programs on simulators or quantum hardware. Qiskit has been undergoing rapid developmental changes due to developments in teh field of quantum computing.

Qiskit underwent breaking changes as it switched from its older Qiskit 0.46 version to Qiskit 1.0 in 2024. Most of the commands and packages used look different and the older codes are not at all compatible with the new version. For Demo 1, we will be using Qiskit 1.0 and the Qiskit Runtime service, which allows us to execute quantum computations on IBM quantum hardware. For Demo 2, we will be using the older Qiskit 0.45.0, along with the corresponding older packages.

## Demo 1
This ia a demo of the Grover's algorithm, taken from 

## Demo 2

To run the string matching demo, ensure you have the python installed. Create a virtual environment, activate it and install required Qiskit dependencies. The string matching demo requires the older version of qiskit.

```
python -m venv qiskit_env
qiskit_env\Scripts\activate
pip install qiskit==0.45.0
pip install qiskit-aer==0.13.2
pip install ibm-cloud-sdk-core==3.18.2
```
To ensure the correct versions have been installed, run

```
python -c "import qiskit; print(qiskit.__qiskit_version__)"
```
We also require the following to visualise our results:

```
pip install matplotlib
pip install 'qiskit[visualization]'
```
Now you can run the script _stringmatchingdemo.py_ in this virtual environment.



