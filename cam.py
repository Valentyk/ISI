from pypylon import pylon
from pypylon import genicam
import matplotlib.pyplot as plt
import cv2
import time

###################################################################

def save_images(img):
    for i in range(len(img)):
        cv2.imwrite(f"C:/Users/User/Desktop/Piezo_particles/2023/code/camera/image_{i + 1}.png", img[i])
        
def video_from_images(img, output_file, fps):
    
    height, width = img[0].shape
    out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height), False)
    
    for i in range(len(img)):
        out.write(img[i])
        
    out.release()

def camera_capture(img, num_of_frames):

    tl_factory = pylon.TlFactory.GetInstance()
    camera = pylon.InstantCamera()
    camera.Attach(tl_factory.CreateFirstDevice())

    camera.Open()
    camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
    i = 0
    print('Starting to acquire')
    t0 = time.time()
    while camera.IsGrabbing():
        grab = camera.RetrieveResult(100, pylon.TimeoutHandling_ThrowException)
        if grab.GrabSucceeded():
            i += 1
            img.append(grab.Array)
        if i == num_of_frames or i > num_of_frames:
            break

    print(f'Acquired {i} frames in {time.time()-t0:.2f} seconds')
    camera.Close()
    return(img)

if __name__ == "__main__":
    num_of_frames = 200
    image = []
    
    img = camera_capture(image, num_of_frames)
    video_from_images(img, "C:/Users/User/Desktop/Piezo_Valentík/2023/Piezo_particles/2023/data/pure_data/video.mp4", 30)