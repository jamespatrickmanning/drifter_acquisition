#!/usr/local/bin/perl
use SOAP::Lite;

use IO::Handle;
open (OUTPUT, ">>/home/user/drift/raw2022.dat") || die $!;
STDOUT->fdopen(\*OUTPUT, "w") || die $!;
#   -> service("https://assetview.comtechmobile.com/sensserve/pickup_depot.wsdl")

print "Connecting to SENS Pickup-Depot Service...\n";
print SOAP::Lite
   -> service("https://assetviewservice.tms-orbcomm.com/sensserve/pickup_depot.wsdl")
   -> get_Packet("69a9bf33096fad0e8900a371b1171027","decoded");
#   -> get_Packet("fadf99172476c288c53eaedcb7fd9f60","decoded");
#print "finished getfix.plx code"
