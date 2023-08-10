import sys
from cefpython3 import cefpython as cef
import platform
import base64

# Define the HTML content for the application
html_content = """
<!DOCTYPE html>
<html>
<head>
<title>CEFPython Simple App</title>
</head>
<body>
<input type="text" id="inputBox" placeholder="Type something...">
<button id="submitButton">Submit</button>
<div id="output"></div>
<script>
    document.getElementById("submitButton").addEventListener("click", function() {
        var inputText = document.getElementById("inputBox").value;
        document.getElementById("output").textContent = "You entered: " + inputText;
    });
</script>
</body>
</html>
"""


def js_print(browser, lang, event, msg):
    # Execute Javascript function "js_print"
    browser.ExecuteFunction("js_print", lang, event, msg)


def html_to_data_uri(html, js_callback=None):
    # This function is called in two ways:
    # 1. From Python: in this case value is returned
    # 2. From Javascript: in this case value cannot be returned because
    #    inter-process messaging is asynchronous, so must return value
    #    by calling js_callback.
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    ret = "data:text/html;base64,{data}".format(data=b64)
    if js_callback:
        js_print(js_callback.GetFrame().GetBrowser(),
                 "Python", "html_to_data_uri",
                 "Called from Javascript. Will call Javascript callback now.")
        js_callback.Call(ret)
    else:
        return ret


class SimpleApp:
    def __init__(self):
        # Initialize CEF
        sys.excepthook = cef.ExceptHook
        settings = {
            "log_severity": cef.LOGSEVERITY_INFO,
            "log_file": "cef.log",
            "product_version": "SimpleApp/0.1",
            "remote_debugging_port": 0,
        }
        cef.Initialize(settings)

        window_info = cef.WindowInfo()
        window_info.SetAsChild(0, [0, 0, 800, 600])
        self.browser = cef.CreateBrowserSync(
            url=html_to_data_uri(html_content),
            window_title="Simple App",
            window_info=window_info  # Pass the window_info parameter
        )

        # Set the close handler
        self.browser.SetClientHandler(CloseHandler())

    def run(self):
        # Run the CEF message loop
        cef.MessageLoop()

        # Clean up CEF
        cef.Shutdown()


class CloseHandler:
    def OnBeforeClose(self, browser):
        cef.QuitMessageLoop()


if __name__ == "__main__":
    app = SimpleApp()
    app.run()
