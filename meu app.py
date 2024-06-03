import customtkinter
import os
import datetime

from PIL import Image
import tkinter 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg , NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import serial
import serial.tools.list_ports  # To get available serial ports

FONT_TYPE = "meiryo"

class App(customtkinter.CTk):
    global_flag = True
    def __init__(self):
        super().__init__()
        self.serial_port_status = False
        self.flag_start = False
        self.data_buffer = [1,2,3,5,5,5,0,8,2]
        self.timediv = 20
        self.times = 0
        self.volt_div = 1
        self.title("mskh")
        self.geometry("800x500")
 
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")

        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "welcom3.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),  dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),  dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),  dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=" Menu", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, 
                                                    corner_radius=0, 
                                                    height=40, 
                                                    border_spacing=10, 
                                                    text="Home",
                                                    fg_color="transparent", 
                                                    text_color=("gray10", "gray90"), 
                                                    hover_color=("gray70", "gray30"),
                                                    image=self.home_image, 
                                                    anchor="w", 
                                                    command=self.home_button_event)
        
        self.home_button.grid(row=1, column=0, sticky="ew")


        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, 
                                                        corner_radius=0, 
                                                        height=40, 
                                                        border_spacing=10, 
                                                        text="Osiloscop",
                                                        fg_color="transparent", 
                                                        text_color=("gray10", "gray90"), 
                                                        hover_color=("gray70", "gray30"),
                                                        image=self.chat_image, 
                                                        anchor="w", 
                                                        command=self.frame_2_button_event)
        
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame,
                                                        corner_radius=0,
                                                        height=40, 
                                                        border_spacing=10, 
                                                        text="Function Generator",
                                                        fg_color="transparent", 
                                                        text_color=("gray10", "gray90"), 
                                                        hover_color=("gray70", "gray30"),
                                                        image=self.add_user_image, 
                                                        anchor="w", 
                                                        command=self.frame_3_button_event)
        
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(2, weight=1)
        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

       
        self.valuport = ['select port']
        for port in serial.tools.list_ports.comports():
            self.valuport.append(port.device)
        print(self.valuport)
    
        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.home_frame,
                                                        dynamic_resizing=False,
                                                        values=self.valuport,
                                                        command=self.select_serial_port)
        

        self.optionmenu_1.grid(row=1, column=0, padx=20, pady=(20, 10))


        self.textbox = customtkinter.CTkTextbox(self.home_frame, height = 423,width = 85)
        self.textbox.grid(row=2, column=0, padx=(20, 20),pady=(20, 20), sticky="nsew")

        # create second frame
        self.osiloscop_fram = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.osiloscop_fram.grid_rowconfigure(1, weight=1)
        self.osiloscop_fram.grid_columnconfigure(0, weight=1)
       
        self.read_file_frame = customtkinter.CTkFrame(self.osiloscop_fram, corner_radius=0, fg_color="transparent")
        self.read_file_frame.grid(row=0, column=0, padx=0, pady=(10,10), sticky="nsew")
        self.read_file_frame.grid_rowconfigure(1, weight=1)
        self.read_file_frame.grid_columnconfigure(0, weight=1)
       
        self.textbox_filepath = customtkinter.CTkEntry(master=self.read_file_frame, placeholder_text="path file")
        self.textbox_filepath.grid(row=0, column=0, padx=20, pady=20, sticky="ew") 

        self.button_select = customtkinter.CTkButton(master=self.read_file_frame, 
                                                    fg_color="transparent",
                                                    border_width=2, 
                                                    text_color=("gray10", "#DCE4EE"),   
                                                    command=self.button_select_callback, 
                                                    text="select file",
                                                    width=80)
        
        self.button_select.grid(row=0, column=1, padx=(10,130), pady=20,sticky="e")
     
        self.button_open = customtkinter.CTkButton(master=self.read_file_frame, command=self.button_open_callback, text="open",width=80 )
        self.button_open.grid(row=0, column=1, padx=30, pady=20,sticky="e")


        self.plot_main_frame = customtkinter.CTkFrame(self.osiloscop_fram, corner_radius=0, fg_color="transparent")
        self.plot_main_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")
        self.plot_main_frame.grid_rowconfigure(0, weight=1)
        self.plot_main_frame.grid_columnconfigure(1, weight=1)
       
        
        self.fig, self.ax = plt.subplots(figsize=(12,6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_main_frame)
        self.canvas.get_tk_widget().grid(row=0 ,column=1, padx=(20, 20),pady=(20, 20), sticky="nsew")
        
        self.toolbar_frame = tkinter.Frame(self.plot_main_frame)
        self.toolbar_frame.grid(row=0, column=1, padx=(20, 20),pady=(20, 20), sticky="se")

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

        self.line, = self.ax.plot([], [])
        self.ax.set_title("Plot")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")

        self.x_label_var = tkinter.StringVar()
        self.ax.set_xlabel(self.x_label_var.get())
        
        self.update_plot_offline()

        self.ani = FuncAnimation(self.fig, self.update_plot, interval=200)

       
        self.plot_edit_frame = Plot_setting_Frame(master=self.plot_main_frame,header_name="Setting",sampletime_call = self.select_sampletime ,start_call = self.button_start_callback,stop_call = self.button_stop_callback,save_plot_call =self.button_saveplot_callback)
        self.plot_edit_frame.grid(row=0, column=0, padx=20, pady=20,sticky="sn")
 
       #***************************************************************************************************************************
        # create third frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.select_frame_by_name("home")

    # def print_app(self):
    #     print("print in class app")
    #     print("flag : ",self.global_flag)

    def update_plot_offline(self):
        self.x_values = list(range(len(self.data_buffer)))
        self.line.set_data(range(self.times,(len(self.data_buffer)+self.times)), self.data_buffer)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def update_plot(self, frame):
        try:
            if  self.serial_port_status & self.flag_start:
                # Read and decode serial data
                lsb = int.from_bytes(self.serial_port.read(), "big")
                msb = int.from_bytes(self.serial_port.read(), "big")
                number = (msb<<8) | lsb
                value = (number/4096)*3.3
                
                # Update the data buffer
                self.data_buffer.append(value)
                if len(self.data_buffer) > self.timediv:  # Keep a limited number of points
                    self.data_buffer.pop(0)
                    self.times += 1
                self.update_plot_offline()
        except Exception as e:
            print(f"Error: {e}")
 
    def button_select_callback(self):

        file_name = self.file_read()

        if file_name is not None:
            self.textbox_filepath.delete(0, tkinter.END)
            self.textbox_filepath.insert(0, file_name)

    def button_open_callback(self):

        if self.textbox_filepath.get() is not None:
            filepath = self.textbox_filepath.get()
            print(filepath)
            self.data_buffer = []
            with open(filepath,"r") as file:
                # Read the contents of the file into a variable
                self.data_buffer = [float(line.rstrip()) for line in file]

            self.update_plot_offline()
            self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") + f'  ->  Ploted signal from {filepath}  \n')

        
    @staticmethod
    def file_read():
        current_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = tkinter.filedialog.askopenfilename(filetypes=[("file name","*.txt")],initialdir=current_dir)

        if len(file_path) != 0:
            return file_path
        else:
            return None

    def serial_print(self):
        self.textbox.insert('end',self.serial_port.readline())

    def select_serial_port(self,port_name):
        self.real_port = ['select port']
        if port_name == 'select port':
            print("please select a port")
            for port in serial.tools.list_ports.comports():
                print(port.device)
                self.real_port.append(port.device)
            self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") +'  ->  Port number Updated\n')
            print('real port is :',self.real_port) 
            self.optionmenu_1.configure(values= self.real_port)

        else:
            self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") +'  ->  Connecting to '+f"{port_name} ...\n")

            try:
                if self.serial_port_status:
                    self.serial_port.close()

                self.serial_port = serial.Serial(port_name, baudrate=9600)
                self.serial_port_status = True
                self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") + f"   ->  Connected to port: {port_name}\n")
                print(self.serial_port.read())
                
                self.textbox.insert('end', datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") +"  ->  " + self.serial_port.read())

            except Exception as e:
                print('error is ',e )
        
    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.osiloscop_fram.grid(row=0, column=1, sticky="nsew")
        else:
            self.osiloscop_fram.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    
    def button_start_callback(self):
        self.flag_start = True
        self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") + f"  ->  starting oscop ...  \n" )


    def button_stop_callback(self):
        self.flag_start  = False
        self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") + f"  ->  oscop is stop \n" )

       
    def button_saveplot_callback(self):
        file_path = tkinter.filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                for data in self.data_buffer:
                    file.writelines(f"{data}\n")
            tkinter.messagebox.showinfo("Success", f"File '{file_path}' created successfully!")
            self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") + f"  ->  save signal successfully from  '{file_path}' \n" )

        else:
            tkinter.messagebox.showerror("Error", "File creation canceled.")
            self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") + f"  ->  save signal faled !!! \n" )


    def select_sampletime(self,sampletime):
        print("sample time is :",sampletime)
        self.textbox.insert('end',datetime.datetime.now().strftime("%Y-%m-%d   %H:%M:%S") + '  ->  selected '+f" {sampletime} " + " sampletime Succesfully\n")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)



class Plot_setting_Frame(customtkinter.CTkFrame):

    def __init__(self,start_call= None,stop_call= None,save_plot_call= None,sampletime_call = None, *args, header_name="PlotConfigFrame", plot_config=None, **kwargs ):
        super().__init__(*args, **kwargs)
        
        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        self.start = start_call
        self.stop =stop_call
        self.sampletime_func = sampletime_call
        self.save_plot = save_plot_call

        self.plot_config = None
        self.setup_form()

    def setup_form(self):

        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self,corner_radius=0, text=self.header_name, font=(FONT_TYPE, 11))
        self.label.grid(row=0, column=0, padx=20, sticky="nw")

        self.combobox_label = customtkinter.CTkLabel(self, text="type line", font=(FONT_TYPE, 13))
        self.combobox_label.grid(row=3, column=0, padx=20, pady=(20,0), sticky="ew")

        self.combobox = customtkinter.CTkComboBox(master=self,corner_radius=0, font=self.fonts,
                                     values=["line", "dashed", "line + marker"],
                                     command=self.combobox_callback)
        self.combobox.grid(row=4, column=0, padx=20, pady=(0,20), sticky="ew")
       
        self.sampletime_menu = customtkinter.CTkOptionMenu(self,
                                                         dynamic_resizing=False,
                                                        values=["8M","500K","50k","Realtime"],
                                                        command=self.sampletime_func)
        self.sampletime_menu.grid(row=1, column=0, padx=20, pady=(20, 10))

        self.button_open = customtkinter.CTkButton(master=self, command=self.start, text="Start", hover_color="green",width=100 , font=self.fonts)
        self.button_open.grid(row=5, column=0, padx=10, pady=(0,10))
        
        self.button_open = customtkinter.CTkButton(master=self, command=self.stop, text="Stop",hover_color="red" ,width=100 , font=self.fonts)
        self.button_open.grid(row=6, column=0, padx=10, pady=(0,10))

        self.button_open = customtkinter.CTkButton(master=self, command=self.save_plot, text="Save Plot" ,width=100 , font=self.fonts)
        self.button_open.grid(row=7, column=0, padx=10, pady=(0,10))

    
    def slider_event(self, value):
        old_label = self.slider_label.cget("text")
        new_label = f"scale {value}"
        if old_label != new_label:
          
            self.slider_label.configure(text=new_label)
            self.plot_config["linewidth"] = value
            self.master.update(config=self.plot_config)
    
    def combobox_callback(self,value):

        self.plot_config["linetype"] = value
        self.master.update(config=self.plot_config)



if __name__ == "__main__":
    app = App()
    app.mainloop()

