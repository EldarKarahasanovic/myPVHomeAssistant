# homeassistant-mypv

Home Assistant Component for AC•THOR of my-PV

<a href="https://buymeacoffee.com/melik787" target="_blank"><img height="41px" width="167px" src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee"></a>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

This repo is actually forked from <a href="https://github.com/zaubererty/homeassistant-mvpv" target="_blank">@zaubererty</a> and implemented some commits from <a href="https://github.com/coccyx00/homeassistant-mvpv" target="_blank">@coccyx00</a>. We still improved this integration by adding more services, improved code and discovery. 

### Installation

Copy this folder to `config/custom_components/mypv/`.

### HACS
You need to install HACS. <a href="https://hacs.xyz/docs/setup/download/" target="_blank">Download HACS</a>

After that go to the 3 dots on HACS --> Custom Repositories --> paste the link of this repository --> select Integration as type --> click on Add
After that it should be available on HACS --> Search my-PV
Install my-PV 

### Configuration

The integration is configurated via UI

BETA * BETA * BETA - Not finished yet - BETA * BETA * BETA

### 1-TODO:
- Complete services
- clean up code
- Test other devices (ELWA, AC•THOR 9s, etc.)
- Autodiscovery

### 2-IN PROGRESS:
-  Implementing hot water assurance
-  Implementing a standard dashboard

### 3-DONE:
- Monitoring of all status values
- Fixed https:// github.com/zaubererty/homeassistant-mvpv/issues/7 (deprecated constants)
- Added icons
- Added button for warm water boost
- Added switch for devmode
- Filtering sensors based on device type