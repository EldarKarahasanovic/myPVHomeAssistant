# my-PV Home Assistant Integration

Home Assistant integration for my-PV

<a href="https://buymeacoffee.com/melik787" target="_blank"><img height="41px" width="167px" src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee"></a>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

This repo is actually forked from <a href="https://github.com/zaubererty/homeassistant-mvpv" target="_blank">@zaubererty</a> and implemented some commits from <a href="https://github.com/coccyx00/homeassistant-mvpv" target="_blank">@coccyx00</a>. We still improved this integration by adding more services, improved code and discovery. 

### Installation

There are 2 ways how to install thw my-PV Home Assistant integration

- Manual installation
Copy this folder to `config/custom_components/mypv/`.

- HACS
You need to install HACS. <a href="https://hacs.xyz/docs/setup/download/" target="_blank">Download HACS</a><br>
After that go to the 3 dots on HACS --> Custom Repositories --> paste the link of this repository --> select Integration as type --> click on Add
After that it should be available on HACS --> Search my-PV --> Install my-PV 

### Configuration

The integration is configurated via UI (recommended) or via configuration.yaml 

To implement recommended user interface: <br>
In dashboard go to: edit -> 3 dots -> raw- configuration editor <br>
Paste following code and replace entities based on your device:
<details>
<summary>Code</summary>
  
```ruby
views:
  - title: Home
    cards:
      - type: vertical-stack
        cards:
          - type: gauge
            entity: sensor.ac_elwa_2_192_168_12_51_power1_solar
            needle: false
            max: 3500
          - type: history-graph
            entities:
              - entity: sensor.ac_elwa_2_192_168_12_51_temperatur_1
          - type: entities
            entities:
              - entity: number.hot_water_assurance_192_168_12_51
          - show_name: true
            show_icon: true
            type: button
            tap_action:
              action: toggle
            icon_height: 30px
            entity: button.single_boost
            icon: mdi:thermometer
          - type: horizontal-stack
            cards:
              - type: button
                tap_action:
                  action: toggle
                entity: switch.device_state
                icon_height: 40px
                name: Power
                margin: 5px
              - type: button
                tap_action:
                  action: toggle
                entity: button.boost_button
                icon_height: 40px
                name: Boost
          - type: entity
            entity: sensor.ac_elwa_2_192_168_12_51_screen_mode
            name: Status
```
</details>
Preview:<br>
<img height = "600" width ="350" src = "https://github.com/user-attachments/assets/4d01b350-48f4-4f63-8885-3d4442b7d389">

### 1-TODO:
- clean up and testing code
- PR to the Home Assistant Core

### 2-IN PROGRESS:
- Release to HACS

### 3-DONE:
- Monitoring of all status values
- Fixed <a href="https://github.com/zaubererty/homeassistant-mvpv/issues/7" target="_blank">issue #7 from @zaubererty</a> (deprecated constants)
- Added icons
- Added button for warm water boost
- Added switch for devmode
- Filtering sensors based on device type
- Autodiscovery (inofficial)
- Configuring sensors
- Added hot water assurance, configurable via slider and "Single Boost" button 
- Display screen mode of my-PV devices
- Test other devices (my-PV WiFi Meter, AC ELWA-E)

