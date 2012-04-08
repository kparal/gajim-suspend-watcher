=======================
 gajim-suspend-watcher
=======================

Fix for `Gajim IM <http://gajim.org/>`_ to disconnect accounts before machine suspend and reconnect them after machine resume.

This was written for GNOME, but it could work also for other environments with UPower and NetworkManager.

Note: Gajim 0.15+ now correctly disconnects accounts before suspend, but it does not still auto-reconnect after resume, so this script is still needed.


Usage
=====

See ``$ ./gajim-suspend-watcher.py --help``.

Auto-start this script on your login (``~/.config/autostart``).


License
=======

This program is a free software, licensed under `GNU AGPL 3 <http://www.gnu.org/licenses/agpl-3.0.html>`_.


Contact
=======

Visit https://github.com/kparal/gajim-suspend-watcher .


Donations
=========

If you like this program you can `Flattr me <https://flattr.com/profile/kamil.paral>`_.

.. image:: http://api.flattr.com/button/flattr-badge-large.png
   :target: https://flattr.com/profile/kamil.paral
