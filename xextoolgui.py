import os
import shutil
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
        
        self.file_radio = tk.Radiobutton(
            self.selection_frame, text="Single XEX File", 
            variable=self.file_mode, value=True, command=self.toggle_mode)
        self.file_radio.pack(side=tk.LEFT)
        self.dir_radio = tk.Radiobutton(
            self.selection_frame, text="XEX Directory", 
            variable=self.file_mode, value=False, command=self.toggle_mode)
        self.dir_radio.pack(side=tk.LEFT)
        
        self.xex_path_label = tk.Label(root, text="Select XEX File or Directory:")
        self.xex_path_label.pack()
        self.xex_path_entry = tk.Entry(root, width=50)
        self.xex_path_entry.pack()
        self.xex_path_button = tk.Button(root, text="Browse", command=self.browse_xex)
        self.xex_path_button.pack()
        
        # New "Patch for BadUpdate" checkbutton positioned under the input browse button.
        self.badupdate_var = tk.BooleanVar()
        self.badupdate_check = tk.Checkbutton(
            root, text="Patch for BadUpdate", variable=self.badupdate_var, command=self.toggle_badupdate)
        self.badupdate_check.pack(pady=5)
        
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
            chk = tk.Checkbutton(
                self.options_frame, text=desc, variable=var,
                command=lambda opt=opt: self.toggle_conflicting_options(opt))
            chk.pack(anchor="w")
            self.option_vars[opt] = var
        
        # Patch file selection (layout similar to output file selector)
        self.patch_file_label = tk.Label(root, text="Select Patch File (.xexp):", anchor="center")
        self.patch_file_label.pack()
        self.patch_file_entry = tk.Entry(root, width=50)
        self.patch_file_entry.pack()
        self.patch_file_button = tk.Button(root, text="Browse", command=self.browse_patch_file)
        self.patch_file_button.pack()
        
        # Output file selection (disabled in directory mode)
        self.output_file_label = tk.Label(root, text="Output XEX File:", anchor="center")
        self.output_file_label.pack()
        self.output_file_entry = tk.Entry(root, width=50)
        self.output_file_entry.pack()
        self.output_file_button = tk.Button(root, text="Browse", command=self.browse_output)
        self.output_file_button.pack()
        
        # Run button
        self.run_button = tk.Button(root, text="Run XexTool", command=self.run_xextool)
        self.run_button.pack(pady=10)
    
    def toggle_badupdate(self):
        """When 'Patch for BadUpdate' is toggled on, reset all flags except -m r and -r a."""
        if self.badupdate_var.get():
            for opt, var in self.option_vars.items():
                if opt in ["-m r", "-r a"]:
                    var.set(True)
                else:
                    var.set(False)
    
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
        if selected_opt not in ["-m r", "-r a"]:
            if self.badupdate_var.get():
                self.badupdate_var.set(False)
        if self.file_mode.get():
            if any(var.get() for opt, var in self.option_vars.items() if opt != "-l"):
                self.output_file_entry.config(state=tk.NORMAL)
                self.output_file_button.config(state=tk.NORMAL)
            else:
                self.output_file_entry.config(state=tk.DISABLED)
                self.output_file_button.config(state=tk.DISABLED)
    
    def toggle_mode(self):
        self.xex_path_entry.delete(0, tk.END)
        if self.file_mode.get():
            self.patch_file_label.config(text="Select Patch File (.xexp):")
            self.output_file_label.config(text="Output XEX File:")
            self.patch_file_entry.config(state=tk.NORMAL)
            self.patch_file_button.config(state=tk.NORMAL)
            self.output_file_entry.config(state=tk.NORMAL)
            self.output_file_button.config(state=tk.NORMAL)
        else:
            self.patch_file_label.config(text="default.xexp will be used if exists next to default.xex")
            self.output_file_label.config(text="original .xex will be named .xex_backup")
            self.patch_file_entry.delete(0, tk.END)
            self.patch_file_entry.config(state=tk.DISABLED)
            self.patch_file_button.config(state=tk.DISABLED)
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
    
    def browse_patch_file(self):
        filename = filedialog.askopenfilename(filetypes=[("XEXP Files", "*.xexp")])
        if filename:
            self.patch_file_entry.delete(0, tk.END)
            self.patch_file_entry.insert(0, filename)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xex", filetypes=[("XEX Files", "*.xex")])
        if filename:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, filename)
    
    def run_xextool(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        xextool_path = os.path.join(script_dir, "xextool.exe")
        if sys.platform == "darwin":
            cmd_prefix = ["/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine", xextool_path]
        elif sys.platform == "linux":
            cmd_prefix = ["wine", xextool_path]
        else:
            cmd_prefix = [xextool_path]
        
        xex_file = self.xex_path_entry.get().strip()
        if not xex_file:
            messagebox.showerror("Error", "Please select a XEX file or directory.")
            return
        
        # Build a queue of commands to run.
        command_queue = []
        if self.file_mode.get():
            # Single file mode.
            cmd = cmd_prefix[:]
            for opt, var in self.option_vars.items():
                if var.get():
                    cmd.append(opt)
            patch_file = self.patch_file_entry.get().strip()
            output_file = self.output_file_entry.get().strip()
            if patch_file:
                if not output_file:
                    messagebox.showerror("Error", "Output XEX file is required when patching.")
                    return
                # Command order: -p patch.xexp -o output.xex -u input.xex
                cmd.append("-p")
                cmd.append(patch_file)
                cmd.extend(["-o", output_file])
                cmd.append("-u")
                cmd.append(xex_file)
            else:
                if output_file:
                    cmd.extend(["-o", output_file])
                cmd.append(xex_file)
            command_queue.append(cmd)
        else:
            # Directory mode.
            for root_dir, _, files in os.walk(xex_file):
                for file in files:
                    if file.lower().endswith(".xex"):
                        xex_path = os.path.join(root_dir, file)
                        backup_file = xex_path + "_backup"
                        # Duplicate the file so that we have a backup.
                        if not os.path.exists(backup_file):
                            shutil.copy2(xex_path, backup_file)
                        
                        file_cmd = cmd_prefix[:]
                        for opt, var in self.option_vars.items():
                            if var.get():
                                file_cmd.append(opt)
                        
                        # Check for auto-detected patch file (same basename with .xexp extension).
                        patch_candidate = os.path.splitext(xex_path)[0] + ".xexp"
                        if os.path.exists(patch_candidate):
                            file_cmd.append("-p")
                            file_cmd.append(patch_candidate)
                            file_cmd.extend(["-o", xex_path])
                            file_cmd.append("-u")
                            file_cmd.append(backup_file)
                        else:
                            file_cmd.extend(["-o", xex_path, backup_file])
                        command_queue.append(file_cmd)
        
        # Execute all queued commands in one sweep.
        for cmd in command_queue:
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
