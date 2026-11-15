# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from PySide6.QtWidgets import QDialog

from epicpy.uifiles.snd_text_settings_ui import Ui_DialogSndTextSettings
from epicpy.utils import config
from epicpy.utils.app_utils import clear_font


class SoundTextSettingsWin(QDialog):
    def __init__(self):
        super(SoundTextSettingsWin, self).__init__()
        self.ok = False
        self.ui = Ui_DialogSndTextSettings()
        self.ui.setupUi(self)

        # replace designed font with application-wide font
        clear_font(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

        if "sndtextsettingswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["sndtextsettingswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["sndtextsettingswindow"] = [
            self.width(),
            self.height(),
        ]
        super(SoundTextSettingsWin, self).resizeEvent(event)

    def setup_options(self):
        self.ui.checkBoxSoundKind.setChecked(config.device_cfg.sound_text_kind)
        self.ui.checkBoxSoundStream.setChecked(config.device_cfg.sound_text_stream)
        self.ui.checkBoxSoundTimbre.setChecked(config.device_cfg.sound_text_timbre)
        self.ui.checkBoxSoundLoudness.setChecked(config.device_cfg.sound_text_loudness)

        self.ui.checkBoxSpeechKind.setChecked(config.device_cfg.speech_text_kind)
        self.ui.checkBoxSoundStream.setChecked(config.device_cfg.speech_text_stream)
        self.ui.checkBoxSpeechPitch.setChecked(config.device_cfg.speech_text_pitch)
        self.ui.checkBoxSpeechLoudness.setChecked(config.device_cfg.speech_text_loudness)
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
        config.device_cfg.sound_text_loudness = self.ui.checkBoxSoundLoudness.isChecked()

        config.device_cfg.speech_text_kind = self.ui.checkBoxSpeechKind.isChecked()
        config.device_cfg.speech_text_stream = self.ui.checkBoxSpeechStream.isChecked()
        config.device_cfg.speech_text_pitch = self.ui.checkBoxSpeechPitch.isChecked()
        config.device_cfg.speech_text_loudness = self.ui.checkBoxSpeechLoudness.isChecked()
        config.device_cfg.speech_text_content = self.ui.checkBoxSpeechContent.isChecked()
        config.device_cfg.speech_text_speaker = self.ui.checkBoxSpeechSpeaker.isChecked()
        config.device_cfg.speech_text_gender = self.ui.checkBoxSpeechGender.isChecked()

        self.close()
