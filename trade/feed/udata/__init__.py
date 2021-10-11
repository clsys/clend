import importlib_metadata

from .udata_datafeed import UdataDatafeed as Datafeed


try:
    __version__ = importlib_metadata.version("feed.udata")
except importlib_metadata.PackageNotFoundError:
    __version__ = "dev"
