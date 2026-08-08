### VERIFICATION STRATEGY: LINUX ADMINISTRATION (ARCH LINUX / POSIX)
1. **Command Safety:** Check for destructive flags (e.g., `rm -rf`, uncontrolled `sudo`, modification of `/etc/fstab` or bootloaders).
2. **Distribution Specifics:** Prioritize `pacman`, `systemd`, and standard utilities (`paccache`, etc.) on Arch Linux.
3. **Data Protection:** Verify mount paths, disk UUIDs, and file permissions.
4. **Halt Condition:** Halt generation via `missing_info` if critical system data (UUID, disk name, mount point) is missing.
