# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Log formatter."""

import logging

from colors import ansilen


class CustomLogFormatter(logging.Formatter):
    """Custom formatter to ensure proper indentation."""

    def __init__(self, prev_formatter: logging.Formatter) -> None:
        """
        Init.

        :param prev_formatter: Formatter, which will be overwritten.
                               We will use this object, so basically we're making more like a wrapper here.
        """
        super().__init__()
        self._prev_formatter = prev_formatter

    def formatMessage(self, record: logging.LogRecord) -> str:
        """
        Format and return log record.

        We assume that this formatter is used only with our predefined log format or similar prefix format,
        which uses fields like asctime, name, functime, levelname, but doesn't include msg/message.
        That's why this formatter will format prefix of log record with previous formatter
        and after that it will add msg with indentations.

        :param record: Log record.
        :return: Formatted message.
        """
        message = record.getMessage()
        # check if separator
        if len(set(message)) == 1:
            return message

        # check if explicitly marked as separator
        if record.__dict__.get("is_separator", False):
            return message

        # this module only logs messages from this module, no need to keep prefix
        record.name = record.name.replace("mfd-code-quality.", "")

        formatted_prefix = self._prev_formatter.format(record)
        return self.get_prepared_message(formatted_prefix, message)

    @staticmethod
    def get_prepared_message(formatted_prefix: str, message: str) -> str:
        """
        Extend message with proper indentations and return joined str with formatted prefix.

        :param formatted_prefix: Already formatted log's prefix with fields like asctime, ...
        :param message: Message, which will be extended with spaces to create column-like aligned text.
        :return: Joined formatted prefix and extended message.
        """
        indent_length = ansilen(formatted_prefix) + 1  # + 1 because of additional space before message
        msg_lines = message.splitlines(True)
        message = ""
        if msg_lines:
            message = "".join([msg_lines[0], *(f"{indent_length * ' '}{line}" for line in msg_lines[1:])])
        return f"{formatted_prefix} {message}"
