# MBOX-EMBEDDED-TOOLKIT

[insert banner image here]

MBOX is a desktop application designed for developers working with embedded systems. It simplifies the debugging and testing process by providing servers and clients for popular protocols such as HTTP, UDP, TCP, and MQTT, as well as an advanced serial monitor and serial plotter. The app is built using PyQt6, which is a Python binding for the Qt application development framework. MBOX has an easy-to-navigate user interface that allows developers to quickly and easily configure servers and clients for the protocols they need. The advanced serial monitor and serial plotter are designed to be user-friendly, with features such as real-time data visualization and automatic scaling of graphs for improved data analysis.

[insert sample image here]

# Features

- **HTTP Server and Client**
  - Set up an HTTP server with one click.
  - Easy file hosting for an OTA or Audio server.
  - Dedicated console for debugging.
- **UDP/TCP Server and Client**
  - Change the response without stopping the connection.
  - Handle multiple connections at once.
- **MQTT Server and Client**.
  - Easily configure and publish MQTT servers locally (requires the Mosquito MQTT broker).
  - Subscibe to any topic on the go.
- **Advanced Serial Monitor**
  - Full fledged serial monitor with all advanced control.
  - Real time filer option.
  - Console with regex decoding depending on various microcontrollers.
- **Serial Plotter**
  - Arduino like serial plotter, which can be implemented with any microcontroller framework.
  - Live customization for the graph.
  - Adjust speed and time.
 
**More features are on the way**



# Installation.

The MBOX toolkit is written in Python 3 with the QT6 framework. The script requires the installation of Python 3.10 or higher.

### Step 1.
**Install Python 3, Git, and Mosquito.

**Debian.**
 ```bash
 sudo apt install python3 git mosquito -y
 ```
 **Windows.**
Install GIT form [here] (https://git-scm.com/download/win).
Install Python 3 from [here](https://www.python.org/downloads/windows/)
Install Mosquito from [here] (https://mosquitto.org/download/).

### Step 2.
Clone this repo

```bash
git clone https://github.com/TECHPROGENY/MBOX-EMBEDDED-TOOLKIT/
```

### Step 3.
Run the installation script.

```bash
cd MBOX-EMBEDDED-TOOLKIT
```

```bash
python3 setup.py
```

### Step 4.
launch the app.
```bash
python3 mbox.py
```

# Tutorials.
- [MQTT Client and Server] (YouTube link here)
- [HTTP Client and Server] (YouTube link here)
- [TCP Client and Server] (YouTube link here)
- [UDP Client and Server] (YouTube link here)
- [Serial Monitor] (YouTube link here)
- [Serial Plotter] (YouTube link here)

## Serial plotter C code for microcontrollers

This code snippet reads the analog value from CHANNEL_0 and prints the value using the "MPLOT" keyword, which is intercepted by the MBOX plotter to plot the graph.

```c

void app_main(void)
{
    adc1_config_width(ADC_WIDTH_BIT_10);
    while (true)
    {
        int x = adc1_get_raw(ADC1_CHANNEL_0);
        printf("MPLOT:%d\n",x);
        vTaskDelay(pdMS_TO_TICKS(100));
    }

}

```

# Contribution Guidelines
MBOX is an open source project that welcomes contributions from the community. Here are some guidelines to follow when making contributions:

Fork the repository and make your changes on a new branch.
Ensure that your changes do not break existing functionality and are consistent with the goals of the project.
Write clear commit messages and use descriptive comments to explain your changes.
Submit a pull request with your changes.
The MBOX team will review your changes and merge them if they meet the project's standards. Thank you for your contributions!

# License
MBOX is licensed under the GNU General Public License (GPL), which is a free and open-source software license. This means that the software is free to use, modify, and distribute, as long as any derivative works are also licensed under the GPL. By contributing to MBOX, you agree to license your contributions under the GPL as well.
