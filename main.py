import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from image_processing import (
    apply_box_filter,
    apply_brightness,
    apply_grayscale,
    apply_sobel,
    apply_threshold,
)


class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing")
        self.root.geometry("1200x760")
        self.root.minsize(980, 620)

        self.original_image = None
        self.processed_image = None

        self.original_photo = None
        self.processed_photo = None

        self.control_buttons = []
        self.pipeline_labels = {
            "grayscale": "Grayscale",
            "brightness": "Brightness",
            "box": "Box Filter",
            "sobel": "Sobel",
            "threshold": "Threshold",
        }
        self.pipeline_vars = {
            "grayscale": tk.BooleanVar(value=False),
            "brightness": tk.BooleanVar(value=False),
            "box": tk.BooleanVar(value=False),
            "sobel": tk.BooleanVar(value=False),
            "threshold": tk.BooleanVar(value=False),
        }
        self.pipeline_order = ["grayscale", "brightness", "box", "sobel", "threshold"]
        self.visible_pipeline_keys = []

        self._build_layout()

    def _build_layout(self):
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(main_container, width=250, padx=12, pady=12, bd=1, relief=tk.GROOVE)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(main_container, padx=12, pady=12)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(left_panel, text="Tools", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")

        io_frame = tk.Frame(left_panel)
        io_frame.pack(fill=tk.X, pady=(10, 14))

        self.load_button = tk.Button(io_frame, text="Load", command=self.load_image)
        self.load_button.pack(fill=tk.X)

        self.save_button = tk.Button(io_frame, text="Save", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(fill=tk.X, pady=(8, 0))

        tk.Label(left_panel, text="Brightness (-100..100)").pack(anchor="w")
        self.brightness_scale = tk.Scale(left_panel, from_=-100, to=100, orient=tk.HORIZONTAL)
        self.brightness_scale.set(0)
        self.brightness_scale.pack(fill=tk.X, pady=(0, 8))

        tk.Label(left_panel, text="Box Filter (3,5,7,9,11)").pack(anchor="w")
        self.kernel_scale = tk.Scale(left_panel, from_=3, to=11, resolution=2, orient=tk.HORIZONTAL)
        self.kernel_scale.set(3)
        self.kernel_scale.pack(fill=tk.X, pady=(0, 8))

        tk.Label(left_panel, text="Threshold (0..255)").pack(anchor="w")
        self.threshold_scale = tk.Scale(left_panel, from_=0, to=255, orient=tk.HORIZONTAL)
        self.threshold_scale.set(127)
        self.threshold_scale.pack(fill=tk.X, pady=(0, 12))

        pipeline_frame = tk.LabelFrame(left_panel, text="Pipeline", padx=8, pady=8)
        pipeline_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Checkbutton(
            pipeline_frame,
            text="Grayscale",
            variable=self.pipeline_vars["grayscale"],
            command=self._refresh_pipeline_order_listbox,
        ).pack(anchor="w")
        tk.Checkbutton(
            pipeline_frame,
            text="Brightness",
            variable=self.pipeline_vars["brightness"],
            command=self._refresh_pipeline_order_listbox,
        ).pack(anchor="w")
        tk.Checkbutton(
            pipeline_frame,
            text="Box Filter",
            variable=self.pipeline_vars["box"],
            command=self._refresh_pipeline_order_listbox,
        ).pack(anchor="w")
        tk.Checkbutton(
            pipeline_frame,
            text="Sobel",
            variable=self.pipeline_vars["sobel"],
            command=self._refresh_pipeline_order_listbox,
        ).pack(anchor="w")
        tk.Checkbutton(
            pipeline_frame,
            text="Threshold",
            variable=self.pipeline_vars["threshold"],
            command=self._refresh_pipeline_order_listbox,
        ).pack(anchor="w")

        tk.Label(pipeline_frame, text="Execution order").pack(anchor="w", pady=(8, 2))
        self.pipeline_order_listbox = tk.Listbox(
            pipeline_frame,
            height=5,
            selectmode=tk.SINGLE,
            exportselection=False,
        )
        self.pipeline_order_listbox.pack(fill=tk.X)

        self._refresh_pipeline_order_listbox()

        order_buttons_frame = tk.Frame(pipeline_frame)
        order_buttons_frame.pack(fill=tk.X, pady=(6, 0))

        self.pipeline_up_button = tk.Button(order_buttons_frame, text="Move Up", command=self.move_pipeline_up)
        self.pipeline_up_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self.pipeline_down_button = tk.Button(order_buttons_frame, text="Move Down", command=self.move_pipeline_down)
        self.pipeline_down_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        self.control_buttons.append(self.pipeline_up_button)
        self.control_buttons.append(self.pipeline_down_button)

        self._add_method_button(left_panel, "Apply Selected Pipeline", self.run_selected_pipeline)

        events_frame = tk.Frame(left_panel)
        events_frame.pack(fill=tk.BOTH, expand=True)

        self.events_text = tk.Text(events_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.events_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        events_scrollbar = tk.Scrollbar(events_frame, orient=tk.VERTICAL, command=self.events_text.yview)
        events_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.events_text.config(yscrollcommand=events_scrollbar.set)

        display_title = tk.Frame(right_panel)
        display_title.pack(fill=tk.X)

        tk.Label(display_title, text="Original", font=("TkDefaultFont", 10, "bold")).pack(side=tk.LEFT, expand=True)
        tk.Label(display_title, text="Processed", font=("TkDefaultFont", 10, "bold")).pack(side=tk.LEFT, expand=True)

        display_frame = tk.Frame(right_panel)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        self.original_label = tk.Label(display_frame, bd=1, relief=tk.SUNKEN, bg="#f5f5f5")
        self.original_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        self.processed_label = tk.Label(display_frame, bd=1, relief=tk.SUNKEN, bg="#f5f5f5")
        self.processed_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

    def _add_method_button(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command)
        button.pack(fill=tk.X, pady=3)
        self.control_buttons.append(button)

    def _set_controls_enabled(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED

        for button in self.control_buttons:
            button.config(state=state)

        self.brightness_scale.config(state=state)
        self.kernel_scale.config(state=state)
        self.threshold_scale.config(state=state)
        self.pipeline_order_listbox.config(state=state)

        self.load_button.config(state=state)
        self.save_button.config(state=tk.NORMAL if enabled and self.processed_image is not None else tk.DISABLED)

    def _push_event(self, message):
        self.events_text.config(state=tk.NORMAL)
        self.events_text.delete("1.0", tk.END)
        self.events_text.insert(tk.END, message)
        self.events_text.see(tk.END)
        self.events_text.config(state=tk.DISABLED)

    def _swap_pipeline_items(self, first_index, second_index):
        first_key = self.visible_pipeline_keys[first_index]
        second_key = self.visible_pipeline_keys[second_index]

        first_order_index = self.pipeline_order.index(first_key)
        second_order_index = self.pipeline_order.index(second_key)

        self.pipeline_order[first_order_index], self.pipeline_order[second_order_index] = (
            self.pipeline_order[second_order_index],
            self.pipeline_order[first_order_index],
        )
        self._refresh_pipeline_order_listbox()

    def _refresh_pipeline_order_listbox(self):
        self.visible_pipeline_keys = [
            key for key in self.pipeline_order if self.pipeline_vars[key].get()
        ]

        self.pipeline_order_listbox.delete(0, tk.END)
        for key in self.visible_pipeline_keys:
            self.pipeline_order_listbox.insert(tk.END, self.pipeline_labels[key])

    def move_pipeline_up(self):
        selected = self.pipeline_order_listbox.curselection()
        if not selected:
            messagebox.showinfo("Info", "Select a filter in the order list.")
            return

        index = selected[0]
        if index == 0:
            return

        self._swap_pipeline_items(index, index - 1)
        self.pipeline_order_listbox.selection_clear(0, tk.END)
        self.pipeline_order_listbox.selection_set(index - 1)

    def move_pipeline_down(self):
        selected = self.pipeline_order_listbox.curselection()
        if not selected:
            messagebox.showinfo("Info", "Select a filter in the order list.")
            return

        index = selected[0]
        last_index = self.pipeline_order_listbox.size() - 1
        if index >= last_index:
            return

        self._swap_pipeline_items(index, index + 1)
        self.pipeline_order_listbox.selection_clear(0, tk.END)
        self.pipeline_order_listbox.selection_set(index + 1)

    def _prepare_preview(self, image, max_width=450, max_height=640):
        preview = image.copy()
        preview.thumbnail((max_width, max_height))
        return ImageTk.PhotoImage(preview)

    def _show_original(self):
        if self.original_image is None:
            self.original_label.config(image="")
            self.original_photo = None
            return

        self.original_photo = self._prepare_preview(self.original_image)
        self.original_label.config(image=self.original_photo)

    def _show_processed(self):
        if self.processed_image is None:
            self.processed_label.config(image="")
            self.processed_photo = None
            return

        self.processed_photo = self._prepare_preview(self.processed_image)
        self.processed_label.config(image=self.processed_photo)

    def load_image(self):
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            loaded = Image.open(path)
            self.original_image = loaded.copy()
            self.processed_image = None
            self._show_original()
            self._show_processed()
            self._set_controls_enabled(True)
            self._push_event("Image loaded")
        except Exception as error:
            self._push_event("Load failed")
            messagebox.showerror("Error", f"Failed to load image:\n{error}")

    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image to save.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            self.processed_image.save(path)
            self._push_event("Result saved")
        except Exception as error:
            self._push_event("Save failed")
            messagebox.showerror("Error", f"Failed to save file:\n{error}")

    def _run_processing(self, processor, name):
        if self.original_image is None:
            messagebox.showwarning("Warning", "Load an image first.")
            return False

        self._set_controls_enabled(False)
        self.root.update_idletasks()

        try:
            self.processed_image = processor(self.original_image)
            self._show_processed()
            return True
        except Exception as error:
            self._push_event(f"Error: {name}")
            messagebox.showerror("Error", f"Error while processing ({name}):\n{error}")
            return False
        finally:
            self._set_controls_enabled(True)

    def run_selected_pipeline(self):
        selected = list(self.visible_pipeline_keys)

        if not selected:
            messagebox.showwarning("Warning", "Select at least one filter in the pipeline.")
            return

        brightness_value = int(self.brightness_scale.get())
        kernel_size = int(self.kernel_scale.get())
        threshold_value = int(self.threshold_scale.get())

        if kernel_size % 2 == 0:
            kernel_size += 1

        def processor(image):
            current = image
            for name in selected:
                if name == "grayscale":
                    current = apply_grayscale(current)
                elif name == "brightness":
                    current = apply_brightness(current, brightness_value)
                elif name == "box":
                    current = apply_box_filter(current, kernel_size)
                elif name == "sobel":
                    current = apply_sobel(current)
                elif name == "threshold":
                    current = apply_threshold(current, threshold_value)
            return current

        pretty_names = {
            "grayscale": self.pipeline_labels["grayscale"],
            "brightness": f"Brightness ({brightness_value})",
            "box": f"Box Filter ({kernel_size})",
            "sobel": self.pipeline_labels["sobel"],
            "threshold": f"Threshold ({threshold_value})",
        }
        completed = self._run_processing(processor, "Pipeline")
        if completed:
            pipeline_lines = [f"- {pretty_names[name]}" for name in selected]
            pipeline_summary = "Done Pipeline:\n" + "\n".join(pipeline_lines)
            self._push_event(pipeline_summary)


def main():
    root = tk.Tk()
    app = ImageProcessingApp(root)
    app._set_controls_enabled(False)
    app.load_button.config(state=tk.NORMAL)
    root.mainloop()


if __name__ == "__main__":
    main()
