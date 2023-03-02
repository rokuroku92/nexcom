import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title('oxxo.studio')
root.geometry('300x300')

def showinfo(): messagebox.showinfo('showinfo', 'showinfo')
btn_showinfo = tk.Button(root, text='showinfo', command=showinfo)
btn_showinfo.pack()

def showwarning(): messagebox.showwarning('showwarning', 'showwarning')
btn_showwarning = tk.Button(root, text='showwarning', command=showwarning)
btn_showwarning.pack()

def showerror(): messagebox.showerror('showerror', 'showerror')
btn_showerror = tk.Button(root, text='showerror', command=showerror)
btn_showerror.pack()

def askquestion(): messagebox.askquestion('askquestion', 'askquestion')
btn_askquestion = tk.Button(root, text='askquestion', command=askquestion)
btn_askquestion.pack()

def askyesno(): messagebox.askyesno('askyesno', 'askyesno')
btn_askyesno = tk.Button(root, text='askyesno', command=askyesno)
btn_askyesno.pack()

def askokcancel(): messagebox.askokcancel('askokcancel', 'askokcancel')
btn_askokcancel = tk.Button(root, text='askokcancel', command=askokcancel)
btn_askokcancel.pack()

def askretrycancel(): messagebox.askretrycancel('askretrycancel', 'askretrycancel')
btn_askretrycancel = tk.Button(root, text='askretrycancel', command=askretrycancel)
btn_askretrycancel.pack()

root.mainloop()