import os
from datetime import datetime
from scamper import ScamperFile, ScamperInst, ScamperTrace, ScamperTraceHop, ScamperPing
from errors import unimplemented_error, parse_error

STD_TIME_FORMAT = "%H:%M:%S.%f"
STD_ZERO_TIME = datetime.strptime("00:00:00.000000", STD_TIME_FORMAT)

class WartsDumpParser:

    def __init__(self, path: str, filename: str) -> None:
        
        res, msg = self._parse_path(os.path.join(path, filename))
        if not res:
            parse_error("scmperfile", f"received exception [{msg}]")
    
    # inner parser functions
    def _parse_inst(self, obj: ScamperInst) -> dict[str, any]:
        '''
        scamper.ScamperInst
        used attributes:
            name: a string that identifies the instance in some way.
            shortname: a shortened string that identifies the instance in some way, if available.
            ipv4: a string containing the IPv4 address of the VP, if available.
            asn4: an integer containing the IPv4 ASN address of the VP, if available.
            cc: an upper-case string containing the country location of the VP, if available.
            st: an upper-case string containing the state location of the VP, if available. 
            place: a string containing the place name of the VP, if available.
        '''
        # TODO: currently unused because seem to be set to null for a lot of measurements
        try:
            name, ipv4 = obj.name, str(obj.ipv4)
            asn4 = obj.asn4
            cc, st, place = obj.cc, obj.st, obj.place
            return {"name": name, "ipv4": ipv4, "asn4": asn4, 
                    "loc-spec": f"{place if place else ''}, {st if st else ''}, {cc if cc else ''}"}
        except Exception as e:
            parse_error("scamperinst", f"received exception [{str(e)}]")
    
    def _parse_hop(self, obj: ScamperTraceHop) -> dict[str, any]:
        '''
        class scamper.ScamperTraceHop
        used attributes:
            src: a ScamperAddr containing the IP address that replied to a probe.
            name: a string containing the name in a DNS PTR record that was looked up, if scamper attempted to resolve a PTR for the IP address.
            tx: a datetime for when the probe was sent, or None if scamper did not record a timestamp.  
            rtt: a timedelta containing the round-trip-time for this response.
            probe_ttl: the TTL set in the probe packet
        '''
        try:
            src, name = str(obj.src), obj.name
            rtt = obj.rtt
            probe_ttl = obj.probe_ttl
            rtt = rtt.total_seconds() * 1000
            return {"src": src, "name": name, "rtt": rtt, 'probe-ttl': probe_ttl}
        except Exception as e:
            parse_error("scamperhop", f"received exception [{str(e)}]")
    
    def _parse_trace(self, obj : ScamperTrace) -> dict[str, any]:
        ''' 
        class scamper.ScamperTrace
        used attributes:
            start: the datetime when this measurement started.
            src: a ScamperAddr containing the source address used in this measurement.
            dst: a ScamperAddr containing the destination address used in this measurement.
            stop_hop: the index of the hop that would have caused scamper to stop probing.
            hops(): returns an iterator that provides the first response scamper obtained for each hop, as a ScamperTraceHop.
            addrs(reserved=True): return a list of unique addresses in the path up to stop_hop.
            stop_reason_str: returns a lower-case string that records why the traceroute stopped.
        '''
        try:
            start_ts = str(obj.start)
            src, dst = str(obj.src), str(obj.dst)
            stop_reason = obj.stop_reason_str

            stop_hop = obj.stop_hop
            hop_metas = []
            for hop in obj.hops():
                if isinstance(hop, ScamperTraceHop):
                    hop_metas.append(self._parse_hop(hop))
            
            return {
                'start-ts': start_ts, 'src-ip' : src, 'dst-ip' : dst,
                'stop-hop': stop_hop, 'hop-metas': hop_metas, 'stop-reason': stop_reason 
            }
            
        except Exception as e:
            parse_error("scampertrace", f"received exception [{str(e)}]")
    def _parse_ping(self, obj : ScamperPing) -> dict[str, any]:
        '''
        class scamper.ScamperPing
        used attributes: 
             start: the datetime when this measurement started.
             src: a ScamperAddr containing the source address used in this measurement.
             dst: a ScamperAddr containing the destination address used in this measurement.
             nreplies: the number of probes for which scamper received at least one reply
             ndups: the number of additional replies that scamper received from the destination.
             nloss: the number of probes for which scamper did not receive any reply.
             nerrs: the number of response packets that were not from the destination.
             min_rtt: the minimum RTT observed in responses
             max_rtt: the maximum RTT observed in responses
             avg_rtt: the average RTT observed in responses
             stddev_rtt: the standard deviation for the RTTs observed in responses
        '''
        try:
            start_ts = str(obj.start)
            src, dst = str(obj.src), str(obj.dst)

            num_replies, num_dups, num_loss, num_errors = obj.nreplies, obj.ndups, obj.nloss, obj.nerrs
            min_rtt, max_rtt = str(obj.min_rtt), str(obj.max_rtt)
            avg_rtt, stddev_rtt = str(obj.avg_rtt), str(obj.stddev_rtt)
            return {'start-ts': start_ts,'src-ip': src, 'dst-ip': dst,
                    'num-rep': num_replies, 'num-dup': num_dups, 'num-los': num_loss, 'num_err': num_errors,
                    'avg-rtt': avg_rtt, 'sdv-rtt': stddev_rtt, 'min-rtt': min_rtt, 'max-rtt': max_rtt}
        except Exception as e:
            parse_error("scamperping", f"received exception[{str(e)}]")

    def _parse_path(self, path: str) -> tuple[bool, str]:
        try:
            assert os.path.exists(path)
            self.inf = ScamperFile(path)
        except Exception as e:
            return False, str(e)
        
        return True, ""
    
    def _parse_file(self, item_parse: str, num_vis : int = None):
        # TODO: add more if needed
        trace_flag = item_parse == 'trace'
        ping_flag = item_parse == 'ping'

        counter = 0
        data = []
        for obj in self.inf:
            if trace_flag and isinstance(obj, ScamperTrace):
                data.append(self._parse_trace(obj))
                counter += 1
            if ping_flag and isinstance(obj, ScamperPing):
                data.append(self._parse_ping(obj))
                counter += 1

            if num_vis and counter >= num_vis:
                break

        return data
        
    # outer getter functions
    def get_data(self, spec : str = 'trace'): # defaults to traceroute 
        return self._parse_file(spec)

    def demo_data(self, spec: str = 'trace', num_vis : int = 5):
        ret = self._parse_file(spec, num_vis = num_vis)
        for inst in ret:
            print(inst)

