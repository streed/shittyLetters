#!/usr/bin/perl
use strict;
use warnings;

sub ayfkm #are you fucking kidding me? functions are this easy?
{
  my $werd;
  my @werds = @_;
  $werd = int(rand(scalar(@werds)));
  chomp @werds;
  return $werds[$werd];
}

my $sloop = 1;
my $input;

open(my $adj, "<", "adj.txt") or die "The file didn't open. Suck a dick!";  
open(my $ing, "<", "ing.txt") or die "The file didn't open. Suck a dick!";
open(my $noun, "<", "noun.txt") or die "The file didn't open. Suck a dick!";
open(my $suf, "<", "suf.txt") or die "The file didn't open. Suck a dick!";

my @p1 = <$adj>;
my @p2 = <$ing>;
my @p3 = <$noun>;
my @p4 = <$suf>;

close($adj);  
close($ing);
close($noun);
close($suf);

while ($sloop)
{
  print "\nYou are one " . &ayfkm(@p1) . " " . &ayfkm(@p2) . " " . 
    &ayfkm(@p3) . &ayfkm(@p4) . ". \n \n";

  print "You want more? (Y/N): ";
  $input = <STDIN>;
  chomp $input;
  
  if ($input eq "Y" || $input eq "y")
  {
    print "\n";
  }
  elsif ($input eq "N" || $input eq "n")
  {
    undef $sloop;
  }
  else
  {
    print "Shit, you can't even type 'Y' or 'N'?\n";
  }
}

print "Smell ya later!\n";