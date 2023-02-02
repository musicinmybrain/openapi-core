from base64 import b64decode
from os import path
from urllib import request

import pytest
from openapi_spec_validator.readers import read_from_filename
from yaml import safe_load

from openapi_core.spec import Spec


def content_from_file(spec_file):
    directory = path.abspath(path.dirname(__file__))
    path_full = path.join(directory, spec_file)
    return read_from_filename(path_full)


def spec_from_file(spec_file):
    spec_dict, spec_url = content_from_file(spec_file)
    return Spec.from_dict(spec_dict, spec_url=spec_url)


def spec_from_url(spec_url):
    content = request.urlopen(spec_url)
    spec_dict = safe_load(content)
    return Spec.from_dict(spec_dict, spec_url=spec_url)


@pytest.fixture(scope="session")
def data_gif():
    return b64decode(
        """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
    )


class Factory(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


@pytest.fixture(scope="session")
def factory():
    return Factory(
        content_from_file=content_from_file,
        spec_from_file=spec_from_file,
        spec_from_url=spec_from_url,
    )
