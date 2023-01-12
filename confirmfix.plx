#!/usr/local/bin/perl
use SOAP::Lite;

use IO::Handle;
open (OUTPUT, ">>/home/user/drift/confirmed2022.dat") || die $!;
STDOUT->fdopen(\*OUTPUT, "w") || die $!;

print "Connecting to SENS Pickup-Depot Service...\n";
print SOAP::Lite
   -> service("https://assetview.tms-orbcomm.com/sensserve/pickup_depot.wsdl")
   -> confirm_Packet("69a9bf33096fad0e8900a371b1171027","$ARGV[0]");
   #fadf99172476c288c53eaedcb7fd9f60","$ARGV[0]");
