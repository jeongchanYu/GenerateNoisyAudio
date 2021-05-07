import os
import io_function as iof
import signal_processing as sp
from tkinter import filedialog
from tkinter import messagebox
from tkinter import*
import tkinter.ttk
import platform

# Generate window
window = Tk()
window.title("Noisy Audio Generator")
window.geometry("450x300")
window.resizable(True, False)
if platform.system() == 'Windows':
    window.iconbitmap("{}/gui_icon.ico".format(iof.load_path()))

def select_source_file():
    source_entry.delete(0, END)
    source_entry.insert(0, filedialog.askopenfilename(filetypes=(('wav file', '*.wav'),)))

def select_source_dir():
    source_entry.delete(0, END)
    source_entry.insert(0, filedialog.askdirectory())


# Source path select
source_window = PanedWindow()
source_window.pack(pady=5)
Label(source_window, text='Source Path', width=11).pack(side=LEFT)
source_entry = Entry(source_window, width=22)
source_entry.pack(side=LEFT, padx=5)
source_file_button = Button(source_window, text='Load File', command=select_source_file, width=7)
source_file_button.pack(side=LEFT)
source_dir_button = Button(source_window, text='Load Directory', command=select_source_dir, width=12)
source_dir_button.pack(side=LEFT)


def select_noise_file():
    noise_entry.delete(0, END)
    noise_entry.insert(0, filedialog.askopenfilename(filetypes=(('wav file', '*.wav'),)))

def select_noise_dir():
    noise_entry.delete(0, END)
    noise_entry.insert(0, filedialog.askdirectory())


# Noise path select
noise_window = PanedWindow()
noise_window.pack(pady=5)
Label(noise_window, text='Noise Path', width=11).pack(side=LEFT)
noise_entry = Entry(noise_window, width=22)
noise_entry.pack(side=LEFT, padx=5)
noise_file_button = Button(noise_window, text='Load File', command=select_noise_file, width=7)
noise_file_button.pack(side=LEFT)
noise_dir_button = Button(noise_window, text='Load Directory', command=select_noise_dir, width=12)
noise_dir_button.pack(side=LEFT)


def select_output_dir():
    output_entry.delete(0, END)
    output_entry.insert(0, filedialog.askdirectory())


# Output path select
output_window = PanedWindow()
output_window.pack(pady=5)
Label(output_window, text='Output Path', width=11).pack(side=LEFT)
output_entry = Entry(output_window, width=22)
output_entry.pack(side=LEFT, padx=5)
output_dir_button = Button(output_window, text='Load Directory', command=select_output_dir, width=23)
output_dir_button.pack(side=LEFT)


def radio_select():
    if snr_ssnr_radio_value.get() == 'snr':
        snr_ssnr_label['text'] = 'SNR'
        frame_size_frame.pack_forget()
    elif snr_ssnr_radio_value.get() == 'ssnr':
        snr_ssnr_label['text'] = 'SSNR'
        frame_size_frame.pack()


# SNR and SSNR select part
snr_ssnr_window = PanedWindow()
snr_ssnr_window.pack(pady=20)
snr_ssnr_frame = Frame(snr_ssnr_window)
snr_ssnr_frame.pack()
snr_ssnr_label = Label(snr_ssnr_frame, text='SNR', width=5)
snr_ssnr_label.pack(side=LEFT)
decibel_entry = Entry(snr_ssnr_frame, justify='right', width=5)
decibel_entry.pack(side=LEFT, padx=5)
Label(snr_ssnr_frame, text='dB').pack(side=LEFT)
Label(snr_ssnr_frame, text='  ').pack(side=LEFT)
snr_ssnr_radio_value = StringVar()
snr_radio = Radiobutton(snr_ssnr_frame, text='SNR', variable=snr_ssnr_radio_value, value='snr', indicatoron=0, command=radio_select)
snr_radio.pack(side=LEFT)
ssnr_radio = Radiobutton(snr_ssnr_frame, text='SSNR', variable=snr_ssnr_radio_value, value='ssnr', indicatoron=0, command=radio_select)
ssnr_radio.pack(side=LEFT)

frame_size_frame = Frame(snr_ssnr_window)
Label(frame_size_frame).pack()
Label(frame_size_frame, text='Frame Size').pack(side=LEFT)
frame_size_entry = Entry(frame_size_frame, justify='right', width=10)
frame_size_entry.pack(side=LEFT, padx=5)

snr_radio.invoke()


# Progress bar
progressbar = tkinter.ttk.Progressbar(window, mode='determinate')
progressbar.pack(fill='x', padx=20)


def main():
    generate_button['text'] = 'Processing...'
    window.update()
    snr_or_ssnr = snr_ssnr_radio_value.get()
    frame_size = None
    if snr_or_ssnr == 'ssnr':
        frame_size = frame_size_entry.get()
        if frame_size_entry.get() == '':
            raise Exception("ERROR: SSNR must have a frame size")
        elif not frame_size.isdecimal():
            raise Exception("ERROR: Frame size is not a number")
        frame_size = int(frame_size)

    target_dB = decibel_entry.get()
    if target_dB == '':
        raise Exception("ERROR: SNR or SSNR value is empty")
    else:
        try:
            target_dB = float(target_dB)
        except Exception:
            raise Exception("ERROR: Selected SNR or SSNR is not a number")


    input_file_dir = source_entry.get()
    noise_file_dir = noise_entry.get()
    output_file_dir = output_entry.get()

    if input_file_dir == "":
        raise Exception("ERROR: Source path is empty")
    if noise_file_dir == "":
        raise Exception("ERROR: Noise path is empty")
    if output_file_dir == "":
        raise Exception("ERROR: Output path is empty")

    # check input, noise directory
    input_is_dir = os.path.isdir(input_file_dir)
    noise_is_dir = os.path.isdir(noise_file_dir)
    if input_is_dir:
        input_file_list = iof.read_dir_list(input_file_dir, extention='wav')
    else:
        input_file_list = [input_file_dir]
    if noise_is_dir:
        noise_file_list = iof.read_dir_list(noise_file_dir, extention='wav')
    else:
        noise_file_list = [noise_file_dir]

    if len(input_file_list) == 0:
        raise Exception("ERROR: Input file is not exist")
    if len(noise_file_list) == 0:
        raise Exception("ERROR: Noise file is not exist")

    total_length = 0
    for wav_file in noise_file_list:
        temp_noise_signal, temp_sample_rate = iof.read_wav(wav_file)
        total_length += len(temp_noise_signal)
    for wav_file in input_file_list:
        temp_input_signal, temp_sample_rate = iof.read_wav(wav_file)
        total_length += len(temp_input_signal)
    progressbar['maximum'] = total_length
    progressbar_value = 0
    # make noise set
    old_sample_rate = 0
    temp_sample_rate = 0
    noise_signal_train = []
    print('Processing noise file.')
    i = 0
    for wav_file in noise_file_list:
        i += 1
        print('Processing({}) {}/{} ...'.format(wav_file, i, len(noise_file_list)))
        temp_noise_signal, temp_sample_rate = iof.read_wav(wav_file)
        if old_sample_rate != 0 and old_sample_rate != temp_sample_rate:
            raise Exception("ERROR: Different sample rate is exist.")
        else:
            old_sample_rate = temp_sample_rate

        temp_noise_signal = sp.change_power(temp_noise_signal, 1)
        noise_signal_train.extend(temp_noise_signal)

        progressbar_value += len(temp_noise_signal)
        progressbar['value'] = progressbar_value
        window.update()

    # mix noise
    old_sample_rate = 0
    temp_sample_rate = 0
    noise_start_point = 0
    print('Generate noisy file.')
    i = 0
    for wav_file in input_file_list:
        i += 1
        print('Processing({}) {}/{} ...'.format(wav_file, i, len(input_file_list)))
        temp_input_signal, temp_sample_rate = iof.read_wav(wav_file)
        if old_sample_rate != 0 and old_sample_rate != temp_sample_rate:
            raise Exception("ERROR: Different sample rate is exist.")
        else:
            old_sample_rate = temp_sample_rate

        temp_noise_signal = []
        left_size = len(temp_input_signal)
        while left_size > 0:
            available_length = len(noise_signal_train) - noise_start_point
            available_length = min(available_length, left_size)
            temp_noise_signal.extend(noise_signal_train[noise_start_point:noise_start_point + available_length])
            left_size -= available_length
            noise_start_point += available_length
            if noise_start_point == len(noise_signal_train):
                noise_start_point = 0

        mixed_signal = sp.mix_noise(temp_input_signal, temp_noise_signal, target_dB, snr_or_ssnr, frame_size)

        if os.path.isdir(input_file_dir):
            temp_output_file_dir = wav_file.replace(input_file_dir, output_file_dir)
        else:
            temp_output_file_dir = output_file_dir + '/' + os.path.basename(input_file_dir)
        iof.create_folder(os.path.dirname(temp_output_file_dir))
        iof.write_wav(mixed_signal, temp_output_file_dir, temp_sample_rate)

        progressbar_value += len(temp_input_signal)
        progressbar['value'] = progressbar_value
        window.update()

    messagebox.showinfo("Processing completed", "{} noisy files generated.".format(len(input_file_list)))
    generate_button['text'] = 'Generate'
    progressbar_value = 0
    progressbar['value'] = progressbar_value

def generate_click():
    try:
        main()
    except Exception as e:
        messagebox.showerror("ERROR", e)

generate_button = Button(window, text='Generate', command=generate_click)
generate_button.pack(pady=10)

window.mainloop()