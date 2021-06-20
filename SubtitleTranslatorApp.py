from __future__ import annotations

import os
import re
from os.path import exists
from shutil import copy
from typing import Tuple

import webvtt
from googletrans import Translator


class SubtitleTranslator:

    def __init__(self, file_address: str, method: int = 0):
        """
        :param file_address: the path of vtt file
        """

        self.file_address = file_address
        self.translator = Translator(service_urls=['translate.googleapis.com'])

    def maker(self) -> None:
        self._backup_old_file()
        untranslated_file = self.open_untranslated_file()
        moments, untranslated_context = self._splitter(untranslated_file)
        translated_context = self._translate(''.join(untranslated_context))
        translated_file = self._joiner(translated_context, moments)
        self._make_output_file(translated_file)

    def open_untranslated_file(self) -> str:
        with open(self.file_address, 'r', encoding='utf-8') as file:
            untranslated_file = file.read()
        return untranslated_file

    @staticmethod
    def _splitter(untranslated_file: str) -> Tuple[list, list]:
        moments = re.findall(r'\d{,2}:\d{,2}:\d{,2}\.\d{,3}\s-->\s\d{,2}:\d{,2}:\d{,2}\.\d{,3}\n',
                             untranslated_file)  # regex result like: '00:08:53.955 --> 00:08:57.420'
        context = re.split(r'\n\d+\n\d{,2}:\d{,2}:\d{,2}\.\d{,3}\s-->\s\d{,2}:\d{,2}:\d{,2}\.\d{,3}\n',
                           untranslated_file)  # regex result like: '\n118\n00:08:53.955 --> 00:08:57.420'
        return moments, context[1:]  # context[0]=='WEBVTT\n'

    @staticmethod
    def _joiner(translated_context: str, moments: list) -> str:
        listed_translated_file = translated_context.split('\n')
        result = [None] * (len(listed_translated_file) + (len(moments) * 2))
        result[::3] = [str(i + 1) + '\n' for i in range(len(moments))]
        result[1::3] = moments
        result[2::3] = [i + '\n\n' for i in listed_translated_file]
        # for index, moment in enumerate(moments):
        #     result += f'{index}\n{moment}\n{listed_translated_file[index]}\n\n'
        return 'WEBVTT\n\n' + ''.join(map(str, result))

    def _translate(self, to_translation: str) -> str:
        translated = self.translator.translate(to_translation, dest='fa')
        return translated.text

    def _backup_old_file(self) -> None:
        if not exists(f'{self.file_address}.bak'):
            copy(f'{self.file_address}', f'{self.file_address}.bak')

    def _make_output_file(self, translated) -> None:
        with open(f'{self.file_address}', 'w+', encoding='utf-8') as f:
            f.writelines(translated)


if __name__ == '__main__':
    user_path_choice = input('get vtt file path or None for all...')
    if user_path_choice and user_path_choice[0] == user_path_choice[-1] == '"':
        user_path_choice = user_path_choice[1:-1]
    if not user_path_choice:
        for top, dirs, nondirs in os.walk(os.path.abspath('')):
            for item in nondirs:
                if item.endswith('.vtt'):
                    sb = SubtitleTranslator(item)
                    sb.maker()
                    vtt = webvtt.read(os.path.join(top, item))
                    vtt.save_as_srt()
    if exists(user_path_choice):
        if user_path_choice.endswith('.vtt'):
            sb = SubtitleTranslator(user_path_choice)
            sb.maker()
            vtt = webvtt.read(user_path_choice)
            vtt.save_as_srt()
