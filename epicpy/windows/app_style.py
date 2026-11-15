# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

import qdarktheme


def set_light_style(app_instance):
    app_instance.setStyle("Fusion")
    app_instance.setStyleSheet("")


def set_dark_style(app_instance):
    app_instance.setStyleSheet(qdarktheme.load_stylesheet("dark"))
