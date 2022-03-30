"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

UNREADY = 0
RUNNABLE = 1
RUNNING = 2
PAUSED = 3

StateName = {0: "UNREADY", 1: "RUNNABLE", 2: "RUNNING", 3: "PAUSED"}
