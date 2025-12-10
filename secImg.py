from tkinter import *
from PIL import Image
img = Image.open("New Project.png")
img.save("person.gif")

# label = an area widget that holds text and/or an image within a window

window = Tk()

photo = PhotoImage(file='person.gif')

label = Label(window,
              text="bro, do you even code?",
              font=('Arial',40,'bold'),
              fg='blue',
              bg='black',
              relief=RAISED,
              bd=10,
              padx=20,
              pady=20,
              image=photo,
              compound='bottom')
label.pack()
#label.place(x=0,y=0)

window.mainloop()