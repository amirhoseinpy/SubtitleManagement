from __future__ import annotations

import os
import re
from os.path import exists
from shutil import copy

import webvtt
from googletrans import Translator


class SubtitleTranslator:

    def __init__(self, file_address: str, method: int = 0):
        """
        :param file_address: the path of vtt file
        :param method: full_translate_method -> 0, line_by_line_method -> 1
        """

        self.file_address = file_address
        self.translator = Translator(service_urls=['translate.googleapis.com'])
        if method == 0:
            self.backup_old_file()
            self.make_output_file(self.full_translate_method())
        if method == 1:
            print('This method had not written')

    def open_untranslated_file(self) -> list:
        with open(self.file_address, 'r', encoding='utf-8') as file:
            untranslated_file = file.readlines()
            untranslated_file.append('\n')
        return untranslated_file

    @staticmethod
    def get_full_translatable_file(untranslatable_regex, untranslated_file) -> str:
        merge_indexes = []
        i, j = 0, 0
        for index, line in enumerate(untranslated_file):
            if re.match(untranslatable_regex, line):
                if i and j:
                    merge_indexes.append((i, j + 1))
                i, j = 0, 0
                continue
            untranslated_file[index] = untranslated_file[index].lstrip()
            if not i:
                i = index
            else:
                j = index

        for i, j in merge_indexes[::-1]:
            untranslated_file[i:j] = [''.join(untranslated_file[i:j])]
            untranslated_file[i] = untranslated_file[i].replace('\n', ' ') + '\n'

        return ''.join(untranslated_file)

    @staticmethod
    def get_line_by_line_translatable_file() -> str:
        pass

    def translate(self, to_translation: str) -> list:
        translated = self.translator.translate(to_translation, dest='fa')
        return translated.text.split('\n')

    def full_translate_method(self) -> list:
        untranslated_file = self.open_untranslated_file()
        untranslatable_regex = r'WEBVTT\n|^\n|^\d+\n|^\d{,2}:\d{,2}:\d{,2}\.\d{,3}\s-->\s\d{,2}:\d{,2}:\d{,2}\.\d{,3}\n'
        translated = self.translate(self.get_full_translatable_file(untranslatable_regex, untranslated_file))

        bad_format_translated_regex = r'^\d{,2}:\s*\d{,2}:\s*\d{,2}\.\d{,3}\s-+>\s\d{,2}:\s*\d{,2}:\s*\d{,2}\.\d{,3}'
        for index, line in enumerate(translated):
            if re.match(bad_format_translated_regex, line):
                line = line[:3] + line[4:7] + line[8:16] + '-' + line[16:21] + line[22:25] + line[26:]
            translated[index] = line + '\n'

        return translated

    def line_by_line_method(self) -> list:
        pass

    def backup_old_file(self) -> None:
        if not exists(f'{self.file_address}.bak'):
            copy(f'{self.file_address}', f'{self.file_address}.bak')

    def make_output_file(self, translated) -> None:
        with open(f'{self.file_address}', 'w+', encoding='utf-8') as f:
            f.writelines(translated)


if __name__ == '__main__':
    for top, dirs, nondirs in os.walk(os.path.dirname(os.path.abspath(__file__))):
        for item in nondirs:
            if item.endswith('.vtt'):
                sb = SubtitleTranslator(item)
                vtt = webvtt.read(os.path.join(top, item))
                vtt.save_as_srt()
