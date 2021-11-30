"""
Custom output formatter for the RIPE ripe-atlas tools result view.

Drop into ~/.config/ripe-atlas-tools/renderers where the ripe-atlas command line utility
can pick it up.
"""
from ripe.atlas.tools.renderers.base import Renderer as BaseRenderer

class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_TRACEROUTE]

    def __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)
        self.output_format = '\t'.join(["%s"]*7) + "\n"

    def on_result(self, result):

        #if result.is_error or result.is_malformed or len(result.ip_path) <= 1:
        #    return None

        hop_ip_list = []
        for hop_list in result.ip_path:
            hop_ip = "*"
            for hop in hop_list:
                if hop != None:
                    hop_ip = hop
                    break

            hop_ip_list.append(hop_ip)

        hop_ips_delimited = ",".join(hop_ip_list)
        datetime = result.end_time.strftime("%Y/%m/%d %H:%M:%S")

        return self.output_format % (result.probe_id, datetime, result.origin, result.source_address, \
                                     result.destination_name, result.destination_address, hop_ips_delimited)