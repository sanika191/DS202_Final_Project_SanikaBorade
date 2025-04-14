from numpy import log2, sqrt
from numpy import pi

from qiskit.tools.visualization import plot_histogram
from qiskit.circuit.gate import Gate
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer
from qiskit import transpile

def run(circuit: QuantumCircuit, shots: int) -> dict:
    simulator = Aer.get_backend('aer_simulator')
    compiled_circuit = transpile(circuit, simulator)
    job = simulator.run(compiled_circuit, shots=shots)
    result = job.result()
    return result.get_counts(compiled_circuit)

def init_register(bin_str: str) -> QuantumCircuit:
    data_qr = QuantumRegister(len(bin_str), 'data')
    qc = QuantumCircuit(data_qr)

    for i, bit in enumerate(bin_str):
        if bit == '1':
            qc.x(data_qr[i])

    return qc
    
#classical_value = '1001'
#print(init_register(classical_value).draw(fold=255))

def rot(n: int, s: int) -> QuantumCircuit:
    y_qr = QuantumRegister(n, 'y')
    qc = QuantumCircuit(y_qr, name='ROT_' + str(s))

    for i in range(1, (int(log2(n)) - int(log2(s)) + 2)):
        for j in range(int(n / (s * (2**i)))):
            for q in range(j * s * (2**i), s * (j*2 ** i+1)):
                qc.swap(n - 1 - (q+s), n - 1 - (q+2 ** (i-1) * s + s))

    return qc

#num_qubits = 8
#shift_value = 2
#print(rot(num_qubits, shift_value).draw(fold=255))


def rot_gate(n: int, s: int) -> Gate:
    rot_circuit = rot(n, s)
    return rot_circuit.to_gate(label='ROT_' + str(s))


def parameterized_rot(n: int) -> QuantumCircuit:
    j_qr = QuantumRegister(int(log2(n)), 'j')
    y_qr = QuantumRegister(n, 'y')
    qc = QuantumCircuit(j_qr, y_qr)

    for i in range(int(log2(n))):
        crot = rot_gate(n, 2**i).control(1)
        qc = qc.compose(crot, [j_qr[i]] + y_qr[:])

    return qc


#num_qubits = 8
#print(parameterized_rot(num_qubits).draw(fold=255))

"""
text = '10110001'
text_length = len(text)

shift_qr = QuantumRegister(int(log2(text_length)), 'shift')
text_qr = QuantumRegister(text_length, 'text')
output_cr = ClassicalRegister(text_length, 'output_classic')
circ = QuantumCircuit(shift_qr, text_qr, output_cr)

circ.h(shift_qr)
circ.append(init_register(text), text_qr[:])
circ.append(parameterized_rot(text_length), shift_qr[:] + text_qr[:])
circ.measure(text_qr, output_cr)

counts = run(circ, 100)
plot_histogram(counts, title='Rotate ' + text + ' Leftward in Superposition')
"""

def match(m: int) -> QuantumCircuit:
    x_qr = QuantumRegister(m, 'x')
    y_qr = QuantumRegister(m, 'y')
    out_qr = QuantumRegister(1, 'out')
    qc = QuantumCircuit(x_qr, y_qr, out_qr)

    for i in range(m):
        qc.cx(x_qr[i], y_qr[i])
        qc.x(y_qr[i])

    qc.mcx(y_qr[:], out_qr)

    for i in reversed(range(m)):
        qc.x(y_qr[i])
        qc.cx(x_qr[i], y_qr[i])

    return qc

"""
#pattern_length = 4
#print(match(pattern_length).draw(fold=255))


text = '1011'
text_length = len(text)

pattern_qr = QuantumRegister(text_length, 'pattern')
text_qr = QuantumRegister(text_length, 'text')
output_qr = QuantumRegister(1, 'output')
output_cr = ClassicalRegister(text_length + 1, 'output_classic')
circ = QuantumCircuit(pattern_qr, text_qr, output_qr, output_cr)

circ.h(pattern_qr)
circ.append(init_register(text), text_qr[:])
circ.append(match(text_length), pattern_qr[:] + text_qr[:] + output_qr[:])
circ.measure(pattern_qr, output_cr[:-1])
circ.measure(output_qr, output_cr[-1])

counts = run(circ, 100)
plot_histogram(counts, title='Matching ' + text)
"""

def match_gate(m: int) -> Gate:
    match_circuit = match(m)
    return match_circuit.to_gate(label='MATCH')


def esm(m: int, n: int) -> QuantumCircuit:
    j_qr = QuantumRegister(int(log2(n)), 'j')
    x_qr = QuantumRegister(m, 'x')
    y_qr = QuantumRegister(n, 'y')
    out = QuantumRegister(1, 'out')

    qc = QuantumCircuit(
        j_qr,
        x_qr,
        y_qr,
        out
    )

    qc = qc.compose(parameterized_rot(n), j_qr[:] + y_qr[:])
    qc = qc.compose(match_gate(m), x_qr[:] + y_qr[:m] + out[:])
    qc = qc.compose(parameterized_rot(n).inverse(), j_qr[:] + y_qr[:])

    return qc


#pattern_length = 2
#text_length = 8
#print(esm(pattern_length, text_length).draw(fold=255))

def esm_oracle(m: int, n: int):
    esm_circuit = esm(m, n)
    return esm_circuit.to_gate(label='ESMO')

def diffuser(n: int) -> Gate:
    qc = QuantumCircuit(n)

    qc.h(range(n))
    qc.x(range(n))

    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)

    qc.x(range(n))
    qc.h(range(n))

    return qc.to_gate(label='DIFF')

def grover(esmo: Gate, t: int, x: str, y: str) -> QuantumCircuit:
    n = len(y)
    m = len(x)
    logn = int(log2(n))
    num_iterations = int(pi/4 * sqrt(n/t))

    j_qr = QuantumRegister(logn, 'j')
    x_qr = QuantumRegister(m, 'x')
    y_qr = QuantumRegister(n, 'y')
    out_qr = QuantumRegister(2, 'out')
    out_cr = ClassicalRegister(logn+1, 'c')
    qc = QuantumCircuit(j_qr, x_qr, y_qr, out_qr, out_cr)

    qc.h(j_qr)
    qc.x(out_qr[0])
    qc.h(out_qr[0])

    qc = qc.compose(init_register(x), x_qr[:])
    qc = qc.compose(init_register(y), y_qr[:])

    for _ in range(num_iterations):
        qc = qc.compose(esmo)
        qc = qc.compose(diffuser(logn))

    qc.measure(j_qr, out_cr[:-1])
    qc = qc.compose(esmo, j_qr[:] + x_qr[:] + y_qr[:] + [out_qr[1]])
    qc.measure(out_qr[1], out_cr[-1])

    return qc

#x = '11'
#y = '10101100'
#esmo = esm_oracle(len(x), len(y))
#print(grover(esmo, 1, x, y).draw(fold=255))

"""
x = '00'
y = '01010101'
esmo = esm_oracle(len(x), len(y))
counts = run(grover(esmo, 1, x, y), 100)
plot_histogram(counts, title=f'Search for {x} in {y} - 0 occurrence(s)')

x = '00'
y = '00111001'
esmo = esm_oracle(len(x), len(y))
counts = run(grover(esmo, 2, x, y), 100)
plot_histogram(counts, title=f'Search for {x} in {y} - 2 occurrence(s)')

x = '00'
y = '11010011'
esmo = esm_oracle(len(x), len(y))
counts = run(grover(esmo, 1, x, y), 100)
plot_histogram(counts, title=f'Search for {x} in {y} - 1 occurrence(s)')
"""




#import matplotlib.pyplot as plt
#plt.show()

def search(x: str, y: str) -> int:
    m = len(x)
    n = len(y)
    esmo = esm_oracle(m, n)

    for t in range(1, int(n/2) + 1):
        print('Trying with t =', t)
        results = run(grover(esmo, t, x, y), 100)
        plot_histogram(results, title=f'Search for {x} in {y}')
        results = list(results.keys())[0]
        outcome = int(results[0])
        position = int(results[1:], 2)

        if outcome: return position
        else: print('Pattern not found in position', position)

    return -1

x = input('Enter the value of x: ')
y = input('Enter the value of y: ')

if len(x) > len(y):
    raise ValueError('The length of x must be shorter than the length of y.')

if not all(c in '01' for c in x):
    raise ValueError('The pattern must be a binary string.')

if not all(c in '01' for c in y):
    raise ValueError('The text must be a binary string.')

print('')
position = search(x, y)

import matplotlib.pyplot as plt
plt.show()

if position >= 0: print('Pattern occurrence found in position', str(position))
else: print('Pattern occurrence not found.')


