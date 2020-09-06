
# ArduinoAD8232EKG

A python frontend for an arduino AD8232 based EKG. Noise reduction and baseline correction are included to produce plots such as this:

![Image of HR](https://github.com/ChrisDavi3s/arduino_ekg_gui/blob/master/HR.PNG)



---
## Table of Contents 

- [Intro](#intro)
- [Installation](#installation)
- [Contributing](#contributing)
- [Team](#team)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)


---

## Introduction

- Electode Placement:

![Image of Placement](https://github.com/ChrisDavi3s/arduino_ekg_gui/blob/master/electrode%20placement.png)

- A quick tour:

![Image of Gui](https://github.com/ChrisDavi3s/arduino_ekg_gui/blob/master/gui.PNG)

1.  Select the COM port the arduino is using. Look in device manager under ports.
1.  This will start/stop monitoring the selected port. This does not record anything. You should see data in (4) if connected correctly.
1.  Starts recording of data. When stop is clicked a prompt will come up to save the data as an excel file. This data has been processed. Try not to record for years I have zero idea how well this copes with *large* data sets.
1.  Live graph of incoming raw unfiltered data. Yes it looks choppy but is only intended to be a viewfinder and not the final data.
1.  Close the program and kill any serial connection. 

---

## Installation

**The arduino side**

- Flash the .ino to your arduino. Ensure that all the data pins are correct.
These three lines will need changing depending on which pins you decide to use. If in trouble just search google for a AD8232 arduino wiring diagram :)

```c++
pinMode(10, INPUT); // Setup for leads off detection LO +
pinMode(11, INPUT); // Setup for leads off detection LO -
Serial.println(analogRead(A0));
```

**The python side**

- Anaconda navigator was installed for my setup. Run the 


- All the `code` required to get started
- Images of what it should look like

---

## Contributing

> To get started...

### Step 1

- **Option 1**
    - 🍴 Fork this repo!

- **Option 2**
    - 👯 Clone this repo to your local machine using `https://github.com/joanaz/HireDot2.git`

### Step 2

- **HACK AWAY!** 🔨🔨🔨

### Step 3

- 🔃 Create a new pull request using <a href="https://github.com/joanaz/HireDot2/compare/" target="_blank">`https://github.com/joanaz/HireDot2/compare/`</a>.

---


## FAQ

- **How do I do *specifically* so and so?**
    - No problem! Just do this
    
    (WIP)

---

## Support

To come.
Will actually try to comment some of my code sorry!

---

## Donations (Optional)

- Buy me a coffee if you ever meet me.

---

## License and other important things

- This is not for medical use. I have made this for fun and any results should not be relied on. If in doubt please seek professional medical advice (ie not mine). No responsibility will be accepted for any harm that is caused by use of this code as per the licence agreement. 




