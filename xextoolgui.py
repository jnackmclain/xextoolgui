import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

class XexToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XexTool GUI Wrapper")
        
        # Xex file or directory selection
        self.selection_frame = tk.Frame(root)
        self.selection_frame.pack()
        
        self.file_mode = tk.BooleanVar()
        self.file_mode.set(True)  # Default to single file mode
        
        self.file_radio = tk.Radiobutton(self.selection_frame, text="Single XEX File", variable=self.file_mode, value=True, command=self.toggle_mode)
        self.file_radio.pack(side=tk.LEFT)
        self.dir_radio = tk.Radiobutton(self.selection_frame, text="XEX Directory", variable=self.file_mode, value=False, command=self.toggle_mode)
        self.dir_radio.pack(side=tk.LEFT)
        
        self.xex_path_label = tk.Label(root, text="Select XEX File or Directory:")
        self.xex_path_label.pack()
        self.xex_path_entry = tk.Entry(root, width=50)
        self.xex_path_entry.pack()
        self.xex_path_button = tk.Button(root, text="Browse", command=self.browse_xex)
        self.xex_path_button.pack()
        
        # Options selection
        self.options_frame = tk.Frame(root)
        self.options_frame.pack()
        
        self.option_list = {
            "-l": "Print extended info",
            "-b": "Dump basefile",
            "-i": "Dump to IDC file",
            "-r a": "Remove all limits",
            "-m d": "Convert to devkit",
            "-m r": "Convert to retail",
            "-e u": "Unencrypt XEX",
            "-e e": "Encrypt XEX",
            "-c u": "Uncompress XEX",
            "-c c": "Compress XEX",
        }
        
        self.option_vars = {}
        for opt, desc in self.option_list.items():
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.options_frame, text=desc, variable=var, command=lambda opt=opt: self.toggle_conflicting_options(opt))
            chk.pack(anchor="w")
            self.option_vars[opt] = var
        
        # Output file selection (disabled in directory mode)
        self.output_file_label = tk.Label(root, text="Output XEX File:")
        self.output_file_label.pack()
        self.output_file_entry = tk.Entry(root, width=50)
        self.output_file_entry.pack()
        self.output_file_button = tk.Button(root, text="Browse", command=self.browse_output)
        self.output_file_button.pack()
        
        # Run button
        self.run_button = tk.Button(root, text="Run XexTool", command=self.run_xextool)
        self.run_button.pack()
    
    def toggle_mode(self):
        self.xex_path_entry.delete(0, tk.END)  # Clear selected XEX file or directory
        if self.file_mode.get():
            self.output_file_entry.config(state=tk.NORMAL)
            self.output_file_button.config(state=tk.NORMAL)
        else:
            self.output_file_entry.config(state=tk.DISABLED)
            self.output_file_button.config(state=tk.DISABLED)
    
    def toggle_conflicting_options(self, selected_opt):
        conflict_pairs = {
            "-e u": "-e e",
            "-e e": "-e u",
            "-m d": "-m r",
            "-m r": "-m d",
            "-c u": "-c c",
            "-c c": "-c u",
        }
        
        if selected_opt in conflict_pairs:
            conflicting_opt = conflict_pairs[selected_opt]
            if self.option_vars[selected_opt].get():
                self.option_vars[conflicting_opt].set(False)
        
        # Ensure output file is mandatory if any option other than -l is selected
        if any(var.get() for opt, var in self.option_vars.items() if opt != "-l") and self.file_mode.get():
            self.output_file_entry.config(state=tk.NORMAL)
            self.output_file_button.config(state=tk.NORMAL)
        elif self.file_mode.get():
            self.output_file_entry.config(state=tk.DISABLED)
            self.output_file_button.config(state=tk.DISABLED)
    
    def browse_xex(self):
        if self.file_mode.get():
            filename = filedialog.askopenfilename(filetypes=[("XEX Files", "*.xex")])
        else:
            filename = filedialog.askdirectory()
        if filename:
            self.xex_path_entry.delete(0, tk.END)
            self.xex_path_entry.insert(0, filename)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xex", filetypes=[("XEX Files", "*.xex")])
        if filename:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, filename)
    
    def run_xextool(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        xextool_path = os.path.join(script_dir, "xextool.exe")
        
        if sys.platform == "darwin":  # macOS
            cmd_prefix = ["/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine", xextool_path]
        elif sys.platform == "linux":  # Linux
            cmd_prefix = ["wine", xextool_path]
        else:  # Windows
            cmd_prefix = [xextool_path]
        
        xex_file = self.xex_path_entry.get().strip()
        if not xex_file:
            messagebox.showerror("Error", "Please select a XEX file or directory.")
            return
        
        cmd = cmd_prefix[:]
        for opt, var in self.option_vars.items():
            if var.get():
                cmd.append(opt)
        
        if self.file_mode.get():
            output_file = self.output_file_entry.get().strip()
            if not output_file and any(var.get() for opt, var in self.option_vars.items() if opt != "-l"):
                messagebox.showerror("Error", "Output XEX file is required.")
                return
            if output_file:
                cmd.extend(["-o", output_file])
            cmd.append(xex_file)
            self.execute_command(cmd)
        else:
            for root, _, files in os.walk(xex_file):
                for file in files:
                    if file.endswith(".xex"):
                        xex_path = os.path.join(root, file)
                        backup_file = xex_path + "_backup"
                        if not os.path.exists(backup_file):
                            os.rename(xex_path, backup_file)
                        
                        cmd = cmd_prefix[:]
                        for opt, var in self.option_vars.items():
                            if var.get():
                                cmd.append(opt)
                        cmd.extend(["-o", xex_path, backup_file])
                        self.execute_command(cmd)
    
    def execute_command(self, cmd):
        try:
            process = subprocess.run(cmd, check=True, text=True, capture_output=True)
            print("XexTool Output:\n", process.stdout.strip())
            print("XexTool Errors:\n", process.stderr.strip())
        except subprocess.CalledProcessError as e:
            print("XexTool Execution Failed:\n", e.stderr)
            messagebox.showerror("Error", f"XexTool execution failed:\n{e.stderr}")

if __name__ == "__main__":
    root = tk.Tk()
    app = XexToolGUI(root)
    root.mainloop()
