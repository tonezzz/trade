# Screen Timeout Configuration

**Last Updated: 2026-08-04**

## Overview

This document describes the configuration for 1-minute screen timeout on both tony-omen and tony-dell machines, including steps to prevent automatic wake-ups from notifications and other system events.

## Problem

Initial attempts to set screen timeout resulted in screens turning off but immediately waking back on due to:
- Conflicting power management configurations (xset vs desktop environment)
- Notification popups triggering screen wake events
- Background scripts re-applying settings and causing interference

## Solution

The solution uses native desktop environment power management combined with notification system disabling to prevent wake events.

## tony-omen (XFCE)

### Power Management Configuration

```bash
# XFCE power manager settings
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac --create --type int --set 60
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled --create --type bool --set true
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-on-ac-sleep --create --type int --set 60
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-battery --create --type int --set 60
```

### Notification System Configuration

```bash
# Disable notification daemon
systemctl --user stop xfce4-notifyd.service

# Configure notification settings
xfconf-query -c xfce4-notifyd -p /expire-timeout --create --type int --set 10
xfconf-query -c xfce4-notifyd -p /notification-log --create --type int --set 0
xfconf-query -c xfce4-notifyd -p /do-not-disturb --create --type bool --set true
xfconf-query -c xfce4-notifyd -p /show-at-startup --create --type bool --set false

# Stop evolution alarm notifications
systemctl --user stop evolution-alarm-notify.service
```

### Autostart Scripts

**Screen Timeout Script** (`~/.config/autostart/screen-off.sh`):
```bash
#!/bin/bash
# Screen timeout script - turns off screen after 1 minute of inactivity
# Run once and exit to avoid interference

sleep 5  # Wait for X to fully initialize

# Set the screen timeout using xset
xset s blank
xset s 60
xset dpms 0 0 60

# Configure XFCE power manager if available
if command -v xfconf-query &> /dev/null; then
    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac --create --type int --set 60 2>/dev/null
    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled --create --type bool --set true 2>/dev/null
    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-on-ac-sleep --create --type int --set 60 2>/dev/null
fi
```

**Disable Notifications Script** (`~/.config/autostart/disable-notify.desktop`):
```ini
[Desktop Entry]
Type=Application
Name=Disable Notifications
Exec=/bin/sh -c 'killall xfce4-notifyd 2>/dev/null; sleep 2; killall xfce4-notifyd 2>/dev/null'
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
```

## tony-dell (LXQT)

### Power Management Configuration

```bash
# LXQT power management config file
# File: ~/.config/lxqt/lxqt-powermanagement.conf
# Key setting: idlenessTime=@Variant(\0\0\0\xf\0\0\0\0x3c)  # 60 seconds
```

### Notification System Configuration

```bash
# Kill LXQT notification daemon
killall lxqt-notificationd

# Prevent it from starting via autostart script
```

### Autostart Scripts

**Screen Timeout Script** (`~/.config/autostart/screen-off.sh`):
```bash
#!/bin/bash
# Screen timeout script - turns off screen after 1 minute of inactivity
# Run once and exit to avoid interference

sleep 5  # Wait for X to fully initialize

# Set the screen timeout using xset
xset s blank
xset s 60
xset dpms 0 0 60

# Configure LXQT power manager if available
if [ -f ~/.config/lxqt/lxqt-powermanagement.conf ]; then
    sed -i 's/idlenessTime=@Variant(\\\\x0\\\\x0\\\\x0\\\\xf\\\\x0\\\\x0\\\\x3\\\\xe8)/idlenessTime=@Variant(\\\\x0\\\\x0\\\\x0\\\\xf\\\\x0\\\\x0\\\\x0\\\\x3c)/' ~/.config/lxqt/lxqt-powermanagement.conf
fi
```

**Disable Notifications Script** (`~/.config/autostart/disable-notify.desktop`):
```ini
[Desktop Entry]
Type=Application
Name=Disable Notifications
Exec=/bin/sh -c 'killall lxqt-notificationd 2>/dev/null; sleep 2; killall lxqt-notificationd 2>/dev/null'
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
```

## Verification

### Check Current Settings

**tony-omen:**
```bash
# Check screen timeout
xset q | grep -E 'timeout|Standby|Suspend|Off'

# Check XFCE power manager settings
xfconf-query -c xfce4-power-manager -l

# Check notification daemon status
systemctl --user status xfce4-notifyd.service
```

**tony-dell:**
```bash
# Check screen timeout (requires DISPLAY)
ssh tony@192.168.1.42 "export DISPLAY=:0 && xset q | grep -E 'timeout|Standby|Suspend|Off'"

# Check LXQT power management config
ssh tony@192.168.1.42 "cat ~/.config/lxqt/lxqt-powermanagement.conf"

# Check notification daemon
ssh tony@192.168.1.42 "ps aux | grep lxqt-notificationd"
```

### Expected Output

Both machines should show:
```
timeout:  60
Standby: 0
Suspend: 0
Off: 60
```

## Troubleshooting

### Screen doesn't turn off
1. Check if screen timeout is set: `xset q`
2. Verify power manager is running: `ps aux | grep power`
3. Check for conflicting settings in desktop environment

### Screen turns off but immediately wakes up
1. Check for notification processes: `ps aux | grep notify`
2. Disable notification daemon temporarily: `killall xfce4-notifyd` or `killall lxqt-notificationd`
3. Check for other wake sources: `cat /proc/acpi/wakeup`

### Settings don't persist after reboot
1. Verify autostart scripts are enabled: Check `~/.config/autostart/`
2. Check script permissions: `chmod +x ~/.config/autostart/screen-off.sh`
3. Ensure scripts are executable and have correct paths

### Notification daemon keeps restarting
1. Check systemd user services: `systemctl --user list-units | grep notify`
2. Mask the service: `systemctl --user mask xfce4-notifyd.service`
3. Use autostart script to kill it on login

## Configuration Files

### tony-omen
- `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml`
- `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-notifyd.xml`
- `~/.config/autostart/screen-off.sh`
- `~/.config/autostart/disable-notify.desktop`
- `~/.config/autostart/screen-timeout.desktop`

### tony-dell
- `~/.config/lxqt/lxqt-powermanagement.conf`
- `~/.config/autostart/screen-off.sh`
- `~/.config/autostart/disable-notify.desktop`
- `~/.config/autostart/screen-timeout.desktop`

## Key Learnings

1. **Use native power management**: Desktop environment power managers work better than xset for preventing wake events
2. **Disable notifications**: Notification popups are a common cause of screen wake-ups
3. **Avoid persistent scripts**: Scripts that continuously re-apply settings can cause interference
4. **Check ACPI wake sources**: Hardware devices can wake the screen from sleep
5. **Test after changes**: Always verify settings take effect and persist across reboots

## Related Documentation

- [Infrastructure Configuration](../../config/infrastructure.yml)
- [Troubleshooting Guide](../../core/TROUBLESHOOTING.md)
- [Operations Knowledge](./README.md)

---

**Configuration Status**: Active on both tony-omen and tony-dell
**Last Verified**: 2026-08-04
**Maintained By**: System Administrator