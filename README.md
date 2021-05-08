<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/GaryCastillo8/Morazan-Tracking-Software">
    <img src="Logo_Morazan.png" alt="Logo" width="250" height="200">
  </a>

  <h3 align="center">MORAZAN TRACKING SOFTWARE</h3>

  <p align="center">
   
    <br />
    <a href="https://github.com/GaryCastillo8/Morazan-Tracking-Software"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/GaryCastillo8/Morazan-Tracking-Software">View Demo</a>
    ·
    <a href="https://github.com/GaryCastillo8/Morazan-Tracking-Softwaree/issues">Report Bug</a>
    ·
    <a href="https://github.com/GaryCastillo8/Morazan-Tracking-Software/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![MTS](https://raw.githubusercontent.com/GaryCastillo8/Morazan-Tracking-Software/main/img/tracking1.png)

MTS is a tracking and orbit propagator software. Shows the world map with the position of the CubeSat and Cabañas ground station, located in Tegucigalpa, Honduras. It also display the CubeSat trajectory and coverage in real time.

The main purposes:
* Show the real-time location of the satellite
* Find its orbital parameters
* Show the visibility window
* To know the events above Central America and Cabañas ground station

Is based on others professional Tracking Softwares like Pypredict, GPredict and Orbitron.

### Built With

* [Python](https://www.python.org)
* [Pypredict](https://github.com/spel-uchile/Pypredict)


<!-- GETTING STARTED -->
## Getting Started

You can use this software to follow the ISS and many other CubeSats.

### Prerequisites

If you have any trouble during the installation of the packages, you can also install them one by one.

* [PyQt5](https://pypi.org/project/PyQt5/)
* [shapely](https://github.com/simplegeo/shapely)
* [cartopy](https://github.com/SciTools/cartopy)
* [cython](https://github.com/cython/cython)
* [geos](https://github.com/grst/geos)
* [matplotlib](https://github.com/matplotlib/matplotlib)
* [numpy](https://github.com/numpy/numpy)
* [Pillow](https://github.com/python-pillow/Pillow)
* [pykdtree](https://github.com/storpipfugl/pykdtree)
* [pymongo](https://github.com/mongodb/mongo-python-driver)
* [pyshp](https://github.com/GeospatialPython/pyshp)
* [scipy](https://github.com/scipy/scipy)
* [sgp4](https://github.com/brandon-rhodes/python-sgp4)

### Installation

1. Clone the repository
   ```sh
   git clone https://github.com/GaryCastillo8/Morazan-Tracking-Software.git
   ```
2. Move to Morazan Tracking Software folder
   ```sh
   cd /'Morazan Tracking Software'
 
   
3. Install packages
   ```sh
   sudo sh install.sh
   pip3 install --upgrade pip
   ```
4. Install MTS
   ```sh
   pip3 install . --no-binary shapely


<!-- USAGE EXAMPLES -->
## Usage

You can view the trajectories of the CubeSats, the south atlantic anomaly and their coverage. There is a buttom for each one.



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/GaryCastillo8/Morazan-Tracking-Software/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the GPL-3.0 License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Christopher Gary Castillo - garycastilloc8@gmail.com

Project Link: [https://github.com/GaryCastillo8/Morazan-Tracking-Software](https://github.com/GaryCastillo8/Morazan-Tracking-Software)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

Thanks to the softwares are shown below:

* [Gpredict](http://gpredict.oz9aec.net/)
* [Pypredict](https://github.com/spel-uchile/Pypredict)
* Orbitron

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/GaryCastillo8/Morazan-Tracking-Software.svg?style=for-the-badge
[contributors-url]: https://github.com/GaryCastillo8/Morazan-Tracking-Software/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/GaryCastillo8/Morazan-Tracking-Software.svg?style=for-the-badge
[forks-url]: https://github.com/GaryCastillo8/Morazan-Tracking-Software/network/members
[stars-shield]: https://img.shields.io/github/stars/GaryCastillo8/Morazan-Tracking-Software.svg?style=for-the-badge
[stars-url]: https://github.com/GaryCastillo8/Morazan-Tracking-Software/stargazers
[issues-shield]: https://img.shields.io/github/issues/GaryCastillo8/Morazan-Tracking-Software.svg?style=for-the-badge
[issues-url]: https://github.com/GaryCastillo8/Morazan-Tracking-Software/issues
[license-shield]: https://img.shields.io/github/license/GaryCastillo8/Morazan-Tracking-Software.svg?style=for-the-badge
[license-url]: https://github.com/GaryCastillo8/Morazan-Tracking-Software/blob/master/LICENSE.txt
