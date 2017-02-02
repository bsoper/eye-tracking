from Tkinter import *

#Create main window
root = Tk()

#Set window size
root.minsize(width=400, height = 400)
root.maxsize(width=400, height=400)

#Update root
root.update_idletasks()

#Get window height and width
w_height = root.winfo_height()
w_width = root.winfo_width()

#Set background to black
root.configure(background="white")

#Let's now add buttons
tb_width = w_width/2
tb_height = w_height/4
lr_width = w_width/4
lr_height = w_height/2

print(tb_width)
print(tb_height)
b_top = Button(root, width=200, height=100)

b_top.place(relx=0.5, rely=0.5, anchor="center")

root.mainloop()
