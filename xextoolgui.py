import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

class XexToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XexTool GUI Wrapper")
        
        # Xex file selection
        self.xex_file_label = tk.Label(root, text="Select XEX File:")
        self.xex_file_label.pack()
        self.xex_file_entry = tk.Entry(root, width=50)
        self.xex_file_entry.pack()
        self.xex_file_button = tk.Button(root, text="Browse", command=self.browse_xex)
        self.xex_file_button.pack()
        
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
            "-o": "Output XEX file"
        }
        
        self.option_vars = {}
        for opt, desc in self.option_list.items():
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.options_frame, text=desc, variable=var)
            chk.pack(anchor="w")
            self.option_vars[opt] = var
        
        # Output file selection
        self.output_file_label = tk.Label(root, text="Output XEX File (optional):")
        self.output_file_label.pack()
        self.output_file_entry = tk.Entry(root, width=50)
        self.output_file_entry.pack()
        self.output_file_button = tk.Button(root, text="Browse", command=self.browse_output)
        self.output_file_button.pack()
        
        # Run button
        self.run_button = tk.Button(root, text="Run XexTool", command=self.run_xextool)
        self.run_button.pack()
    
    def browse_xex(self):
        filename = filedialog.askopenfilename(filetypes=[("XEX Files", "*.xex")])
        if filename:
            self.xex_file_entry.delete(0, tk.END)
            self.xex_file_entry.insert(0, filename)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xex", filetypes=[("XEX Files", "*.xex")])
        if filename:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, filename)
    
    def run_xextool(self):
        xex_file = self.xex_file_entry.get().strip()
        if not xex_file:
            messagebox.showerror("Error", "Please select a XEX file.")
            return
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        xextool_path = os.path.join(script_dir, "xextool.exe")
        
        if sys.platform == "darwin":  # macOS
            cmd = ["/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine", xextool_path]
        elif sys.platform == "linux":  # Linux
            cmd = ["wine", xextool_path]
        else:  # Windows
            cmd = [xextool_path]
        
        for opt, var in self.option_vars.items():
            if var.get():
                if opt == "-o":
                    output_file = self.output_file_entry.get().strip()
                    if output_file:
                        cmd.extend([opt, output_file])
                else:
                    cmd.append(opt)
        
        cmd.append(xex_file)
        
        try:
            process = subprocess.run(cmd, check=True, text=True, capture_output=True)
            output = process.stdout.strip()
            error_output = process.stderr.strip()
            
            if output:
                print("XexTool Output:\n", output)
            if error_output:
                print("XexTool Errors:\n", error_output)
            
            messagebox.showinfo("Success", "XexTool executed successfully.")
        except subprocess.CalledProcessError as e:
            print("XexTool Execution Failed:\n", e.stderr)
            messagebox.showerror("Error", f"XexTool execution failed:\n{e.stderr}")

if __name__ == "__main__":
    root = tk.Tk()
    app = XexToolGUI(root)
    root.mainloop()
