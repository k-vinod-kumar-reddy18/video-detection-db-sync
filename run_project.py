import subprocess
import time


PYTHON = r".\venv\Scripts\python.exe"

processes = []


try:

    # --------------------------------------------------
    # 1. START FASTAPI
    # --------------------------------------------------

    print("Starting FastAPI...")

    fastapi_process = subprocess.Popen([
        PYTHON,
        "-m",
        "uvicorn",
        "main:app",
        "--port",
        "8001"
    ])

    processes.append(fastapi_process)

    time.sleep(5)


    # --------------------------------------------------
    # 2. START DJANGO
    # --------------------------------------------------

    print("Starting Django...")

    django_process = subprocess.Popen([
        PYTHON,
        "manage.py",
        "runserver",
        "8000",
        "--noreload"
    ])

    processes.append(django_process)

    time.sleep(5)


    print()
    print("===================================")
    print("FastAPI and Django are running")
    print("===================================")
    print("FastAPI : http://127.0.0.1:8001")
    print("Django  : http://127.0.0.1:8000")
    print("===================================")


    # --------------------------------------------------
    # 3. VIDEO PROCESSING
    # --------------------------------------------------

    while True:

        video_path = input(
            "\nEnter video path (or type 'exit' to stop videos): "
        ).strip()


        # Stop entering videos
        if video_path.lower() == "exit":

            print()
            print("No more videos.")
            break


        # Empty input
        if not video_path:

            print("Please enter a video path.")
            continue


        print()
        print("===================================")
        print("Starting YOLO video processing")
        print("===================================")
        print("Video:", video_path)
        print()


        # --------------------------------------------------
        # 4. RUN YOLO
        # --------------------------------------------------

        yolo_process = subprocess.run([
            PYTHON,
            "test_yolo.py",
            video_path
        ])


        # --------------------------------------------------
        # 5. CHECK YOLO RESULT
        # --------------------------------------------------

        if yolo_process.returncode == 0:

            print()
            print("===================================")
            print("Video processing completed")
            print("===================================")

        else:

            print()
            print("===================================")
            print("Video processing failed")
            print("===================================")


        print()
        print("Enter another video path or type 'exit'.")


    # --------------------------------------------------
    # 6. START TIMER AFTER ALL VIDEO PROCESSING
    # --------------------------------------------------

    print()
    print("Starting synchronization timer...")

    timer_process = subprocess.Popen([
        PYTHON,
        "timer.py"
    ])

    processes.append(timer_process)


    print()
    print("===================================")
    print("Synchronization system is running")
    print("===================================")
    print("Sync interval : 2 minutes")
    print("Cleanup       : After 2 hours")
    print()
    print("PostgreSQL -> MongoDB")
    print()
    print("Press Ctrl+C to stop everything.")


    # --------------------------------------------------
    # 7. KEEP PROJECT RUNNING
    # --------------------------------------------------

    while True:
        time.sleep(1)


except KeyboardInterrupt:

    print()
    print("Stopping all services...")


finally:

    # Stop FastAPI, Django and Timer
    for process in processes:

        if process.poll() is None:
            process.terminate()


    print("All services stopped.")