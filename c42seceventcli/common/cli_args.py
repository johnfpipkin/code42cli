from argparse import SUPPRESS
from datetime import datetime, timedelta


def add_authority_host_address_arg(arg_group):
    arg_group.add_argument(
        "-s",
        "--server",
        dest="c42_authority_url",
        action="store",
        help="The full scheme, url and port of the Code42 server.",
    )


def add_username_arg(arg_group):
    arg_group.add_argument(
        "-u",
        "--username",
        action="store",
        dest="c42_username",
        help="The username of the Code42 API user.",
    )


def add_config_file_arg(arg_group):
    arg_group.add_argument(
        "-c",
        "--config",
        action="store",
        dest="c42_config_file",
        help="Path to a .cfg file containing a username and Code42 authority host address."
    )


def add_help_arg(arg_group):
    arg_group.add_argument(
        "-h", "--help", action="help", default=SUPPRESS, help="Show this help message and exit"
    )


def add_begin_timestamp_arg(arg_group):
    default_begin_date = datetime.now() - timedelta(days=60)
    default_begin_date_str = default_begin_date.strftime("%Y-%m-%d")
    arg_group.add_argument(
        "-b",
        "--begin",
        action="store",
        dest="c42_begin_date",
        default=default_begin_date_str,
        help="The end of the date range in which to look for events, "
        "in YYYY-MM-DD format OR a number (number of minutes ago).",
    )


def add_end_timestamp_arg(arg_group):
    default_end_date = datetime.now()
    default_end_date_str = default_end_date.strftime("%Y-%m-%d")
    arg_group.add_argument(
        "-e",
        "--end",
        action="store",
        dest="c42_end_date",
        default=default_end_date_str,
        help="The beginning of the date range in which to look for events, "
        "in YYYY-MM-DD format OR a number (number of minutes ago).",
    )


def add_ignore_ssl_errors_arg(arg_group):
    arg_group.add_argument(
        "-i",
        "--ignore-ssl-errors",
        action="store_true",
        dest="c42_ignore_ssl_errors",
        default=False,
        help="Set to ignore ssl errors.",
    )


def add_output_format_arg(arg_group):
    arg_group.add_argument(
        "-o",
        "--output-format",
        dest="c42_output_format",
        action="store",
        default="JSON",
        choices=["CEF", "JSON"],
        help="The format used for outputting events."
    )


def add_record_cursor_arg(arg_group):
    arg_group.add_argument(
        "-r",
        "--record-cursor",
        dest="c42_record_cursor",
        action="store_true",
        default=False,
        help="Used to only get new events on subsequent runs."
    )


def add_event_type_args(arg_group):
    arg_group.add_argument(
        "-t",
        "--types",
        nargs="*",
        action="store",
        dest="c42_event_types",
        choices=[u"created", u"modified", u"deleted", u"read_by_app"],
        help="The types of events to extract."
    )


def add_debug_arg(arg_group):
    arg_group.add_argument(
        "-d"
        "--debug",
        action="store_true",
        dest="c42_debug_mode",
        help="Set to turn on debug logging."
    )
