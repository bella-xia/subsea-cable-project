This is intended as a brainstorming documentation for the project


1. Prior Works

The existing studies have focused extensively on subsea cable inference methods,
meaning that each research would have adopted a set of primary assumptions,
and attempt to iteratively select information most closely aligned with the assumptions

----- TODO: organize an overview on different assumption set -----


2. Problem

One prevalent challenges across all works seem to be the awareness that
the submarine cable information remains the most occluded resources among 
available internet data, suffering from problems

    a. there is no guarantee that the cable ownership woule align with the ASN
    of each cable, as cables can be leased to other ISPS. Additionally, current
    ecosystem of cable ownership seem to be divided between traditional cable
    ISPs and large cloud providers

    b. the landing station is not guaranteed to be close to the IP address due 
    to the deployment of [TODO: find the protocol name]. As noted by [TODO: cite
    the paper], when they use a set of assumptions not including geographical
    proximity to infer on cable topography, they observed that the general distance
    of their inferred cable IP address is geolocated [TODO: check the numerical value]
    far from the landing stations

    c. even if the the actual interface is close to the landing station, internet
    geolocation data are popularly known to be inaccurate, especially when focusing
    on city-level and latitide-altitude numerics (which the inference would need to 
    do the calculate the distance from landing point). Most existing studies uses 
    MaxMind geolocation data as the source, and do not offer ablation study on
    alternative possibilities of geolocation resources. [TODO: cite the paper], on
    the other hand, use as many as 11 geolocation resources.

    However, the authors admitted that 

        i). they took equal weighing across all data sources regardless of 
        their creidibility and observed accuracy

        ii). even though aware that some geolocation sources are themselves an
        aggregation of other resources, the author do not attempt to further address
        the dependency
    
    d. the cable dataset is aggregated based on available disclosures by large 
    corporations, who tend to prefer to keep the system black box. This means there
    is no way to validate on the available cable dataset. And there seem to be
    relatively little attempt to perform ablation studies on various sources of
    available cable dataset.

3. Proposal

The current project intends to start with pattern-finding on the existing large
scale CAIDA ARK traceroute dataset. Instead of organizing an overarching view of
subsea cables, it intends to only include submarine cable information (landing
station, cable ownership, etc.) at the end.

Specifically, it intends to query upon a specific subsea cable phenomenon: cable 
breakages. When a cable breakage occurs, the IP addresses associated with the cables
would become unreachable and consequently disappear from the traceroute probes. Backup
cables may be deployed leading to the sudden emergences of new IP addresses, or the 
traceroute would fail any attempt to probe the inter-continental location suffering
from cable breakage. Both occurences may be observable simply from the traceroute data.

Admittedly, the study design is still subject to a number of assumptions about the 
subsea cable system

    a. if multiple parallel cables are anycasted and share the same IP address, the
    breakage may not be observable. However, existing studies also rely heavily on
    IP-to-cable mapping, which seem the suggest there is a consensus that cables are
    not anycasted currently?

    b. to target intercontinental probe and their characteristics require geolocation
    data on the country-level. Even though [TODO: cite the paper] confirms that 
    country-level geolocation accuracy can be as high as [TODO: get the numerics], and
    ASN can always serve as a partial validation for country-level geolocation, there 
    are still risks and inaccuracies inherently associated with relying on geolocation
    for experiment design.


3. Methodology
    
    a. Exploratory study

    The exploratory study takes CAIDA ARK's traceroute probes from a single VP (Kenya).
    The range of probes are limited by existing data. Currently the project uses a set
    of disjoint durations including Jan 30 - Feb 19, 2024, and Aug 28 - Sep 2, 2024. 

    Nevertheless, these sets of dates correspond with a significant cable breakage
    event. At the end of Februrary, 2024, the Red Sea cable system experiences multiple
    disruptions, leading to lost or significantly delayed traffic between Europe, Africa,
    and Asia [TODO: cite the news]. This period is the focus of the current exploratory
    study.
