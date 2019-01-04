import os
import tkinter as tk
from tkinter import colorchooser as cc
from tkinter import filedialog as fd
from tkinter import messagebox as mb

from PIL import Image, ImageTk

from backend import Notes

# Constants
STICKY = (tk.N + tk.E + tk.S + tk.W)


class NoteShrinkGUI(tk.Frame):
    def __init__(self, master=None):
        # Main Window Options
        tk.Frame.__init__(self, master)
        self.master.title("Note Shrinker")
        self.grid()
        self.master.iconbitmap("assets/notes_icon.ico")
        # Assets
        temp = Image.open('assets/add_file.png')
        temp = temp.resize((32, 32), resample=Image.LANCZOS)
        self.img_add_file = ImageTk.PhotoImage(temp)
        self.file_error = ImageTk.PhotoImage(Image.open('assets/file_error.png'))

        # Variables
        self.bg_color = None
        self.bg_color_set_state = tk.IntVar()
        self.image_orig = None

        self.file_path = tk.StringVar()
        self.v_thresh = tk.IntVar()
        self.v_thresh.set(25)
        self.s_thresh = tk.IntVar()
        self.s_thresh.set(15)
        self.bit_depth = tk.IntVar()
        self.bit_depth.set(6)
        self.color_count = tk.IntVar()
        self.color_count.set(8)

        self.file_increment = 0

        # Validation
        vcmd = (master.register(self._validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # Row 1: Select File & Options
        self.option_frame = tk.Frame(self)
        self.option_frame.grid(row=0, column=0, sticky=STICKY)

        ## Choose File
        self.choose_file_frame = tk.LabelFrame(self.option_frame, text="Choose a file")
        self.choose_file_frame.grid(row=0, column=0)
        self.choose_file_entry = tk.Entry(self.choose_file_frame, textvariable=self.file_path, width=40, )
        self.choose_file_entry.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.choose_file_button = tk.Button(self.choose_file_frame, image=self.img_add_file,
                                            command=self._get_file_name)
        self.choose_file_button.grid(row=0, column=1, sticky=STICKY)
        self.open_file_button = tk.Button(self.choose_file_frame, command=self._open_file, text='Open')
        self.open_file_button.grid(row=0, column=2, sticky=STICKY)

        ## Set BG Color
        self.bg_color_set = tk.Checkbutton(self.option_frame, text="Custom Color", command=self._set_bg_color,
                                           variable=self.bg_color_set_state)
        self.bg_color_set.grid(row=1, column=0)

        ## Sliders
        self.slider_frame = tk.Frame(self.option_frame)
        self.slider_frame.grid(row=2, column=0)

        ### Saturation Threshold Slider & Input
        self.s_thresh_slider = tk.Scale(self.slider_frame, variable=self.s_thresh, from_=10, to=30,
                                        orient=tk.HORIZONTAL,
                                        label='Saturation Threshold', length=250)
        self.s_thresh_slider.grid(row=0, column=0)

        ### Value Threshold Slider
        self.v_thresh_slider = tk.Scale(self.slider_frame, variable=self.v_thresh, from_=15, to=40,
                                        orient=tk.HORIZONTAL,
                                        label="Value Threshold", length=250)
        self.v_thresh_slider.grid(row=1, column=0)

        ### Bit Depth Slider
        self.b_slider = tk.Scale(self.slider_frame, variable=self.bit_depth, from_=2, to=8, orient=tk.HORIZONTAL,
                                 label="Bit-depth Threshold", length=250)
        self.b_slider.grid(row=2, column=0)

        ## Color Count Entry & Label
        self.color_count_frame = tk.Frame(self.option_frame)
        self.color_count_frame.grid(row=3, column=0, sticky=STICKY)
        self.color_count_entry = tk.Entry(self.color_count_frame, textvariable=self.color_count, validate='key',
                                          validatecommand=vcmd, width=4)
        self.color_count_entry.grid(row=0, column=1)
        self.color_count_label = tk.Label(self.color_count_frame, text="Color Count (between 4-16):     ")
        self.color_count_label.grid(row=0, column=0)

        ## Run, Rerun, and Save Buttons
        self.button_frame = tk.Frame(self.option_frame)
        self.button_frame.grid(row=6, column=0)
        self.run_button = tk.Button(self.button_frame, command=self._run, text="Run", width=40, height=2)
        self.run_button.grid(row=0, column=0)

        self.rerun_button = tk.Button(self.button_frame, command=self._rerun, text="Re-run", width=20, height=2)
        self.save_button = tk.Button(self.button_frame, command=self._save, text="Save", width=20, height=2)

        ################################################################################################################
        # Original Image
        self.orig_image_label = tk.Label(self, image=None)
        self.orig_image_label.grid(row=0, column=1)

        self.final_image_label = tk.Label(self, image=None)
        self.final_image_label.grid(row=0, column=2)

    def _get_file_name(self):
        file_path = fd.askopenfilename(title="Select Image", initialdir=os.path.expanduser('~') + "/Documents",
                                       filetypes=(("Images", ".jpeg"), ("Images", ".jpg"), ("Images", ".png")))
        self.file_path.set(file_path)

    def _run(self):  # TODO: Implement run
        if self.image_orig is not None:

            self.run_button.config(state=tk.DISABLED, text="Running...")

            note = Notes(self.image_orig, self.bg_color, self.v_thresh.get(), self.s_thresh.get(), self.bit_depth.get(),
                         self.color_count.get())

            try:
                self.image_final = note.process()
            except:
                mb.showerror("Oh crap", "Run failed! Inform the developer immediately!")
                quit()

            temp = ImageTk.PhotoImage(self.image_final.resize((450, 619), resample=Image.LANCZOS))
            self.final_image_label.configure(image=temp)
            self.final_image_label.image = temp

            self.run_button.grid_remove()
            self.rerun_button.grid(row=0, column=0, sticky=STICKY)
            self.save_button.grid(row=0, column=1, sticky=STICKY)
        else:
            print("wait what")

    def _rerun(self):
        self.rerun_button.config(state=tk.DISABLED, text="Running...")
        note = Notes(self.image_orig, self.bg_color, self.v_thresh.get(), self.s_thresh.get(), self.bit_depth.get(),
                     self.color_count.get())
        self.final_image_label = note.process()

        temp = ImageTk.PhotoImage(self.image_final.resize((450, 619), resample=Image.LANCZOS))
        self.final_image_label.configure(image=temp)
        self.final_image_label.image = temp

        self.rerun_button.config(state=tk.NORMAL, text="Re-Run")

    def _save(self):
        self.file_increment += 1
        save_file = fd.asksaveasfilename(defaultextension='.pdf', initialdir=os.path.expanduser('~') + "/Documents",
                                         initialfile="notes{}".format(self.file_increment))
        if save_file == "":
            print('https://bit.ly/2QmOJrA')
            self.file_increment -= 1
        else:
            self.image_final.save(save_file)
            self.rerun_button.grid_remove()
            self.save_button.grid_remove()
            self.run_button.config(text="Run", state=tk.NORMAL)
            self.run_button.grid(row=0, column=0, sticky=STICKY)

    def _set_bg_color(self):
        if self.bg_color_set_state.get() == 1:
            self.bg_color, _ = cc.askcolor()
        else:
            self.bg_color = None

    def _open_file(self):  # TODO: Fix Image Display
        try:
            self.image_orig = Image.open(self.file_path.get())
            temp = ImageTk.PhotoImage(self.image_orig.resize((450, 619), resample=Image.LANCZOS))
            self.orig_image_label.configure(image=temp)
            self.orig_image_label.image = temp  # keeps a reference to the image file

        except AttributeError:
            self.file_path.set("ERROR: Empty File path")

        except FileNotFoundError:
            self.file_path.set("ERROR: Can't find file")

        except:
            self.file_path.set("Unknown Error")

    @staticmethod
    def _validate(action, index, value_if_allowed,
                  prior_value, text, validation_type, trigger_type, widget_name):
        if action == '1':
            if text in '0123456789.-+':
                try:
                    float(value_if_allowed)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True


def main():
    root = tk.Tk()
    NoteShrinkGUI(root).mainloop()


main()
