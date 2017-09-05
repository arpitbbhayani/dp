import os
import traceback

class LocalFS:
    def __init__(self, meta):
        self.directory = meta['directory']

    def provision(self):
        logs = []
        try:
            logs.append(("INFO", "Provisioning LocalFS: " + self.directory))
            if not os.path.isdir(self.directory):
                logs.append(("INFO", "Creating directory: " + self.directory))
                os.makedirs(self.directory)
                logs.append(("INFO", "Created directory: " + self.directory))
            else:
                logs.append(("INFO", "Directory: " + self.directory + " already exists."))

            logs.append(("SUCCESS", "LocalFS Provisioned for directory " + self.directory))
        except Exception as e:
            logs.append(("FAIL", str(e)))
            logs.append(("FAIL", traceback.format_exc()))

        return logs
