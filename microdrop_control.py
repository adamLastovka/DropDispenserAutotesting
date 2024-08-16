import serial
import time

def read_all(port, chunk_size=1):
    """Read all characters on the serial port and return them."""
    if not port.timeout:
        raise TypeError('Port needs to have a timeout set!')

    read_buffer = b''

    while True:
        # Read in chunks. Each chunk will wait as long as specified by
        # timeout. Increase chunk_size to fail quicker
        byte_chunk = port.read(size=chunk_size)
        read_buffer += byte_chunk
        if not len(byte_chunk) == chunk_size:
            break

    print(read_buffer.decode('utf-8'))
    return read_buffer

def wait_for_log(port):
    log = port.readline().decode('utf-8').strip()

    while not log:
        log = port.readline().decode('utf-8').strip()

    print(log)
    return log

if __name__ == "__main__":
    END = '\n\r'
    OK = 'OK'

    dispenser = serial.Serial('COM7', 115200, timeout=1.5)

    # t0 = time.perf_counter()
    # dispenser.write(bytes("TRIGGER:ASET:65,2,30,65,100,50,1" + END, 'utf-8'))
    # log = wait_for_log(dispenser)
    # t1 = time.perf_counter()
    #
    # dispenser.write(bytes("TRIGGER:ASET:?"+END, 'utf-8'))
    # log = wait_for_log(dispenser)
    # t2 = time.perf_counter()

    t1 = time.perf_counter()
    dispenser.write(bytes("VALVE:AOPEN:65,2,30,65,100,50" + END, 'utf-8'))
    log = wait_for_log(dispenser)
    t3 = time.perf_counter()

    print(f"dt1: {t3-t1}")

    time.sleep(2)

    # t0 = time.perf_counter()
    # dispenser.write(bytes("TRIGGER:ASET:60,2,30,65,100,50,1" + END, 'utf-8'))
    # t1 = time.perf_counter()
    #
    # dispenser.write(bytes("TRIGGER:ASET:?" + END, 'utf-8'))
    # t2 = time.perf_counter()
    #
    # dispenser.write(bytes("VALVE:OPEN" + END, 'utf-8'))
    # t3 = time.perf_counter()
    #
    # print(f"dt1: {t1 - t0},dt2: {t2 - t1},dt1: {t3 - t2}")


