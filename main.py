import tkinter as tk
from app_controller import AppController
from gui import ModernGUI


def main():
    root = tk.Tk()
    controller = AppController(root)
    gui = ModernGUI(root, controller)
    controller.bind_gui(gui)
    controller.check_tools()
    root.mainloop()


if __name__ == "__main__":
    main()
