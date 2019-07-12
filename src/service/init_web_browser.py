import webbrowser

class WebBrowserProcessForker:
    """
        Start the web browser in a new process.
    """
    def __init__(self, url):
        print("Attempting to open management portal at "+str(url)+" in default web browser.")
        self.web_browser_process = None
        try:
            webbrowser.open(url, new=0, autoraise=True)
        except Exception as e:
            pass
