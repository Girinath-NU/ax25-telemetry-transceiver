import subprocess
import threading

while True:

    msg = input("\nMessage (or 'veliya vaa'): ")

    if msg.lower() == "veliya vaa":
        print("Goodbye!")
        break

    # Generate packet.wav
    subprocess.run(
        ["python3", "encoder.py", msg],
        check=True
    )

    print("\nStarting transmitter...")

    tx = subprocess.Popen(
        ["python3", "ax25_tx.py"]
    )

    print("Type 'exit' to stop transmitting")

    while True:

        cmd = input("> ")

        if cmd.lower() == "exit":

            print("Stopping transmitter...")

            tx.terminate()

            try:
                tx.wait(timeout=3)
            except:
                tx.kill()

            break

        elif cmd.lower() == "veliya vaa":

            print("Stopping transmitter...")

            tx.terminate()

            try:
                tx.wait(timeout=3)
            except:
                tx.kill()

            print("Goodbye!")
            exit()
