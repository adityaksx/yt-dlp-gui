import tkinter as tk
from app_controller import AppController
from gui import AppGUI


def main():
    root = tk.Tk()
    controller = AppController(root)
    gui = AppGUI(root, controller)
    controller.bind_gui(gui)
    controller.check_tools_clicked()
    root.mainloop()


if __name__ == "__main__":
    main()
