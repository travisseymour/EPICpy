"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EPICpy.
If not, see <https://www.gnu.org/licenses/>.
"""

from uifiles.sndtextsettingsui import Ui_DialogSndTextSettings
from PySide2.QtWidgets import QDialog
import config


class SoundTextSettingsWin(QDialog):
    def __init__(self, context):
        super(SoundTextSettingsWin, self).__init__()
        self.context = context
        self.ok = False
        self.ui = Ui_DialogSndTextSettings()
        self.ui.setupUi(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )

        if "sndtextsettingswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["sndtextsettingswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        self.setLayout(self.ui.verticalLayout)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["sndtextsettingswindow"] = [
            self.width(),
            self.height(),
        ]
        config.save_app_config(quiet=True)
        super(SoundTextSettingsWin, self).resizeEvent(event)

    def setup_options(self):
        self.ui.checkBoxSoundKind.setChecked(config.device_cfg.sound_text_kind)
        self.ui.checkBoxSoundStream.setChecked(config.device_cfg.sound_text_stream)
        self.ui.checkBoxSoundTimbre.setChecked(config.device_cfg.sound_text_timbre)
        self.ui.checkBoxSoundLoudness.setChecked(config.device_cfg.sound_text_loudness)

        self.ui.checkBoxSpeechKind.setChecked(config.device_cfg.speech_text_kind)
        self.ui.checkBoxSoundStream.setChecked(config.device_cfg.speech_text_stream)
        self.ui.checkBoxSpeechPitch.setChecked(config.device_cfg.speech_text_pitch)
        self.ui.checkBoxSpeechLoudness.setChecked(
            config.device_cfg.speech_text_loudness
        )
        self.ui.checkBoxSpeechContent.setChecked(config.device_cfg.speech_text_content)
        self.ui.checkBoxSpeechSpeaker.setChecked(config.device_cfg.speech_text_speaker)
        self.ui.checkBoxSpeechGender.setChecked(config.device_cfg.speech_text_gender)

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True

        config.device_cfg.sound_text_kind = self.ui.checkBoxSoundKind.isChecked()
        config.device_cfg.sound_text_stream = self.ui.checkBoxSoundStream.isChecked()
        config.device_cfg.sound_text_timbre = self.ui.checkBoxSoundTimbre.isChecked()
        config.device_cfg.sound_text_loudness = (
            self.ui.checkBoxSoundLoudness.isChecked()
        )

        config.device_cfg.speech_text_kind = self.ui.checkBoxSpeechKind.isChecked()
        config.device_cfg.speech_text_stream = self.ui.checkBoxSpeechStream.isChecked()
        config.device_cfg.speech_text_pitch = self.ui.checkBoxSpeechPitch.isChecked()
        config.device_cfg.speech_text_loudness = (
            self.ui.checkBoxSpeechLoudness.isChecked()
        )
        config.device_cfg.speech_text_content = (
            self.ui.checkBoxSpeechContent.isChecked()
        )
        config.device_cfg.speech_text_speaker = (
            self.ui.checkBoxSpeechSpeaker.isChecked()
        )
        config.device_cfg.speech_text_gender = self.ui.checkBoxSpeechGender.isChecked()

        self.close()
