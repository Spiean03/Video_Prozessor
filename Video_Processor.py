import spinmob.egg as _egg
import cv2 as _cv2
import time as _t
import numpy as _n
#import egg

"""
To do: when changing the video input source field, change the stream!
"""


###############################
# Basic classes and functions
###############################

def image_to_rgb_data(image): 
    """
    Converts the array from cv2 to an array of data for our plotter.
    """
    return image.transpose((1,0,2)).astype(float)


def data_to_image(image, rescale=False):
    """
    Converts our plotty data to an image array for cv2.
    """    
    if rescale: 
        imax = max(image)
        imin = min(image)        
        return ((image.transpose((1,0)) - imin) * 256.0/(imax-imin)).astype(int) 
    else: 
        return image.transpose((1,0)).astype(int)

class ImageWithButtons(_egg.gui.GridLayout):
    
    def __init__(self, window):
        """
        This object is a grid layout containing an image with save / load 
        buttons.
        
        You must supply a window object so that it can connect buttons to 
        actions, etc.
        """

        # initialize the grid layout
        _egg.gui.GridLayout.__init__(self)    
        
        # no need for more margins
        self._layout.setContentsMargins(0,0,0,0)

        # store the window object
        self._window = window

        # add the save, load, and image
        self.button_save = self.place_object(_egg.gui.Button("Save"))
        self.button_load = self.place_object(_egg.gui.Button("Load"))
        self.image       = self.place_object(_egg.pyqtgraph.ImageView(), 0,1, column_span=3, alignment=0)
       
        
        # sha-clacky the buttons together
        self.set_column_stretch(2,10)        
        
        # data
        self.data = 0.0
        

        # connect the buttons to the functionality
        self._window.connect(self.button_save.signal_clicked, self.button_save_clicked)
        self._window.connect(self.button_load.signal_clicked, self.button_load_clicked)
        
    def set_data(self, data, **kwargs):
        """
        Sets the image view data to the supplied array.
        """
        self.image.setImage(data, **kwargs)
        self.data = data
        
    def set_levels(self, minvalue, maxvalue, minlevel, maxlevel):
        """
        Sets the minimum and maximum values of the histogram as well as the levelbars. 
        """
        self.image.setLevels(minlevel, maxlevel)
        self.image.ui.histogram.setHistogramRange(minvalue, maxvalue)
    
    def save_image(self, path="ask"):
        """
        Saves the image.
        """
        # get a valid path
        if path=="ask": path = _egg.dialogs.save("*.png")
        if not path: return

        # save the image
        _cv2.imwrite(path, data_to_image(self.image.image))
    
    def button_save_clicked(self, *a): self.save_image()

    def load_image(self, path="ask"):
        """
        Loads an image.
        """
        # get a path
        if path=="ask": path = _egg.dialogs.open_single("*.png")
        if not path: return
        
        # load the image
        rgb = image_to_rgb_data(_cv2.imread(path))
    
        # assume r+g+b / 3 by default.
        self.set_data((rgb[:,:,0]+rgb[:,:,1]+rgb[:,:,2]) / 3.0)

    def button_load_clicked(self, *a): self.load_image()

#######################
# GUI 
#######################

# main window
window = _egg.gui.Window('Image Processing', [1000,500]).set_position()



# top row for global controls
top_row       = window.place_object(_egg.gui.GridLayout()                        )
button_stream = top_row.place_object(_egg.gui.Button("Stream").set_checkable(True))
text_script   = top_row.place_object(_egg.gui.TextBox("(r+g+b)/3.0")              )
label_fps     = top_row.place_object(_egg.gui.Label("FPS = 0"), alignment=2       )
number_averages      = top_row.place_object(_egg.gui.NumberBox(20, 1, [1,None], True),  alignment=1).set_width(50)
label_average_count  = top_row.place_object(_egg.gui.Label("Averages"),                 alignment=1)



# tabs
tabs = window.place_object(_egg.gui.TabArea(False), 0,1, alignment=0)


# zero'th tab for raw stream
tab0 = tabs.add_tab("Raw Stream")

# first row: controls
tab0_row1 = tab0.place_object(_egg.gui.GridLayout())
tab0_row1.set_column_stretch(2)
video_input_tab0 = tab0_row1.place_object(_egg.gui.NumberBox(0, 1).set_width(40))
label_channel_tab0 = tab0_row1.place_object(_egg.gui.Label('Input channel'))

# second row: images
tab0_row2 = tab0.place_object(_egg.gui.GridLayout(), 0,1, alignment=0)
image_raw = tab0_row2.place_object(ImageWithButtons(window), alignment=0)



# first tab for reference and subtraction images
tab1 = tabs.add_tab("Real-Time Subtraction")

# first row: controls
tab1_row1 = tab1.place_object(_egg.gui.GridLayout())
tab1_row1.set_column_stretch(2)
button_get_reference = tab1_row1.place_object(_egg.gui.Button("Capture Reference", True), alignment=1)
video_input_tab1   = tab1_row1.place_object(_egg.gui.NumberBox(0, 1).set_width(40))
label_channel_tab1 = tab1_row1.place_object(_egg.gui.Label('Input channel'))

# second row: images and buttons
tab1_row2 = tab1.place_object(_egg.gui.GridLayout(), 0,1, alignment=0)
image_reference  = tab1_row2.place_object(ImageWithButtons(window), alignment=0)
image_subtracted = tab1_row2.place_object(ImageWithButtons(window), alignment=0)
deviation_plot =tab1_row2.place_object(_egg.pyqtgraph.PlotWidget(), alignment=0)

# second tab for subtraction and deviation images
tab2 = tabs.add_tab("Fine alignment")

#first row: controls
tab2_row1 = tab2.place_object(_egg.gui.GridLayout())
tab2_row1.set_column_stretch(2)
video_input_tab2   = tab2_row1.place_object(_egg.gui.NumberBox(0, 1).set_width(40))
label_channel_tab2 = tab2_row1.place_object(_egg.gui.Label('Input channel'))
zoom_input =tab2_row1.place_object(_egg.gui.NumberBox(30, 1).set_width(40))
label_zoom = tab2_row1.place_object(_egg.gui.Label('Zoom value'))
average_number = tab2_row1.place_object(_egg.gui.NumberBox(15, 1).set_width(40))
label_zoom = tab2_row1.place_object(_egg.gui.Label('Average value'))

# second row: images and buttons
tab2_row2 = tab2.place_object(_egg.gui.GridLayout(), 0,1, alignment=0)
image_subtracted2 = tab2_row2.place_object(ImageWithButtons(window), alignment=0)
deviation_plot2 =tab2_row2.place_object(_egg.pyqtgraph.PlotWidget(), alignment=0)




# third tab for reference and deviation images
tab3 = tabs.add_tab("Sidecam")

#first row: controls
tab3_row1 = tab3.place_object(_egg.gui.GridLayout())
tab3_row1.set_column_stretch(2)
button_get_reference_3 = tab3_row1.place_object(_egg.gui.Button("Capture Reference", True), alignment=1)
number_averages_3      = tab3_row1.place_object(_egg.gui.NumberBox(20, 1, [1,None], True),  alignment=1).set_width(50)
video_input_tab3   = tab3_row1.place_object(_egg.gui.NumberBox(0, 1).set_width(40))
label_channel_tab3 = tab3_row1.place_object(_egg.gui.Label('Input channel'))

# second row: images and buttons

tab3_row2 = tab3.place_object(_egg.gui.GridLayout(), 0,1, alignment=0)
image_reference_tab3  = tab3_row2.place_object(ImageWithButtons(window), alignment=0)
image_subtracted_tab3 = tab3_row2.place_object(ImageWithButtons(window), alignment=0)

# fourth tab for reference and deviation images
tab4 = tabs.add_tab("Topcam")

#first row: controls
tab4_row1 = tab4.place_object(_egg.gui.GridLayout())
tab4_row1.set_column_stretch(2)
button_get_reference_4 = tab4_row1.place_object(_egg.gui.Button("Capture Reference", True), alignment=1)
number_averages_4      = tab4_row1.place_object(_egg.gui.NumberBox(20, 1, [1,None], True),  alignment=1).set_width(50)
video_input_tab4   = tab4_row1.place_object(_egg.gui.NumberBox(0, 1).set_width(40))
label_channel_tab4 = tab4_row1.place_object(_egg.gui.Label('Input channel'))

# second row: images and buttons

tab4_row2 = tab4.place_object(_egg.gui.GridLayout(), 0,1, alignment=0)
image_reference_tab4  = tab4_row2.place_object(ImageWithButtons(window), alignment=0)
image_subtracted_tab4 = tab4_row2.place_object(ImageWithButtons(window), alignment=0)


# Create a databox to hold the std. variance data we acquire
databox = _egg.gui.DataboxPlot()



#######################
# Functionality
#######################

def button_get_reference_clicked(*a):
    '''
    Called when the capture reference button is pressed.
    '''

    # let the loop stop itself if we're unchecking
    if not button_get_reference.is_checked() and not button_get_reference_3.is_checked() and not button_get_reference_4.is_checked() : return

    # disable other streamers
    button_stream.disable()
    
    # get the camera input we want to use
    if   tabs.get_current_tab() == 0: 
        channel = int(video_input_tab0.get_value())
        
    elif tabs.get_current_tab() == 1:
        channel = int(video_input_tab1.get_value())
        
    elif tabs.get_current_tab() == 2:
        channel = int(video_input_tab2.get_value())
        
    elif tabs.get_current_tab() == 3:
        channel = int(video_input_tab3.get_value())
        
    elif tabs.get_current_tab() == 4:
        channel = int(video_input_tab4.get_value())
        
    else:
        print "Something went really wrong when I tried to get the video input"
    
    # connect to the camera
    camera = _cv2.VideoCapture(channel)

        
    # capture loop (we want successful captures, which is why 
    # this isn't a for loop)
    n = 0
    average = 0.0
    while n < number_averages.get_value():
        
        # get an image
        success, image = camera.read()
        
        # if we got an image, go for it.        
        if success:
            
            # process the image
            image = image_to_rgb_data(image)
            
            # globals for eval script            
            g = _n.__dict__            
            g.update(dict(r=image[:,:,0],
                          g=image[:,:,1],
                          b=image[:,:,2]))

            # the try/except thing here prevents a bad script from
            # pooping out the program. 
            try:
                # get the plot data based on the script
                data = eval(text_script.get_text(), g)
                
                # update the average
                if n==0: average = data
                else:    average = (1.0*average*n + data)/(n+1)
                
                # update the reference image
                if  tabs.get_current_tab() == 0: 
                    image_reference.set_data(average)
                    
                elif tabs.get_current_tab() == 1:
                    image_reference.set_data(average)
                    
                elif tabs.get_current_tab() == 2:
                    image_reference.set_data(average)
                    
                elif tabs.get_current_tab() == 3:
                    image_reference_tab3.set_data(average)
                    
                elif tabs.get_current_tab() == 4:
                    image_reference_tab4.set_data(average)

                # update the count
                n += 1
                label_average_count.set_text(str(n)+" Averages")
                


            # If the script pooped. Quietly do nothing. The 
            # script box should be pink already
            except: pass                
        
        # process GUI events so it doesn't freeze
        window.process_events()        
        
        # break if we manually unchecked the button
        if not button_get_reference.set_checked(): break
        if not button_get_reference_3.set_checked(): break
        if not button_get_reference_4.set_checked(): break
    
    # release the camera
    camera.release()
    
    # uncheck the button`
    button_get_reference.set_checked(False)    
    button_get_reference_3.set_checked(False)
    button_get_reference_4.set_checked(False)
    
    # enable other camera stuff
    button_stream.enable()
    
    return

# connect the signal to the function
window.connect(button_get_reference.signal_clicked, button_get_reference_clicked)
window.connect(button_get_reference_3.signal_clicked, button_get_reference_clicked)
window.connect(button_get_reference_4.signal_clicked, button_get_reference_clicked)


def text_script_changed(*a):
    '''
    Called whenever we change the script.
    '''
    g = _n.__dict__
    g.update(dict(r=1.0, g=1.0, b=1.0))
    
    try:
        eval(text_script.get_text(), g)
        text_script.set_colors('black','white')
    except: 
        text_script.set_colors('black','pink')

# connect the signal to the function
window.connect(text_script.signal_changed, text_script_changed)



def button_stream_pressed(*a):
    '''
    Called whenever the stream button is pressed.
    '''
        
    # let the loop shut itself down
    if not button_stream.is_checked(): return
    
    # disable other camera business
    button_get_reference.disable() 
    button_get_reference_3.disable()
    button_get_reference_4.disable()
    
    #Initialize the camera to input 0, need the camera object later on
    channel = 0
    camera = _cv2.VideoCapture(channel)
#    return1= camera.set(_cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
#    return2 = camera.set(_cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 1024)
#    print return1
#    print return2
#    print camera.get(_cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
#    print camera.get(_cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    
    #Make sure that we always pick a tab number which is higher than the values we actually have.
    #Needed s.t. we always get the correct video input for the tab we look at.
    tab = 100
    
    # for the frames per second calculation    
    t0 = _t.time()
    n  = 0
    
    # for the update of the histogram levels in the subtraction, and for initial values
    a = 0
    mean = 20
    std = 50
    
    b = 0
    plotx = _n.array(0)
    ploty = _n.array(1)

    #Threshold filter for getting away with the noise in the fine alignment tab    
    filterthreshold = 100
    
#    #for the fien alignment subtration\
#    f = 0
    
    
    # global variables for script execution
    g = _n.__dict__
    
    # loop until we're told not to
    while button_stream.is_checked():
        
        #if we change the tab we look at, change the video input to the input source specified in the tab
        if tab != tabs.get_current_tab():
            
            # release the camera
            camera.release()

            if   tabs.get_current_tab() == 0: 
                channel = int(video_input_tab0.get_value())
                tab = 0
        
            elif tabs.get_current_tab() == 1:
                channel = int(video_input_tab1.get_value())
                tab = 1
        
            elif tabs.get_current_tab() == 2:
                channel = int(video_input_tab2.get_value())
                tab = 2
        
            elif tabs.get_current_tab() == 3:
                channel = int(video_input_tab3.get_value())
                tab = 3
        
            elif tabs.get_current_tab() == 4:
                channel = int(video_input_tab4.get_value())
                tab = 4
        
            else:
                print "Something went really wrong when I tried to get the video input"
                
            # connect to the camera again in the new tab
            camera = _cv2.VideoCapture(channel)
            
        
        # get an image
        success, image = camera.read()
        if success:
            
            
            # process the image
            image = image_to_rgb_data(image)
            g.update(dict(r=image[:,:,0],
                          g=image[:,:,1],
                          b=image[:,:,2]))

            # the try/except thing here prevents a bad script from
            # pooping out the program. 
            try:
                # get the plot data based on the script
                data = eval(text_script.get_text(), g)
                
                
                # update the image based on which tab we're looking at
                if   tabs.get_current_tab() == 0: 

                    image_raw.set_data(data)    
                    

                elif tabs.get_current_tab() == 1:
#                    # Normalize the data and reference images
#                    max_reference = _n.amax(image_reference.data)
#                    max_data      = _n.amax(data)
#                    data = data/max_data
#                    image_reference.data = image_reference.data/max_reference
                    
                    # Get the 2d array of the image subtraction
                    working = data-image_reference.data
                    
                    # Set the image subtraction
                    image_subtracted.set_data(working) 
                    
                    # Set the levels of the histogram
                    image_subtracted.set_levels(mean-5*std, mean+5*std, mean-3*std, mean+3*std )
                    
                    #Increment a, used to update the histogram min and max values
                    a = a+1
                    
                    # Only every five frames update our histogram, save computation time 
                    if a %5 == 0:
                        
                       # Flatten the 2D data array to a 1D one and compute the mean & std. deviation
                        deviation = working.flatten()
                        deviation = deviation[::5]
                        std = _n.std(deviation)
                        mean= _n.mean(deviation) 
                        
                        # Update the arrays which are to be plotted 
                        b += 1
                        plotx = _n.append(plotx, b)
                        ploty = _n.append(ploty, 50*std)
                        
                        # Do the plotting
                        deviation_plot.clear()
                        plot = _egg.pyqtgraph.PlotCurveItem(plotx, ploty)
                        deviation_plot.addItem(plot)
                        
                        #Set the histogram min and max values
                        image_subtracted.set_levels(mean-5*std, mean+5*std, mean-3*std, mean+3*std )
                   
                elif tabs.get_current_tab() == 2:
                    
                    #Get the reference image data
                    image_ref = image_reference.data
                    
                    #Get the values for averaging
                    n = 0
                    averages_num = int(average_number.get_value())
                    
                    # Average data over averages_num number of captures to reduce fluctuations
                    for i in range (0, averages_num):
                        print averages_num
                         # update the average
                        if n==0: average = data
                        else:    average = (1.0*average*n + data)/(n+1)
                        n +=1
                        
                    #Because its easier to read   
                    data = average
                    
                    # These masks serve as noise threshold filters
                    mask_dat = _n.where(data > filterthreshold, 1 , 0)  
                    mask_ref = _n.where(image_reference.data > filterthreshold, 1 , 0) 
                    
                    #Find the index of the maximum in the reference array, needed to zoom in:
                    i, j = _n.unravel_index(image_ref.argmax(), image_ref.shape)
                    
                    #Get the step size for the automated zoom
                    zoom = zoom_input.get_value()
                    
                    #Find start and end indices for the zoom crop    
                    start_i = i - zoom
                    end_i = i + zoom + 1
                    start_j = j - zoom
                    end_j = j + zoom + 1
                    
                    #Make sure we don't get negative indices
                    if start_i < 0 or start_j < 0:
                        start_i = 0
                        start_j = 0 
                   
                    #Crop the noise masks and the data
                    mask_dat = mask_dat[start_i:end_i, start_j: end_j]
                    mask_ref = mask_ref[start_i:end_i, start_j: end_j]

                    image_ref = image_ref[start_i:end_i, start_j: end_j]
                    data = data[start_i:end_i, start_j: end_j]

                    # Multiply our 2d data and reference image arrays with noise filters
                    image_ref = image_ref*mask_ref
                    data *=mask_dat
                    

                    # Get the 2d array of the image subtraction
                    working = image_ref - data
                    working = _n.abs(working)

                    # Set the image subtraction
                    image_subtracted2.set_data(working) 
                    
                    # Set the levels of the histogram
                    image_subtracted2.set_levels(0, 100, 0, 100 )
                    
                    #Increment a, used to update the histogram min and max values
                    a = a+1
                    
                    # Only every five*average_num frames update our deviation plot, save computation time 
                    if a %5 == 0:
                        
                        # Flatten the 2D data array to a 1D one and compute the mean & std. deviation
                        deviation = working.flatten()
                        deviation = deviation[::5]
                        std = _n.std(deviation)
                        mean= _n.mean(deviation) 
                        
                        # Update the arrays which are to be plotted
                        b += 1
                        plotx = _n.append(plotx, b)
                        ploty = _n.append(ploty, 50*std)
                        
                        # Do the plotting
                        deviation_plot2.clear()
                        plot = _egg.pyqtgraph.PlotCurveItem(plotx, ploty)
                        deviation_plot2.addItem(plot)
                        
                        #Set the histogram min and max values
                       # image_subtracted2.set_levels(-1, 3, -1, 3 )   
                        
                elif tabs.get_current_tab() == 3:
                    
                    working = data-image_reference_tab3.data
                    
                    # Set the image subtraction
                    image_subtracted_tab3.set_data(working)

                    
                elif tabs.get_current_tab() == 4:
                    
                    working = data-image_reference_tab4.data
                    
                    # Set the image subtraction
                    image_subtracted_tab4.set_data(working)
                    
        
        
            # If the script pooped. Quietly do nothing. The 
            # script box should be pink already
            except: pass
                
            # update the frames per second
            n = n+1
            if n%10 == 0:
                label_fps.set_text("FPS = " + str(int(1.0*n/(_t.time()-t0))))
                n = 0
                t0 = _t.time()
         
        # Set the tab variable so that we can check wether we changed the tab
        tab = tabs.get_current_tab()
            
        # let the gui update every frame. Otherwise it freezes!    
        window.process_events()

    # release the camera
    camera.release()
    
    # enable other camera stuff
    button_get_reference.enable()
    button_get_reference_3.enable()
    button_get_reference_4.enable()
    
# connect the button to the function
window.connect(button_stream.signal_clicked, button_stream_pressed)





# (towards a) clean shutdown of the window
def window_close():
    
    # uncheck the stream button, and wait until it's done.
    button_stream.set_checked(False)
    
    # This is a hack. I tried waiting for the loop to finish but that froze. :\    
    window.pause(0.5)

# overwrite the event_close function (there is no signal for this)
window.event_close = window_close




# final setup and show!
window.show(True)


