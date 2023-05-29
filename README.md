# EMBOX-EMBEDDED-TOOLKIT

![banner image](https://github.com/TECHPROGENY/embox-embedded-toolkit/blob/main/files/banner.png)

EMBOX is a desktop application designed for developers working with embedded systems. It simplifies the debugging and testing process by providing servers and clients for popular protocols such as HTTP, UDP, TCP, and MQTT, as well as an advanced serial monitor and serial plotter. The app is built using PyQt6, which is a Python binding for the Qt application development framework. EMBOX has an easy-to-navigate user interface that allows developers to quickly and easily configure servers and clients for the protocols they need. The advanced serial monitor and serial plotter are designed to be user-friendly, with features such as real-time data visualization, and automatic scaling of graphs for improved data analysis.

![home page](https://github.com/TECHPROGENY/embox-embedded-toolkit/blob/main/files/start-up.png)
![serial plotter](https://github.com/TECHPROGENY/embox-embedded-toolkit/blob/main/files/plotter.png)

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

The EMBOX toolkit is written in Python 3 with the QT6 framework. The script requires the installation of Python 3.10 or higher.

**Install Python 3, Git, and Mosquito.

# METHOD 1: Binary installation.
### Step 1.

**Debian.**
 ```bash
 sudo apt install python3 mosquito -y
 ```
 **Windows.**
Install Python 3 from the oficial microsoft store.
Install Mosquito from [here](https://mosquitto.org/download/).

### Step 2.

Download and insatll the package from the release section.
**Debian.**
 ```bash
dpkg -i embox.deb
 ```
 **Windows.**
launch the exe directly no installaton required.

# METHOD 2: Build from source.
### Step 1.

**Debian.**
 ```bash
 sudo apt install python3 git mosquito -y
 ```
 **Windows.**
Install GIT form [here](https://git-scm.com/download/win).
Install Python 3 from the oficial microsoft store.
Install Mosquito from [here](https://mosquitto.org/download/).
### Step 2.
Clone this repo

```bash
git clone https://github.com/TECHPROGENY/embox-embedded-toolkit.git
```

### Step 3.
Chnage to cloned directory and Install python modules.

```bash
cd embox-embedded-toolkit
```

```bash
pip install -r requirements.txt
```

### Step 4.
launch the app.
```bash
python3 embox.py
```

# Tutorials.
- [OTA server example](https://youtu.be/R-KDr5iDOCk)
- [MQTT Client and Server] (Comming soon)
- [TCP Client and Server] (Comming soon)
- [Serial Monitor] (Comming soon)
- [Serial Plotter] (Comming soon)

## Serial plotter C code for microcontrollers

This code snippet reads the analog value from CHANNEL_0 and prints the value using the "MPLOT" keyword, which is intercepted by the EMBOX plotter to plot the graph.

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
EMBOX is an open source project which welcomes contributions from the community. Here are some guidelines to follow while making contributions:

Fork the repository and make your changes on a new branch.
Ensure that your changes do not break existing functionality and are consistent with the goals of the project.
Write clear commit messages and use descriptive comments to explain your changes.
Submit a pull request with your changes.
The EMBOX team will review your changes and merge them if they meet the project's standards. Thank you for your contributions!

# License
EMBOX is licensed under the GNU General Public License (GPL), which is a free and open-source software license. This means that the software is free to use, modify, and distribute, as long as any derivative works are also licensed under the GPL. By contributing to EMBOX, you agree to license your contributions under the GPL as well.
