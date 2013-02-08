# Kill Announcer Plugin for [B3](http://www.bigbrotherbot.net/ "BigBrotherBot")

### Features

- Killstreak announcer
- first kill announcer
- Announcements for kills with certain weapons  
  For example, to tell if someone is killed with a knife.
- Random choice of the announcement  
  Define different announcer for an action.

## Usage

### Installation
1. Copy the file [extplugins/killannouncerbf3.py](extplugins/killannouncerbf3.py) into your `b3/extplugins` folder and
[extplugins/conf/plugin_killannouncerbf3.ini](extplugins/conf/plugin_killannouncerbf3.ini) into your `b3/conf` folder

2. Add the following line in your b3.xml file (below the other plugin lines)
```xml
<plugin name="killannouncerbf3" config="@conf/plugin_killannouncerbf3.ini"/>
```

### Settings and Messages
Look into `plugin_killannouncerbf3.ini` file. A detailed description is coming soon.

## FAQ
**Q**: What mean that bf3 in plugin name?  
**A**: The plugin has been tested only on BF3. This does not mean that it does not work well with other games.
