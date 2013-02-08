# Kill Announcer Plugin for [B3](http://www.bigbrotherbot.net/ "BigBrotherBot")

### Features

- Killstreak announcer
- Announcements for kills with certain weapons
  For example, to tell if someone is killed with a knife.
- Random choice of the announcement
  Define different announcer for an action.

## Usage

### Installation
1. Copy the file [extensions/killannouncerbf3.py](extensions/killannouncerbf3.py) into your `b3/extensions` folder and
[extensions/conf/plugin_killannouncerbf3.ini](extensions/conf/plugin_killannouncerbf3.ini) into your `b3/conf` folder

2. Add the following line in your b3.xml file (below the other plugin lines)
```xml
<plugin name="admin" config="@conf/plugin_admin.xml"/>
```

### Settings and Messages
Look into `plugin_killannouncerbf3.xml` file. A detailed description is coming soon.

## FAQ
**Q**: What mean that bf3 in plugin name?
**A**: The plugin has been tested only on BF3. This does not mean that it does not work well with other games.
