import csv
import io
import logging

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

WHAZZUP_CACHE_KEY = "slurper:whazzup"
DEFAULT_WHAZZUP_URL = "https://fsddata.skylitefly.com/whazzup.json"
DEFAULT_WHAZZUP_TIMEOUT_SECONDS = 5
DEFAULT_WHAZZUP_CACHE_SECONDS = 5


def _setting(name, default):
    return getattr(settings, name, default)


def _fetch_whazzup():
    cached = cache.get(WHAZZUP_CACHE_KEY)
    if cached is not None:
        return cached

    url = _setting("SLURPER_WHAZZUP_URL", DEFAULT_WHAZZUP_URL)
    timeout = _setting("SLURPER_WHAZZUP_TIMEOUT_SECONDS", DEFAULT_WHAZZUP_TIMEOUT_SECONDS)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("whazzup response must be a JSON object")

    cache_timeout = _setting("SLURPER_WHAZZUP_CACHE_SECONDS", DEFAULT_WHAZZUP_CACHE_SECONDS)
    cache.set(WHAZZUP_CACHE_KEY, data, cache_timeout)
    return data


def _format_frequency(value):
    if value in (None, ""):
        return "199.998"
    return str(value)


def _format_coordinate(value):
    try:
        return str(float(value))
    except (TypeError, ValueError):
        return "0.0"


def _format_slurper_detail(value):
    if value in (None, ""):
        return "0"
    return str(value)


def _slurper_line(*, cid, callsign, connection_type, frequency, detail, latitude, longitude):
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="")
    writer.writerow(
        [
            str(cid or ""),
            str(callsign or ""),
            str(connection_type or ""),
            _format_frequency(frequency),
            _format_slurper_detail(detail),
            _format_coordinate(latitude),
            _format_coordinate(longitude),
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "",
        ]
    )
    return output.getvalue()


def _whazzup_list(whazzup, key):
    value = whazzup.get(key, [])
    return value if isinstance(value, list) else []


def _controller_lines(whazzup, cid):
    lines = []
    for controller in _whazzup_list(whazzup, "controllers"):
        if not isinstance(controller, dict):
            continue
        if str(controller.get("cid", "")) != cid:
            continue

        callsign = controller.get("callsign", "")
        if not callsign:
            continue

        lines.append(
            _slurper_line(
                cid=controller.get("cid", ""),
                callsign=callsign,
                connection_type="atc",
                frequency=controller.get("frequency", ""),
                detail=controller.get("facility", controller.get("rating", "")),
                latitude=controller.get("latitude", 0),
                longitude=controller.get("longitude", 0),
            )
        )
    return lines


def _pilot_lines(whazzup, cid):
    lines = []
    for pilot in _whazzup_list(whazzup, "pilot"):
        if not isinstance(pilot, dict):
            continue
        if str(pilot.get("cid", "")) != cid:
            continue

        callsign = pilot.get("callsign", "")
        if not callsign:
            continue

        lines.append(
            _slurper_line(
                cid=pilot.get("cid", ""),
                callsign=callsign,
                connection_type="pilot",
                frequency="pilot",
                detail=pilot.get("rating", ""),
                latitude=pilot.get("latitude", 0),
                longitude=pilot.get("longitude", 0),
            )
        )
    return lines


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


@require_GET
def users_info(request):
    cid = request.GET.get("cid", "").strip()
    if not cid:
        return HttpResponse("", content_type="text/plain; charset=utf-8")

    try:
        whazzup = _fetch_whazzup()
    except requests.RequestException:
        logger.exception("Failed to fetch whazzup data for slurper cid=%s", cid)
        return HttpResponse("Unable to fetch network data", status=502, content_type="text/plain")
    except ValueError:
        logger.exception("Invalid whazzup JSON for slurper cid=%s", cid)
        return HttpResponse("Invalid network data", status=502, content_type="text/plain")

    lines = _controller_lines(whazzup, cid) + _pilot_lines(whazzup, cid)
    if not lines:
        return HttpResponse("\n", content_type="text/plain; charset=utf-8")

    body = "\n".join(lines)
    return HttpResponse(f"{body}\n", content_type="text/plain; charset=utf-8")
