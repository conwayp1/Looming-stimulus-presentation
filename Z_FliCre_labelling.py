from psychopy import visual, core, monitors
import threading
from math import tan, radians
from datetime import datetime
import cv2
import os


def record(e, path):
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

    target_size = (640, 360)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_size[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_size[1])

    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    frame_list = []

    win_name = "recording " + animal_id
    cv2.namedWindow(win_name)  # Create a named window
    cv2.moveWindow(win_name, 640, 30)  # Move it to specified location

    global timer
    global start_exp
    global stimulus_state

    arena_map = cv2.imread('map_opaque-no-shelter.png')
    alpha = 0.8

    while not e.is_set():
        ret, frame = cap.read()
        if ret:
            cv2.putText(frame, str(stimulus_state),
                        (575, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255))
            frame_list.append(frame)
            added_image = cv2.addWeighted(frame, alpha, arena_map, 1 - alpha, 0)
            frame = added_image
            cv2.imshow(win_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("\nNO VIDEO FEED!\n")
            os.system('pause')
            break
    cap.release()

    elapsed_time = (timer.getTime() - start_exp)
    fps = len(frame_list) / elapsed_time
    fourcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')

    if not os.path.exists(path):
        os.makedirs(path)
    now = datetime.now().strftime('%Y-%m-%d %H_%M_%S')
    filename = path + '\\' + animal_id + ' LOOMING EXT' + now + '.avi'
    out = cv2.VideoWriter(filename, fourcc, fps, size)
    for f in frame_list:
        out.write(f)

    out.release()
    cv2.destroyAllWindows()


def calibrate(c):
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

    target_size = (640, 360)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_size[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_size[1])

    win_name = "calibrating... "
    cv2.namedWindow(win_name)  # Create a named window
    cv2.moveWindow(win_name, 640, 30)  # Move it to specified location

    global timer
    global start_exp

    arena_map = cv2.imread('map_opaque-no-shelter.png')
    alpha = 0.8

    while not c.is_set():
        ret, frame = cap.read()
        if ret:
            cv2.putText(frame, 'CALIBRATING... ALIGN CAMERA...',
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255))
            added_image = cv2.addWeighted(frame, alpha, arena_map, 1 - alpha, 0)
            frame = added_image
            cv2.imshow(win_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("\nNO VIDEO FEED!\n")
            os.system('pause')
            break


def looming_stimulus(color, win,
                     angle_start, angle_end, distance,
                     expand_f, remain_f, pause_f):

    # Compute stimulus size in cm
    diam_start = compute_size(distance, angle_start)
    diam_end = compute_size(distance, angle_end)
    increment = (diam_end - diam_start) / (expand_f - 1) / 2

    # to set random position
    # rand_x = rand_float(size_max/2, width - size_max/2)
    # rand_y = rand_float(size_max/2, height - size_max/2)
    # disk = visual.Circle(win, units='cm', fillColor=color, lineColor=color, radius=diam_start / 2, pos=(rand_x, rand_y))

    disk = visual.Circle(win, units='cm', fillColor=color, lineColor=color, radius=diam_start / 2, pos=(-0.2*width, 0))

    # Expand disk from size_min to size_max in ms_expand
    for frame_e in range(1, expand_f + 1):
        disk.draw()
        win.flip()
        disk.radius += increment
    disk.radius -= increment
    # Let disk remain on screen for ms_remain
    for frame_r in range(1, remain_f):  # minus one frame, already present at the end of expansion
        disk.draw()
        win.flip()
        # print "staying, radius=", disk.radius

    # Present white screen before next stimulus
    for frame_p in range(1, pause_f + 1):
        win.flip()


def compute_size(distance, visual_angle):
    size = 2 * float(distance) * tan(radians(float(visual_angle)) / 2)
    return size


if __name__ == '__main__':
    # # # # # # # # # # # # # # # # # # # LOOMING # # # # # # # # # # # # # # # # # # #
    #
    # This script present 'looming' stimuli according to set visuals
    # and timing parameters (first paper: Yilmaz & Meister, 2013).
    #

    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

    # # # # You can change the values (but not names) of the following parameters # # # #

    # File parameters
    save_destination = r'Videos'

    # Timing parameters
    min_acclimation = 5  # Number of minutes the animal is left is in the arena before stimuli are presented
    ms_expand = 250  # Number of milliseconds during which the disk expands
    ms_remain = 250  # Number of milliseconds during which the disk remains on screen at full size
    ms_pause = 500  # Number of milliseconds between stimuli presentations
    numStimuli = 15  # Number of stimuli per wave
    numWaves = 1  # Number of stimuli waves
    min_rest = 1  # Number of minutes the animal is left is in the arena after stimuli are presented

    # Manual/auto settings
    manual_mode = False

    # Visual parameters
    bkgd_color = 1  # Color of the background
    disk_color = -1  # Color of the disk

    angle_ini = 2  # Initial size of the disk
    angle_fin = 40  # Final size of the disk

    dist = 30  # Distance between the screen and the animal
    dens = 35.5  # Pixel density of the screen, unit must be coherent with dist

    width = 47.376  # width of the screen in cm
    resolution = [1680, 1050]  # size of the screen in pixels

    # # # # # DO NOT CHANGE ANYTHING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING # # # # #

    # Screen settings
    mon = monitors.Monitor(name='Dell P2217', width=width, distance=dist)
    mon.setSizePix(resolution)
    window = visual.Window(screen=1, monitor=mon, color=bkgd_color, size=resolution, fullscr=True,
                           units='pix', checkTiming=True)
    ifi = window.monitorFramePeriod

    # Compute timings in appropriate units
    s_acclimation = min_acclimation * 60.0
    s_rest = min_rest * 60.0
    s_expand = ms_expand / 1000.0
    frames_expand = int(round(s_expand / ifi))
    s_remain = ms_remain / 1000.0
    frames_remain = int(round(s_remain / ifi))
    s_pause = ms_pause / 1000.0
    frames_pause = int(round(s_pause / ifi))
    wait_frames = 1

    # Initialize screen
    window.flip()

    # # Start calibrating
    calibrated_event = threading.Event()
    thread1 = threading.Thread(target=calibrate, args=(calibrated_event,))
    thread1.start()

    if not manual_mode:
        print("\nWARNING: auto mode is set!")
    animal_id = str(input("\nAnimal ID (experiment will start immediately): "))

    # Stop calibrating
    calibrated_event.set()
    thread1.join()

    # Start timer and initialise stimulus state
    timer = core.Clock()
    start_exp = timer.getTime()
    stimulus_state = 'OFF'

    # Start recording
    stop_event = threading.Event()
    thread = threading.Thread(target=record, args=(stop_event, save_destination,))
    thread.start()

    # Wait for acclimation
    print("\nAcclimation period started.")
    core.wait(s_acclimation)

    if manual_mode:
        print("\nAcclimation period ended. Ready to present stimulus.")
        os.system('pause')  # event.waitKeys()

    # Present stimuli
    for wave in range(1, numWaves + 1):
        start_stim = timer.getTime()
        start_stim = start_stim - start_exp
        stimulus_state = 'ON'
        if numWaves > 1:
            print("\nWave #%d" % wave)
        print("\nStimulus started at %f s" % start_stim)
        for stimulus in range(1, numStimuli + 1):
            start_stim = timer.getTime()
            print("Presentation #%d" % stimulus)
            looming_stimulus(disk_color, window,
                             angle_ini, angle_fin, dist,
                             frames_expand, frames_remain, frames_pause)
            end_stim = timer.getTime()
            duration = end_stim - start_stim
            print("%f s\n" % duration)
        stimulus_state = 'OFF'

        # Wait before ending experiment
        print("\nAll stimuli presented. Resting period started.")
        core.wait(s_rest)

    # Stop recording
    stop_event.set()
    thread.join()

    # print("\nResting period ended. Stopping experiment.")
    print("\nResting period ended. Ready to end experiment with animal " + animal_id + ".")
    os.system('pause')  # event.waitKeys()
